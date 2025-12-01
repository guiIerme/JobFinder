"""
Chat Analytics URL Configuration

URL patterns for chat analytics dashboard and API endpoints.
Requirements: 7.2, 7.4
"""

from django.urls import path
from . import analytics_views

urlpatterns = [
    path('', analytics_views.chat_analytics_dashboard, name='chat_analytics_dashboard'),
    path('api/', analytics_views.chat_analytics_api, name='chat_analytics_api'),
    
    # Export endpoints (Requirements: 7.4)
    path('export/sessions/', analytics_views.export_chat_sessions, name='export_chat_sessions'),
    path('export/messages/', analytics_views.export_chat_messages, name='export_chat_messages'),
    path('export/analytics/', analytics_views.export_chat_analytics, name='export_chat_analytics'),
]
