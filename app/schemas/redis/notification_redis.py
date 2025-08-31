from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class NotificationRedis(BaseModel):
    id: str  # Redis key
    user_id: UUID
    title: str
    message: str
    type: str
    related_id: Optional[str] = None
    is_read: bool = False
    created_at: datetime
    
    @classmethod
    def create_key(cls, user_id: UUID, notification_id: str) -> str:
        return f"notification:{user_id}:{notification_id}"
    
    @classmethod
    def create_user_notifications_key(cls, user_id: UUID) -> str:
        return f"user_notifications:{user_id}"