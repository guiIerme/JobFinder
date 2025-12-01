from .models import Service, Chat, Message
from django.db.models import Q
from django.contrib.auth.models import User

def global_context(request):
    """Add global context variables to all templates"""
    service_categories = Service.CATEGORY_CHOICES
    
    # Initialize counts
    unread_chats_count = 0
    notifications_count = 0
    
    # Only calculate counts for authenticated users
    if request.user.is_authenticated:
        try:
            # Get unread messages count for the current user
            unread_chats_count = Message.objects.filter(
                Q(chat__customer=request.user) | Q(chat__professional=request.user)
            ).exclude(
                sender=request.user
            ).filter(
                status='sent'
            ).count()
            
            # For now, we'll set notifications count to 0 as we don't have a notifications system
            # This can be implemented later
            notifications_count = 0
        except:
            # If there's any error, just set counts to 0
            unread_chats_count = 0
            notifications_count = 0
    
    return {
        'service_categories': service_categories,
        'unread_chats_count': unread_chats_count,
        'notifications_count': notifications_count,
    }