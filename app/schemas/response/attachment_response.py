from pydantic import BaseModel
from uuid import UUID

class AttachmentResponse(BaseModel):
    id: UUID
    file_name: str
    file_url: str
    task_id: UUID
    author_id: UUID