"""
WebSocket URL routing configuration for home_services project.

This module defines the WebSocket URL patterns for the application,
mapping WebSocket connections to their respective consumers.
"""

from django.urls import path
from services import consumers
from services.chat.consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
    path('ws/chat/', ChatConsumer.as_asgi()),
]
