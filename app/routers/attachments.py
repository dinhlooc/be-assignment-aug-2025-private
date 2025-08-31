from fastapi import APIRouter, UploadFile, File, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi.responses import FileResponse
from app.schemas.response.api_response import APIResponse
from app.schemas.response.attachment_response import AttachmentResponse
from app.dependencies.attachment import require_attachment_delete_access, require_task_attachment_access, require_attachment_access
from app.database import get_db
from app.services import attachment_service

attachments_router = APIRouter(prefix="/attachments", tags=["Attachments"])

@attachments_router.post(
    "/tasks/{task_id}",
    response_model=APIResponse[AttachmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload attachment for task"
)
def upload_task_attachment(
    task_id: UUID,
    file: UploadFile = File(...),
    task_access=Depends(require_task_attachment_access),
    db: Session = Depends(get_db)
):
    """
    Upload a file attachment for a task (max 3 files, max 5MB/file)
    """
    current_user, task = task_access
    result = attachment_service.upload_attachment(db, task_id, file, current_user.id)
    return APIResponse(
        code=201,
        message="Attachment uploaded successfully",
        result=result
    )

@attachments_router.get(
    "/{attachment_id}",
    response_class=FileResponse,
    summary="Download attachment"
)
def download_attachment(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    attachment = Depends(require_attachment_access),
    
):
    """
    Download an attachment file (permission checked via task)
    """
    return FileResponse(
        path=attachment.file_url,
        filename=attachment.file_name,
        media_type="application/octet-stream"
    )

@attachments_router.get(
    "/tasks/{task_id}",
    response_model=APIResponse[list[AttachmentResponse]],
    summary="Get all attachments of a task"
)
def get_attachments_by_task(
    task_id: UUID,
    task_access=Depends(require_task_attachment_access),
    db: Session = Depends(get_db)
):
    """
    Get all attachments for a specific task (permission checked via task)
    """
    attachments = attachment_service.get_attachments_by_task(db, task_id)
    return APIResponse(
        code=200,
        message=f"Found {len(attachments)} attachments",
        result=attachments
    )

@attachments_router.delete(
    "/{attachment_id}",
    response_model=APIResponse[dict],
    summary="Delete attachment"
)
def delete_attachment(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    attachment = Depends(require_attachment_delete_access)
):
    """
    Delete an attachment file (permission checked via task)
    """
    success = attachment_service.delete_attachment(db, attachment_id)
    return APIResponse(
        code=200,
        message="Attachment deleted successfully",
        result={"deleted": success, "attachment_id": str(attachment_id)}
    )

router = APIRouter()
router.include_router(attachments_router)