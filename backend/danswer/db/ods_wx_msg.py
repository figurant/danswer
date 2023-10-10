from collections.abc import Sequence
import datetime
from sqlalchemy import and_
from sqlalchemy import ColumnElement
from sqlalchemy import delete
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.orm import Session

from danswer.connectors.file.utils import get_file_ext
from danswer.db.dwd_wx_dialog import delete_dwd_wx_dialog_by_meta
from danswer.db.models import OdsWxMsg, Connector
from danswer.utils.logger import setup_logger


logger = setup_logger()


def create_wx_msg(
    sender_name: str,
    send_time: datetime.datetime,
    msg_content: str,
    meta_info: str,
    db_session: Session,
) -> OdsWxMsg:
    wx_msg = OdsWxMsg(
        sender_name=sender_name,
        send_time=send_time,
        msg_content=msg_content,
        meta_info=meta_info
    )
    db_session.add(wx_msg)
    db_session.commit()

    return wx_msg


def get_wx_msg(
    msg_id: int,
    db_session: Session
) -> OdsWxMsg | None:
    stmt = select(OdsWxMsg)
    stmt = stmt.where(OdsWxMsg.id == msg_id)
    return db_session.execute(stmt).scalars().first()


def delete_wx_msg_by_conn_id(
    connector_id: int,
    db_session: Session,
) -> None:
    stmt = select(Connector).where(
        Connector.id == connector_id
    )
    connector = db_session.execute(stmt).scalars().first()

    extension = ""
    file_locations = connector.connector_specific_config['file_locations']
    if len(file_locations) > 0:
        extension = get_file_ext(file_locations[0])
    if extension == ".wx":
        delete_dwd_wx_dialog_by_meta(
            file_locations[0],
            db_session
        )
        stmt = delete(OdsWxMsg).where(
            OdsWxMsg.meta_info == file_locations[0]
        )
        db_session.execute(stmt)
