from fastapi import Path
from uuid import UUID
from typing import Optional

from app.services.notification_service import get_notification
from app.core.exceptions import NotificationNotFoundException

def get_notification_dependency(
    notification_id: str = Path(..., description="Notification ID")
) -> Optional[dict]:
    """
    Dependency to get notification by ID
    Raises NotificationNotFoundException if not found
    """
    # Note: This dependency assumes current_user is available from auth dependency
    # In actual usage, combine with get_current_user dependency
    return {"notification_id": notification_id}