from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.attachment import Attachment

def create_attachment(db: Session, file_name: str, file_url: str, task_id: UUID, author_id: UUID) -> Attachment:
    attachment = Attachment(file_name=file_name, file_url=file_url, task_id=task_id, author_id=author_id)
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment

def get_attachments_by_task(db: Session, task_id: UUID) -> List[Attachment]:
    return db.query(Attachment).filter(Attachment.task_id == task_id).all()

def get_attachment_by_id(db: Session, attachment_id: UUID) -> Optional[Attachment]:
    return db.query(Attachment).filter(Attachment.id == attachment_id).first()

def delete_attachment(db: Session, attachment_id: UUID) -> bool:
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        return False
    db.delete(attachment)
    db.commit()
    return True

def count_attachments_by_task(db: Session, task_id: UUID) -> int:
    return db.query(Attachment).filter(Attachment.task_id == task_id).count()