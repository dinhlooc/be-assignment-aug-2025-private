from fastapi import Depends, Path
from uuid import UUID
from app.dependencies.task import require_task_access
from app.services.attachment_service import get_attachment 
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.core.exceptions import AttachmentNotFoundException, UserNotInProjectException, AttachmentDeleteFailedException
from app.services.project_member_service import check_project_access_permission
def require_task_attachment_access(
    task_id: UUID = Path(...),
    task_access=Depends(require_task_access)
):
    # task_access đã kiểm tra quyền truy cập task
    return task_access

def require_attachment_access(
    attachment_id: UUID = Path(...),
    db = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    # Lấy attachment từ DB
    attachment = get_attachment(db, attachment_id)
    if not attachment:
        raise AttachmentNotFoundException()
    # Kiểm tra quyền truy cập task
    require_task_access(task_id=attachment.task_id, db=db, current_user=current_user)
    return attachment

def require_attachment_delete_access(
    attachment_id: UUID = Path(...),
    db = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    # Lấy attachment từ DB
    attachment = get_attachment(db, attachment_id)
    if not attachment:
        raise AttachmentNotFoundException()
    # Kiểm tra quyền truy cập task
    task_access = require_task_access(task_id=attachment.task_id, db=db, current_user=current_user)
    task = task_access[1]
    # Chỉ Admin/Manager mới được xóa attachment
    if current_user.role == "admin":
        return attachment
    elif current_user.role == "manager":
        # Manager phải là thành viên của project
        if not check_project_access_permission(db, task.project_id, current_user.id):
            raise UserNotInProjectException()  
        return attachment
    elif current_user.role == "member":
        # Member phải là thành viên của project
        if not check_project_access_permission(db, task.project_id, current_user.id):
            raise UserNotInProjectException()
        if attachment.author_id != current_user.id:
            raise AttachmentDeleteFailedException("You can only delete your own attachments")
        return attachment

    else:
        raise AttachmentDeleteFailedException("You do not have permission to delete this attachment")
