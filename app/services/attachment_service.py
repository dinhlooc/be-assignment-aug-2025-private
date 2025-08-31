import os
from fastapi import UploadFile
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from app.repositories import attachment as attachment_repo
from app.config import settings
from app.core.exceptions import (
    AttachmentLimitExceededException,
    AttachmentFileTooLargeException,
    AttachmentFileTypeInvalidException,
    AttachmentNotFoundException,
    AttachmentDeleteFailedException,
    AttachmentUploadFailedException
)
from app.schemas.response.attachment_response import AttachmentResponse

ALLOWED_EXTENSIONS = settings.allowed_extensions.split(",")
MAX_FILE_SIZE = settings.max_file_size
MAX_FILES_PER_TASK = settings.max_files_per_task
UPLOAD_DIR = settings.upload_dir

def validate_file(file: UploadFile):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise AttachmentFileTypeInvalidException()
    # Đọc thử 1 chunk để check size
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZE:
        raise AttachmentFileTooLargeException()

def save_file(file: UploadFile) -> str:
    ext = file.filename.split(".")[-1].lower()
    unique_name = f"{uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return file_path

def upload_attachment(db: Session, task_id: UUID, file: UploadFile, author_id: UUID) -> AttachmentResponse:
    # Check số lượng file đã đính kèm
    count = attachment_repo.count_attachments_by_task(db, task_id)
    if count >= MAX_FILES_PER_TASK:
        raise AttachmentLimitExceededException()
    validate_file(file)
    try:
        file_path = save_file(file)
        attachment = attachment_repo.create_attachment(
            db, file.filename, file_path, task_id, author_id
        )
        return AttachmentResponse(
            id=attachment.id,
            file_name=attachment.file_name,
            file_url=attachment.file_url,
            task_id=attachment.task_id,
            author_id=attachment.author_id
        )
    except Exception as e:
        raise AttachmentUploadFailedException(str(e))

def get_attachment(db: Session, attachment_id: UUID) -> AttachmentResponse:
    attachment = attachment_repo.get_attachment_by_id(db, attachment_id)
    if not attachment:
        raise AttachmentNotFoundException()
    return AttachmentResponse(
        id=attachment.id,
        file_name=attachment.file_name,
        file_url=attachment.file_url,
        task_id=attachment.task_id,
        author_id=attachment.author_id
    )

def get_attachments_by_task(db: Session, task_id: UUID) -> list[AttachmentResponse]:
    from app.repositories import attachment as attachment_repo
    attachments = attachment_repo.get_attachments_by_task(db, task_id)
    return [
        AttachmentResponse(
            id=a.id,
            file_name=a.file_name,
            file_url=a.file_url,
            task_id=a.task_id,
            author_id=a.author_id
        ) for a in attachments
    ]

def delete_attachment(db: Session, attachment_id: UUID) -> bool:
    attachment = attachment_repo.get_attachment_by_id(db, attachment_id)
    if not attachment:
        raise AttachmentNotFoundException()
    try:
        if os.path.exists(attachment.file_url):
            os.remove(attachment.file_url)
        return attachment_repo.delete_attachment(db, attachment_id)
    except Exception as e:
        raise AttachmentDeleteFailedException(str(e))