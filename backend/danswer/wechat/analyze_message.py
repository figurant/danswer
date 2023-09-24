import time
import re
import time
import uuid
from datetime import datetime
from datetime import timezone

from sqlalchemy.orm import Session

from danswer.configs.app_configs import INDEX_BATCH_SIZE
from danswer.configs.constants import DocumentSource
from danswer.configs.model_configs import MAX_WECHAT_MESSAGE_LENGTH, MAX_WECHAT_CONTEXT
from danswer.connectors.interfaces import GenerateDocumentsOutput
from danswer.connectors.models import Document, Section
from danswer.connectors.models import IndexAttemptMetadata
from danswer.datastores.indexing_pipeline import build_indexing_pipeline
from danswer.db.connector_credential_pair import update_connector_credential_pair
from danswer.db.dwd_wx_dialog import get_dwd_wx_dialog_all
from danswer.db.index_attempt import mark_attempt_failed
from danswer.db.index_attempt import mark_attempt_succeeded
from danswer.db.index_attempt import update_docs_indexed
from danswer.db.models import IndexAttempt
from danswer.db.models import IndexingStatus
from danswer.db.models import OdsWxMsg
from danswer.db.ods_wx_msg import create_wx_msg, get_wx_msg
from danswer.utils.logger import setup_logger
from danswer.wechat.dialog import Dialog, Message
from danswer.wechat.prompts import get_ana_wx_prompt, MESSAGE_TYPE_EXPERT_ANSWER
from danswer.wechat.wechat_openai import get_completion, get_completion_mock

logger = setup_logger()


def preprocess_msgs(
    db_session: Session, attempt: IndexAttempt
) -> list[OdsWxMsg]:
    def _one_msg(
            db_session: Session, sender: str, send_time: str, content: str, meta_info: str
    ) -> OdsWxMsg:
        wx_msg = None
        if len(sender) != 0 and len(send_time) != 0 and len(content) != 0:
            wx_msg = create_wx_msg(sender, send_time, content, meta_info, db_session)
        return wx_msg

    with open(attempt.connector.connector_specific_config['file_locations'][0], 'r', encoding='utf-8') as file:
        lines = file.readlines()

    msgs = []
    sender = ""
    send_time = ""
    content = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match_obj = re.match(r'(.*) (\d{4}/\d{2}/\d{2} \d{2}:\d{2})', line)
        if match_obj:
            current_msg = _one_msg(db_session, sender, send_time, content,
                                   attempt.connector.connector_specific_config['file_locations'][0])
            if current_msg:
                msgs.append(current_msg)

            sender = match_obj.group(1)
            send_time = match_obj.group(2)
            content = ""
        else:
            if len(content) > 0:
                content += f"，{line}"
            else:
                content = line
            content = content.replace("\n", "")
            content = content.replace("|", ",")

    current_msg = _one_msg(db_session, sender, send_time, content,
                           attempt.connector.connector_specific_config['file_locations'][0])
    if current_msg:
        msgs.append(current_msg)

    return msgs


def load_from_dialogs(
    attempt: IndexAttempt,
    dialogs: Dialog
) -> GenerateDocumentsOutput:
    documents: list[Document] = []
    file_name = attempt.connector.connector_specific_config['file_locations'][0]
    for d in dialogs:
        # todo section第一个参数可优化
        sections = [Section(link=str(d.uuid), text=d.get_qa_block())]
        documents.append(Document(
            id=file_name,
            sections=sections,
            source=DocumentSource.FILE,
            semantic_identifier=file_name,
            metadata={},
        ))
        if len(documents) >= INDEX_BATCH_SIZE:
            yield documents
            documents = []
    if documents:
        yield documents


def get_dialogs_mock(
        db_session: Session
) -> list[Dialog]:
    dwd_wx_dialogs = get_dwd_wx_dialog_all(db_session)
    dlgs_map = {}  # uuid->dialog的map
    for dwd_wx_dialog in dwd_wx_dialogs:
        dlg_uuid = str(dwd_wx_dialog.dialog_uuid)
        ods_wx_msg = get_wx_msg(dwd_wx_dialog.msg_id, db_session)
        message = Message(dwd_wx_dialog.msg_id,
                          ods_wx_msg.sender_name,
                          ods_wx_msg.send_time,
                          ods_wx_msg.msg_content,
                          dwd_wx_dialog.msg_type
                          )
        if dlg_uuid in dlgs_map:
            dlgs_map[dlg_uuid].add_message(message)
        else:
            dlg = Dialog(dlg_uuid, [message])
            dlgs_map[dlg_uuid] = dlg

    valid_dlgs = []
    for d in list(dlgs_map.values()):
        for m in d.messages:
            if int(m.type) == MESSAGE_TYPE_EXPERT_ANSWER:
                valid_dlgs.append(d)
                break

    return valid_dlgs



def get_dialogs(
        db_session: Session, msgs: list[OdsWxMsg]
) -> list[Dialog]:
    def _exract_dialogs(raw_dialogs_txt: str, db_session: Session) -> (list[Dialog], list[Dialog]):
        pending_dlgs = []  # 有提问，待回答的对话消息，需要进行下一轮处理
        valid_dlgs = []
        dlgs_map = {}  # id->dialog的map
        for line in raw_dialogs_txt.splitlines():
            match_obj = re.match(r'(\d+)\|(\d+)\|(\d+)', line)
            if match_obj:
                msg_id = int(match_obj.group(1).strip())
                msg_type = int(match_obj.group(2).strip())
                dialog_id = int(match_obj.group(3).strip())
                if msg_id > 0 and 0 < msg_type < 5 and dialog_id > 0:
                    ods_wx_msg = get_wx_msg(msg_id, db_session)
                    message = Message(msg_id,
                                      ods_wx_msg.sender_name,
                                      ods_wx_msg.send_time,
                                      ods_wx_msg.msg_content,
                                      msg_type
                                      )
                    if dialog_id in dlgs_map:
                        dlgs_map[dialog_id].add_message(message)
                        if msg_type == MESSAGE_TYPE_EXPERT_ANSWER:
                            dlgs_map[dialog_id].set_has_answer()
                    else:
                        dialog = Dialog(uuid.uuid1(), [message])
                        dlgs_map[dialog_id] = dialog
        for d in dlgs_map.values():
            if d.has_answer:
                valid_dlgs.append(d)
                d.commit_dwd_wx_dialog(db_session)
            else:
                pending_dlgs.append(d)

        return valid_dlgs, pending_dlgs

    dialogs = []
    msgs_txt = ""
    finished = True
    for msg in msgs:
        msg_txt = msg.get_msg_txt()
        if len(msg_txt) > MAX_WECHAT_MESSAGE_LENGTH:
            logger.warning(
                f"wechat message exceed max length {len(msg_txt)} > {MAX_WECHAT_MESSAGE_LENGTH}:{msg_txt}")
            continue
        # msgs取len=MAX_WECHAT_CONTEXT进行处理，处理完加上剩下的组成新的MAX_WECHAT_CONTEXT长度。
        if len(msgs_txt) + len(msg_txt) < MAX_WECHAT_CONTEXT:
            msgs_txt += f"{msg_txt}\n"
            finished = False
        else:
            finished = True
            dialogs_txt = get_completion(get_ana_wx_prompt(msgs_txt), "gpt-3.5-turbo")
            valid_dlgs, pending_dlgs = _exract_dialogs(dialogs_txt, db_session)
            dialogs += valid_dlgs
            msgs_txt = ""
            for d in pending_dlgs:
                for m in d.messages:
                    msgs_txt += f"{m.get_msg_txt()}\n"
            if len(msgs_txt) > MAX_WECHAT_CONTEXT/2:
                logger.warning(
                    f"pending wechat messages exceed max length {len(msgs_txt)} > {MAX_WECHAT_CONTEXT}/2:{msgs_txt}")
                break
    if not finished:
        dialogs_txt = get_completion(get_ana_wx_prompt(msgs_txt), "gpt-3.5-turbo")
        valid_dlgs, pending_dlgs = _exract_dialogs(dialogs_txt, db_session)
        dialogs += valid_dlgs
        for d in pending_dlgs:
            logger.info(f"this is a pending dialog {d.uuid}")
            d.commit_dwd_wx_dialog(db_session)

    return dialogs


def index(
    db_session: Session,
    attempt: IndexAttempt,
    doc_batch_generator: GenerateDocumentsOutput,
    run_time: float,
) -> None:
    indexing_pipeline = build_indexing_pipeline()

    run_dt = datetime.fromtimestamp(run_time, tz=timezone.utc)
    db_connector = attempt.connector
    db_credential = attempt.credential

    update_connector_credential_pair(
        db_session=db_session,
        connector_id=db_connector.id,
        credential_id=db_credential.id,
        attempt_status=IndexingStatus.IN_PROGRESS,
        run_dt=run_dt,
    )

    try:
        net_doc_change = 0
        document_count = 0
        chunk_count = 0
        for doc_batch in doc_batch_generator:
            logger.debug(
                f"Indexing batch of documents: {[doc.to_short_descriptor() for doc in doc_batch]}"
            )
            index_user_id = (
                None if db_credential.public_doc else db_credential.user_id
            )
            new_docs, total_batch_chunks = indexing_pipeline(
                documents=doc_batch,
                index_attempt_metadata=IndexAttemptMetadata(
                    user_id=index_user_id,
                    connector_id=db_connector.id,
                    credential_id=db_credential.id,
                ),
            )
            net_doc_change += new_docs
            chunk_count += total_batch_chunks
            document_count += len(doc_batch)
            update_docs_indexed(
                db_session=db_session,
                index_attempt=attempt,
                num_docs_indexed=document_count,
            )

            # check if connector is disabled mid run and stop if so
            db_session.refresh(db_connector)
            if db_connector.disabled:
                # let the `except` block handle this
                raise RuntimeError("Connector was disabled mid run")

        mark_attempt_succeeded(attempt, db_session)
        update_connector_credential_pair(
            db_session=db_session,
            connector_id=db_connector.id,
            credential_id=db_credential.id,
            attempt_status=IndexingStatus.SUCCESS,
            net_docs=net_doc_change,
            run_dt=run_dt,
        )

        logger.info(
            f"Indexed or updated {document_count} total documents for a total of {chunk_count} chunks"
        )
        logger.info(
            f"Connector successfully finished, elapsed time: {time.time() - run_time} seconds"
        )
    except Exception as e:
        logger.info(
            f"Failed connector elapsed time: {time.time() - run_time} seconds"
        )
        mark_attempt_failed(attempt, db_session, failure_reason=str(e))
        # The last attempt won't be marked failed until the next cycle's check for still in-progress attempts
        # The connector_credential_pair is marked failed here though to reflect correctly in UI asap
        update_connector_credential_pair(
            db_session=db_session,
            connector_id=attempt.connector.id,
            credential_id=attempt.credential.id,
            attempt_status=IndexingStatus.FAILED,
            net_docs=net_doc_change,
            run_dt=run_dt,
        )
        raise e


def run_wechat_indexing(
    db_session: Session,
    index_attempt: IndexAttempt,
) -> None:
    # msgs = preprocess_msgs(db_session, index_attempt)
    # dialogs = get_dialogs(db_session, msgs)
    dialogs = get_dialogs_mock(db_session)
    wx_batch_generator = load_from_dialogs(index_attempt, dialogs)
    index(db_session, index_attempt, wx_batch_generator, time.time())