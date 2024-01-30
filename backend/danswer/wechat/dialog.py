from typing import List
from uuid import UUID

from danswer.db.dwd_wx_dialog import create_dwd_wx_dialog
from danswer.db.dws_dialog import create_dws_dialog, update_dws_dialog_faq
from danswer.wechat.prompts import MESSAGE_TYPE_USER_QUESTION, MESSAGE_TYPE_USER_ANSWER
from sqlalchemy.orm import Session


class Message:
    id: int
    sender: str
    send_time: str
    content: str
    type: int

    def __init__(self, id, sender, send_time, content, type):
        self.id = id
        self.sender = sender
        self.send_time = send_time
        self.content = content
        self.type = type

    def get_msg_txt(self):
        return f"{self.id}|{self.sender}|{self.send_time}|{self.content}"


class Dialog:
    messages: List[Message]
    has_answer: bool
    uuid: UUID
    dialog_category: str = None,
    dialog_type: str = None,
    version: str = None,
    question: str = None,
    answer: str = None,
    type_reason: str = None,
    faq_gen: str = None

    def __init__(self, uuid, messages, has_answer: bool = False):
        self.uuid = uuid
        self.messages = messages
        self.has_answer = has_answer

    def add_extend_info(self, dialog_category, dialog_type, version, question, answer, type_reason):
        self.dialog_category = dialog_category
        self.dialog_type = dialog_type,
        self.version = version,
        self.question = question,
        self.answer = answer,
        self.type_reason = type_reason

    def add_faq_gen(self, faq_gen):
        self.faq_gen = faq_gen

    def add_message(self, message):
        self.messages.append(message)

    def set_has_answer(self):
        self.has_answer = True

    def get_qa_block(self):
        qa_block = ""
        for msg in self.messages:
            if int(msg.type) == MESSAGE_TYPE_USER_QUESTION or int(msg.type) == MESSAGE_TYPE_USER_ANSWER:
                qa = "Question"
            else:
                qa = "Answer"
            qa_block += f"{qa}: {msg.content}\n"
        return qa_block

    def get_faq_material(self):
        qa_block = ""
        for msg in self.messages:
            qa_block += f"{msg.sender}: {msg.content}\n"
        return qa_block

    def can_gen_faq(self):
        return True
        # 对于产品使用咨询和产品需求，可以生成FQA作为知识库测试集。
        # return self.has_answer and (self.dialog_category == 1 or self.dialog_category == 4)

    def commit_dialog(self, db_session: Session):
        self.commit_dwd_wx_dialog(db_session)
        self.commit_dws_dialog(db_session)

    def commit_dwd_wx_dialog(self, db_session: Session):
        for m in self.messages:
            create_dwd_wx_dialog(db_session, m.id, m.type, str(self.uuid))

    def commit_dws_dialog(self, db_session: Session):
        create_dws_dialog(db_session,
                          str(self.uuid),
                          self.dialog_category,
                          self.dialog_type,
                          self.version,
                          self.question,
                          self.answer,
                          self.type_reason,
                          None,
                          self.get_faq_material(),
                          self.has_answer)

    def commit_dws_dialog_faq(self, db_session: Session):
        update_dws_dialog_faq(db_session, self.uuid, self.faq_gen)
