"""
ASGI config for home_services project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import routing and security middleware after Django is initialized
from home_services.routing import websocket_urlpatterns
from services.chat.security import WebSocketSecurityMiddleware

# WebSocket application with security layers
# Requirements: 8.3 (Security - CORS, origin validation, authentication)
websocket_app = AllowedHostsOriginValidator(
    WebSocketSecurityMiddleware(  # Custom origin validation
        AuthMiddlewareStack(  # Django authentication
            URLRouter(websocket_urlpatterns)
        )
    )
)

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": websocket_app,
})
