from typing import List
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.orm import Session

from danswer.db.models import DwdWxDialog, OdsWxMsg
from danswer.utils.logger import setup_logger

logger = setup_logger()


def create_dwd_wx_dialog(
    db_session: Session,
    msg_id: int,
    msg_type: str,
    dialog_uuid: UUID,
    dialog_type: str = None,
    extra_info: str = None
) -> int:
    wx_dlg = DwdWxDialog(
        msg_id=msg_id,
        msg_type=msg_type,
        dialog_uuid=dialog_uuid,
        dialog_type=dialog_type,
        extra_info=extra_info
    )
    db_session.add(wx_dlg)
    db_session.commit()

    return wx_dlg.id


def get_dwd_wx_dialog_all(
    db_session: Session
) -> List[DwdWxDialog] | None:
    stmt = select(DwdWxDialog)
    return db_session.execute(stmt).scalars()


def delete_dwd_wx_dialog_by_meta(
    meta_info: str,
    db_session: Session,
) -> None:
    stmt = select(OdsWxMsg).where(
        OdsWxMsg.meta_info == meta_info
    )
    msgs = db_session.execute(stmt).scalars()
    msg_ids = []
    for msg in msgs:
        msg_ids.append(msg.id)
    stmt = delete(DwdWxDialog).where(
        DwdWxDialog.msg_id.in_(msg_ids)
    )
    db_session.execute(stmt)
    db_session.commit()

