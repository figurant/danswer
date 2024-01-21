from sqlalchemy import update
from uuid import UUID

from sqlalchemy.orm import Session

from danswer.db.models import DwsDialog
from danswer.utils.logger import setup_logger

logger = setup_logger()


def create_dws_dialog(
    db_session: Session,
    dialog_uuid: UUID,
    dialog_category: str = None,
    dialog_type: str = None,
    version: str = None,
    question: str = None,
    answer: str = None,
    type_reason: str = None,
    faq_gen: str = None,
    faq_material: str = None,
    is_expert_answered: bool = None
) -> UUID:
    dlg = DwsDialog(
        dialog_uuid=dialog_uuid,
        dialog_category=dialog_category,
        dialog_type=dialog_type,
        version=version,
        question=question,
        answer=answer,
        type_reason=type_reason,
        faq_gen=faq_gen,
        faq_material=faq_material,
        is_expert_answered=is_expert_answered
    )
    db_session.add(dlg)
    db_session.commit()
    return dlg.dialog_uuid

def update_dws_dialog_faq(
    db_session: Session,
    dialog_uuid: UUID,
    faq_gen: str = None
) -> UUID:
    stmt = update(DwsDialog).where(DwsDialog.dialog_uuid == dialog_uuid).values(faq_gen=faq_gen)
    db_session.execute(stmt)
    db_session.commit()



