# Admin Customization - Modern Dashboard
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg, Sum
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
import json

class ModernAdminSite(admin.AdminSite):
    site_header = 'Job Finder - Painel Administrativo'
    site_title = 'Job Finder Admin'
    index_title = 'Dashboard'
    
    def index(self, request, extra_context=None):
        """
        Custom admin index with dashboard statistics
        """
        from .models import (
            Service, UserProfile, Order, ServiceRequestModal,
            ContactMessage, Review
        )
        from .chat_models import ChatSession, ChatMessage
        
        # Calculate statistics
        from django.contrib.auth.models import User
        
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        
        stats = {
            # Users
            'total_users': User.objects.count(),
            'new_users_30d': User.objects.filter(date_joined__gte=last_30_days).count(),
            'providers': UserProfile.objects.filter(user_type='professional').count(),
            
            # Services
            'total_services': Service.objects.count(),
            'active_services': Service.objects.filter(is_active=True).count(),
            
            # Orders
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'completed_orders': Order.objects.filter(status='completed').count(),
            'orders_30d': Order.objects.filter(created_at__gte=last_30_days).count(),
            
            # Service Requests
            'total_requests': ServiceRequestModal.objects.count(),
            'pending_requests': ServiceRequestModal.objects.filter(status='pending').count(),
            'requests_7d': ServiceRequestModal.objects.filter(created_at__gte=last_7_days).count(),
            
            # Contact Messages
            'unread_messages': ContactMessage.objects.filter(status='unread').count(),
            'total_messages': ContactMessage.objects.count(),
            
            # Reviews
            'total_reviews': Review.objects.count(),
            'avg_rating': Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0,
            
            # Chat
            'total_chat_sessions': ChatSession.objects.count(),
            'active_chat_sessions': ChatSession.objects.filter(is_active=True).count(),
            'total_chat_messages': ChatMessage.objects.count(),
            'chat_sessions_7d': ChatSession.objects.filter(created_at__gte=last_7_days).count(),
        }
        
        # Recent activity
        recent_orders = Order.objects.select_related('user', 'service').order_by('-created_at')[:5]
        recent_requests = ServiceRequestModal.objects.order_by('-created_at')[:5]
        recent_messages = ContactMessage.objects.order_by('-created_at')[:5]
        
        extra_context = extra_context or {}
        extra_context.update({
            'stats': stats,
            'recent_orders': recent_orders,
            'recent_requests': recent_requests,
            'recent_messages': recent_messages,
        })
        
        return super().index(request, extra_context)

# Create custom admin site instance
modern_admin_site = ModernAdminSite(name='modern_admin')
