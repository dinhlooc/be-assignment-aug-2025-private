from fastapi import APIRouter, Depends, Query, Path
from typing import List

from app.schemas.response.api_response import APIResponse
from app.schemas.response.notification_response import NotificationResponse
from app.dependencies.auth import get_current_user
from app.services.notification_service import (
    get_user_notifications,
    get_notification,
    mark_as_read,
    mark_all_as_read,
    delete_notification,
    get_unread_count
)
from app.core.exceptions import NotificationNotFoundException

notifications_router = APIRouter(prefix="/notifications", tags=["Notifications"])

@notifications_router.get(
    "/my",
    response_model=APIResponse[List[NotificationResponse]]
)
def get_my_notifications(
    skip: int = Query(0, ge=0, description="Number of notifications to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of notifications to return"),
    current_user = Depends(get_current_user)
):
    """
    Get current user's notifications
    """
    result = get_user_notifications(
        current_user.id, skip, limit
    )
    
    return APIResponse(
        code=200,
        message=f"Retrieved {len(result)} notifications",
        result=result
    )

@notifications_router.get(
    "/{notification_id}",
    response_model=APIResponse[NotificationResponse]
)
def get_notification_detail(
    notification_id: str = Path(..., description="Notification ID"),
    current_user = Depends(get_current_user)
):
    """
    Get a specific notification
    """
    notification = get_notification(current_user.id, notification_id)
    
    if not notification:
        raise NotificationNotFoundException()
    
    return APIResponse(
        code=200,
        message="Notification retrieved successfully",
        result=notification
    )

@notifications_router.put(
    "/{notification_id}/read",
    response_model=APIResponse[dict]
)
def mark_notification_as_read(
    notification_id: str = Path(..., description="Notification ID"),
    current_user = Depends(get_current_user)
):
    """
    Mark a specific notification as read
    """
    success = mark_as_read(current_user.id, notification_id)
    
    if not success:
        raise NotificationNotFoundException()
    
    return APIResponse(
        code=200,
        message="Notification marked as read",
        result={"success": True, "notification_id": notification_id}
    )

@notifications_router.put(
    "/mark-all-read",
    response_model=APIResponse[dict]
)
def mark_all_notifications_as_read(
    current_user = Depends(get_current_user)
):
    """
    Mark all user's notifications as read
    """
    updated_count = mark_all_as_read(current_user.id)
    
    return APIResponse(
        code=200,
        message=f"Marked {updated_count} notifications as read",
        result={"updated_count": updated_count}
    )

@notifications_router.delete(
    "/{notification_id}",
    response_model=APIResponse[dict]
)
def delete_notification_endpoint(
    notification_id: str = Path(..., description="Notification ID"),
    current_user = Depends(get_current_user)
):
    """
    Delete a notification
    """
    success = delete_notification(current_user.id, notification_id)
    
    if not success:
        raise NotificationNotFoundException()
    
    return APIResponse(
        code=200,
        message="Notification deleted successfully",
        result={"success": True, "notification_id": notification_id}
    )

@notifications_router.get(
    "/unread-count",
    response_model=APIResponse[dict]
)
def get_unread_notifications_count(
    current_user = Depends(get_current_user)
):
    """
    Get count of unread notifications
    """
    count = get_unread_count(current_user.id)
    
    return APIResponse(
        code=200,
        message="Unread count retrieved",
        result={"unread_count": count}
    )

router = APIRouter()
router.include_router(notifications_router)