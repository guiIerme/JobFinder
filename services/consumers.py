"""
WebSocket consumers for real-time functionality.

This module implements WebSocket consumers for handling real-time
notifications and other bidirectional communication with clients.

Requirements: 8.1, 8.2
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    
    Handles user authentication, group management, and notification delivery.
    Supports up to 10,000 simultaneous connections.
    
    Requirements: 8.1, 8.2
    """
    
    async def connect(self):
        """
        Handle WebSocket connection.
        
        Authenticates the user and adds them to their personal notification group.
        Only authenticated users can establish WebSocket connections.
        """
        # Get user from scope (set by AuthMiddlewareStack)
        self.user = self.scope.get('user')
        
        # Reject connection if user is not authenticated
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)  # Custom close code for authentication failure
            return
        
        # Create a unique group name for this user
        self.user_group_name = f'user_{self.user.id}'
        
        # Add this connection to the user's group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        # Accept the WebSocket connection
        await self.accept()
        
        # Send a welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to notification service',
            'user_id': self.user.id,
            'username': self.user.username
        }))
    
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        
        Removes the user from their notification group.
        
        Args:
            close_code: WebSocket close code
        """
        # Remove this connection from the user's group
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Handle messages received from the WebSocket client.
        
        Supports heartbeat/ping messages to keep the connection alive.
        
        Args:
            text_data: JSON string containing the message
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            # Handle heartbeat/ping messages
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
            
            # Handle mark notification as read
            elif message_type == 'mark_read':
                notification_id = data.get('notification_id')
                if notification_id:
                    success = await self.mark_notification_read(notification_id)
                    await self.send(text_data=json.dumps({
                        'type': 'mark_read_response',
                        'notification_id': notification_id,
                        'success': success
                    }))
            
            # Handle get unread count
            elif message_type == 'get_unread_count':
                count = await self.get_unread_count()
                await self.send(text_data=json.dumps({
                    'type': 'unread_count',
                    'count': count
                }))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def notification_message(self, event):
        """
        Handle notification messages sent to the user's group.
        
        This method is called when a notification is sent to the user's group
        via channel_layer.group_send().
        
        Args:
            event: Dictionary containing notification data
        """
        # Extract notification data from the event
        notification_data = event.get('notification', {})
        
        # Send the notification to the WebSocket client
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': notification_data
        }))
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """
        Mark a notification as read in the database.
        
        Args:
            notification_id: ID of the notification to mark as read
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from services.models import Notification
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.is_read = True
            notification.save(update_fields=['is_read'])
            return True
        except Notification.DoesNotExist:
            return False
        except Exception:
            return False
    
    @database_sync_to_async
    def get_unread_count(self):
        """
        Get the count of unread notifications for the user.
        
        Returns:
            int: Number of unread notifications
        """
        try:
            from services.models import Notification
            return Notification.objects.filter(
                user=self.user,
                is_read=False
            ).count()
        except Exception:
            return 0
