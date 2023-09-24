from collections.abc import Sequence
import datetime
from typing import List

from sqlalchemy import and_
from sqlalchemy import ColumnElement
from sqlalchemy import delete
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.orm import Session

from danswer.db.models import DwdWxDialog
from danswer.utils.logger import setup_logger
from uuid import UUID

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
