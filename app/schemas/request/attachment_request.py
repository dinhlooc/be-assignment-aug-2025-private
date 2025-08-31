from pydantic import BaseModel

class AttachmentUploadRequest(BaseModel):
    pass  # Không cần field, chỉ dùng để giữ format nếu muốn mở rộng sau này