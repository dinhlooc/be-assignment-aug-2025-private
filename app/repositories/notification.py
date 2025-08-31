import redis
import json
from uuid import uuid4
from typing import List, Optional
from datetime import datetime

from app.config import settings
from app.schemas.redis.notification_redis import NotificationRedis

# Sync Redis client
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password,
    decode_responses=True
)


def create_notification(user_id: str, title: str, message: str, 
                      type_: str, related_id: Optional[str] = None) -> NotificationRedis:
    """Create a new notification in Redis"""
    notification_id = str(uuid4())
    notification = NotificationRedis(
        id=notification_id,
        user_id=user_id,
        title=title,
        message=message,
        type=type_,
        related_id=related_id,
        created_at=datetime.utcnow()
    )
    
    # Store notification data
    key = NotificationRedis.create_key(user_id, notification_id)
    redis_client.setex(key, settings.notification_ttl, notification.json())
    
    # Add to user's notification list
    user_key = NotificationRedis.create_user_notifications_key(user_id)
    redis_client.lpush(user_key, notification_id)
    redis_client.expire(user_key, settings.notification_ttl)
    
    return notification

def get_user_notifications(user_id: str, skip: int = 0, limit: int = 50) -> List[NotificationRedis]:
    """Get user's notifications with pagination"""
    user_key = NotificationRedis.create_user_notifications_key(user_id)
    notification_ids = redis_client.lrange(user_key, skip, skip + limit - 1)
    
    notifications = []
    for nid in notification_ids:
        key = NotificationRedis.create_key(user_id, nid)
        data = redis_client.get(key)
        if data:
            notification_data = json.loads(data)
            notifications.append(NotificationRedis(**notification_data))
    
    return notifications

def get_notification(user_id: str, notification_id: str) -> Optional[NotificationRedis]:
    """Get a specific notification"""
    key = NotificationRedis.create_key(user_id, notification_id)
    data = redis_client.get(key)
    if data:
        notification_data = json.loads(data)
        return NotificationRedis(**notification_data)
    return None

def mark_as_read(user_id: str, notification_id: str) -> bool:
    """Mark notification as read"""
    key = NotificationRedis.create_key(user_id, notification_id)
    data = redis_client.get(key)
    if data:
        notification_data = json.loads(data)
        notification_data['is_read'] = True
        redis_client.setex(key, settings.notification_ttl, json.dumps(notification_data))
        return True
    return False

def mark_all_as_read(user_id: str) -> int:
    """Mark all user's notifications as read"""
    user_key = NotificationRedis.create_user_notifications_key(user_id)
    notification_ids = redis_client.lrange(user_key, 0, -1)
    
    updated_count = 0
    for nid in notification_ids:
        if mark_as_read(user_id, nid):
            updated_count += 1
    
    return updated_count

def delete_notification(user_id: str, notification_id: str) -> bool:
    """Delete a notification"""
    key = NotificationRedis.create_key(user_id, notification_id)
    user_key = NotificationRedis.create_user_notifications_key(user_id)
    
    # Remove from user's list
    redis_client.lrem(user_key, 0, notification_id)
    
    # Delete notification data
    deleted = redis_client.delete(key)
    return deleted > 0

def get_unread_count(user_id: str) -> int:
    """Get count of unread notifications"""
    notifications = get_user_notifications(user_id, 0, 1000)  # Get all
    return sum(1 for n in notifications if not n.is_read)