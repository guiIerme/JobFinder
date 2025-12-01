"""
WebSocket utility functions for sending real-time notifications.

This module provides helper functions to send notifications to users
via WebSocket connections.

Requirements: 8.2, 8.3
"""

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from typing import Dict, Any, Optional


def send_notification_to_user(user_id: int, notification_data: Dict[str, Any]) -> bool:
    """
    Send a notification to a specific user via WebSocket.
    
    This function sends a notification to the user's WebSocket group,
    which will be received by all active WebSocket connections for that user.
    
    Requirements: 8.2 - Send notifications in less than 100ms
    
    Args:
        user_id: ID of the user to send the notification to
        notification_data: Dictionary containing notification details
            Expected keys:
                - id: Notification ID
                - title: Notification title
                - message: Notification message
                - notification_type: Type of notification
                - created_at: ISO format timestamp
                - is_read: Boolean indicating if read
                - related_object_id: Optional related object ID
                - related_object_type: Optional related object type
    
    Returns:
        bool: True if sent successfully, False otherwise
    
    Example:
        >>> send_notification_to_user(
        ...     user_id=123,
        ...     notification_data={
        ...         'id': 456,
        ...         'title': 'New Service Request',
        ...         'message': 'You have a new service request',
        ...         'notification_type': 'service_request',
        ...         'created_at': '2025-11-17T10:30:00Z',
        ...         'is_read': False
        ...     }
        ... )
        True
    """
    try:
        channel_layer = get_channel_layer()
        user_group_name = f'user_{user_id}'
        
        # Send the notification to the user's group
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'notification_message',
                'notification': notification_data
            }
        )
        return True
    except Exception as e:
        # Log the error but don't raise it
        # This ensures that notification failures don't break the main flow
        print(f"Error sending WebSocket notification to user {user_id}: {e}")
        return False


def send_notification_to_multiple_users(user_ids: list, notification_data: Dict[str, Any]) -> Dict[int, bool]:
    """
    Send a notification to multiple users via WebSocket.
    
    Args:
        user_ids: List of user IDs to send the notification to
        notification_data: Dictionary containing notification details
    
    Returns:
        dict: Dictionary mapping user_id to success status (True/False)
    
    Example:
        >>> send_notification_to_multiple_users(
        ...     user_ids=[123, 456, 789],
        ...     notification_data={
        ...         'title': 'System Announcement',
        ...         'message': 'Scheduled maintenance tonight'
        ...     }
        ... )
        {123: True, 456: True, 789: False}
    """
    results = {}
    for user_id in user_ids:
        results[user_id] = send_notification_to_user(user_id, notification_data)
    return results


def create_and_send_notification(
    user: User,
    notification_type: str,
    title: str,
    message: str,
    sender: Optional[User] = None,
    related_object_id: Optional[int] = None,
    related_object_type: Optional[str] = None
) -> Optional[int]:
    """
    Create a notification in the database and send it via WebSocket.
    
    This is a convenience function that combines database creation with
    WebSocket delivery for seamless notification handling.
    
    Requirements: 8.2, 8.3
    
    Args:
        user: User to send the notification to
        notification_type: Type of notification (from Notification.NOTIFICATION_TYPES)
        title: Notification title
        message: Notification message
        sender: Optional user who triggered the notification
        related_object_id: Optional ID of related object
        related_object_type: Optional type of related object
    
    Returns:
        int: Notification ID if successful, None otherwise
    
    Example:
        >>> from django.contrib.auth.models import User
        >>> user = User.objects.get(id=123)
        >>> create_and_send_notification(
        ...     user=user,
        ...     notification_type='service_request',
        ...     title='New Service Request',
        ...     message='You have a new service request from John Doe',
        ...     related_object_id=456,
        ...     related_object_type='ServiceRequest'
        ... )
        789
    """
    try:
        from services.models import Notification
        from django.utils import timezone
        
        # Create the notification in the database
        notification = Notification.objects.create(
            user=user,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            related_object_id=related_object_id,
            related_object_type=related_object_type,
            is_read=False
        )
        
        # Prepare notification data for WebSocket
        notification_data = {
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'notification_type': notification.notification_type,
            'created_at': notification.created_at.isoformat(),
            'is_read': notification.is_read,
            'sender_id': sender.id if sender else None,
            'sender_username': sender.username if sender else None,
            'related_object_id': notification.related_object_id,
            'related_object_type': notification.related_object_type
        }
        
        # Send via WebSocket
        send_notification_to_user(user.id, notification_data)
        
        return notification.id
    
    except Exception as e:
        print(f"Error creating and sending notification: {e}")
        return None


def broadcast_system_notification(title: str, message: str, user_ids: Optional[list] = None) -> int:
    """
    Broadcast a system notification to all users or specific users.
    
    Args:
        title: Notification title
        message: Notification message
        user_ids: Optional list of specific user IDs. If None, sends to all users.
    
    Returns:
        int: Number of notifications successfully sent
    
    Example:
        >>> broadcast_system_notification(
        ...     title='Scheduled Maintenance',
        ...     message='The system will be down for maintenance from 2-4 AM',
        ...     user_ids=[123, 456]  # Optional: specific users
        ... )
        2
    """
    try:
        from services.models import Notification
        from django.contrib.auth.models import User
        
        # Get target users
        if user_ids:
            users = User.objects.filter(id__in=user_ids)
        else:
            users = User.objects.filter(is_active=True)
        
        success_count = 0
        
        for user in users:
            notification_id = create_and_send_notification(
                user=user,
                notification_type='system',
                title=title,
                message=message
            )
            if notification_id:
                success_count += 1
        
        return success_count
    
    except Exception as e:
        print(f"Error broadcasting system notification: {e}")
        return 0
