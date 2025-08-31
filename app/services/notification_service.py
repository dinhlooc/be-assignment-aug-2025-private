from typing import List
from uuid import UUID

from typing import Optional

from app.repositories.notification import (
    create_notification as repo_create_notification,
    get_user_notifications as repo_get_user_notifications,
    get_notification as repo_get_notification,
    mark_as_read as repo_mark_as_read,
    mark_all_as_read as repo_mark_all_as_read,
    delete_notification as repo_delete_notification,
    get_unread_count as repo_get_unread_count
)   
from app.schemas.response.notification_response import NotificationResponse

def create_notification(user_id: UUID, title: str, message: str, 
                      type_: str, related_id: Optional[UUID] = None) -> NotificationResponse:
    """Create notification"""
    notification = repo_create_notification(
        str(user_id), title, message, type_, str(related_id) if related_id else None
    )
    return NotificationResponse(
        id=notification.id,
        user_id=notification.user_id,
        title=notification.title,
        message=notification.message,
        type=notification.type,
        related_id=notification.related_id,
        is_read=notification.is_read,
        created_at=notification.created_at
    )

def get_user_notifications(user_id: UUID, skip: int = 0, limit: int = 50) -> List[NotificationResponse]:
    """Get user's notifications"""
    notifications = repo_get_user_notifications(str(user_id), skip, limit)
    return [
        NotificationResponse(
            id=n.id,
            user_id=n.user_id,
            title=n.title,
            message=n.message,
            type=n.type,
            related_id=n.related_id,
            is_read=n.is_read,
            created_at=n.created_at
        ) for n in notifications
    ]

def get_notification(user_id: UUID, notification_id: str) -> Optional[NotificationResponse]:
    """Get a specific notification"""
    notification = repo_get_notification(str(user_id), notification_id)
    if notification:
        return NotificationResponse(
            id=notification.id,
            user_id=notification.user_id,
            title=notification.title,
            message=notification.message,
            type=notification.type,
            related_id=notification.related_id,
            is_read=notification.is_read,
            created_at=notification.created_at
        )
    return None

def mark_as_read(user_id: UUID, notification_id: str) -> bool:
    """Mark notification as read"""
    return repo_mark_as_read(str(user_id), notification_id)

def mark_all_as_read(user_id: UUID) -> int:
    """Mark all notifications as read"""
    return repo_mark_all_as_read(str(user_id))

def delete_notification(user_id: UUID, notification_id: str) -> bool:
    """Delete notification"""
    return repo_delete_notification(str(user_id), notification_id)

def get_unread_count(user_id: UUID) -> int:
    """Get unread count"""
    return repo_get_unread_count(str(user_id))