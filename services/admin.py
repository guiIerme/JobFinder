from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg, Sum
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import (
    Service, UserProfile, PaymentMethod, Order, Sponsor, 
    CustomService, Chat, Message, Review, ProfileChange, ServiceRequestModal, ServiceRequestSession,
    ContactMessage, RateLimitRecord
)
from .chat_models import ChatSession, ChatMessage, KnowledgeBaseEntry, ChatAnalytics

# Customize Admin Site
admin.site.site_header = 'Job Finder - Painel Administrativo'
admin.site.site_title = 'Job Finder Admin'
admin.site.index_title = 'Dashboard'

# Override admin index to add statistics
def admin_index(self, request, extra_context=None):
    """Custom admin index with dashboard statistics"""
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
        'active_services': Service.objects.filter(is_active=True).count() if hasattr(Service, 'is_active') else Service.objects.count(),
        
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
    recent_orders = Order.objects.select_related('customer', 'service').order_by('-created_at')[:5]
    recent_requests = ServiceRequestModal.objects.order_by('-created_at')[:5]
    recent_messages = ContactMessage.objects.order_by('-created_at')[:5]
    
    extra_context = extra_context or {}
    extra_context.update({
        'stats': stats,
        'recent_orders': recent_orders,
        'recent_requests': recent_requests,
        'recent_messages': recent_messages,
    })
    
    # Debug
    print(f"[Admin Dashboard] Stats: {stats}")
    print(f"[Admin Dashboard] Extra context keys: {extra_context.keys()}")
    
    return super(type(admin.site), admin.site).index(request, extra_context)

# Monkey patch the admin site index
admin.site.index = admin_index.__get__(admin.site, type(admin.site))

# Enhanced Model Admins
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_display', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    ordering = ['-created_at']
    
    def price_display(self, obj):
        return format_html('<strong style="color: #10b981;">R$ {}</strong>', obj.price)
    price_display.short_description = 'Preço'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'phone', 'rating']
    list_filter = ['user_type']
    search_fields = ['user__username', 'user__email', 'phone']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'service', 'status_badge', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__username', 'service__name']
    ordering = ['-created_at']
    
    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'confirmed': '#3b82f6',
            'in_progress': '#8b5cf6',
            'completed': '#10b981',
            'cancelled': '#ef4444'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600; font-size: 12px;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['customer', 'professional', 'rating_stars', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_verified', 'created_at']
    search_fields = ['customer__username', 'professional__username', 'comment']
    ordering = ['-created_at']
    
    def rating_stars(self, obj):
        stars = '⭐' * obj.rating
        return format_html('<span style="font-size: 16px;">{}</span>', stars)
    rating_stars.short_description = 'Avaliação'

admin.site.register(PaymentMethod)
admin.site.register(Sponsor)
admin.site.register(CustomService)
admin.site.register(Chat)
admin.site.register(Message)

@admin.register(ServiceRequestModal)
class ServiceRequestModalAdmin(admin.ModelAdmin):
    list_display = ['contact_name', 'service_name', 'contact_phone', 'contact_email', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'service']
    search_fields = ['contact_name', 'contact_email', 'contact_phone', 'service_name']
    readonly_fields = ['created_at', 'updated_at', 'ip_address', 'user_agent']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informações do Serviço', {
            'fields': ('service', 'service_name', 'service_description', 'estimated_price')
        }),
        ('Dados de Contato', {
            'fields': ('contact_name', 'contact_phone', 'contact_email')
        }),
        ('Detalhes', {
            'fields': ('user', 'notes', 'status')
        }),
        ('Informações do Sistema', {
            'fields': ('created_at', 'updated_at', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )

# Check if ProfileChange is already registered before registering
try:
    # Try to get the model admin for ProfileChange
    admin.site._registry[ProfileChange]
except KeyError:
    # If it's not registered, register it now
    @admin.register(ProfileChange)
    class ProfileChangeAdmin(admin.ModelAdmin):
        list_display = ('user', 'field_name', 'change_type', 'created_at')
        list_filter = ('change_type', 'field_name', 'created_at')
        search_fields = ('user__username', 'field_name')
        readonly_fields = ('user', 'field_name', 'old_value', 'new_value', 
                          'change_type', 'ip_address', 'user_agent', 'created_at')
        ordering = ('-created_at',)
        
        def has_add_permission(self, request):
            # Prevent adding profile changes manually
            return False
        
        def has_change_permission(self, request, obj=None):
            # Prevent changing profile changes
            return False


@admin.register(ServiceRequestSession)
class ServiceRequestSessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'user', 'service_id', 'current_step', 'created_at', 'expires_at', 'is_expired']
    list_filter = ['current_step', 'created_at', 'expires_at']
    search_fields = ['session_key', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'is_expired']
    ordering = ['-created_at']
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expirada'
    
    fieldsets = (
        ('Informações da Sessão', {
            'fields': ('session_key', 'user', 'service_id', 'current_step')
        }),
        ('Dados das Etapas', {
            'fields': ('step1_data', 'step2_data', 'step3_data'),
            'classes': ('collapse',)
        }),
        ('Controle de Tempo', {
            'fields': ('created_at', 'expires_at', 'is_expired')
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'subject', 'created_at']
    search_fields = ['name', 'email', 'phone', 'message']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informações do Remetente', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Mensagem', {
            'fields': ('subject', 'message')
        }),
        ('Gerenciamento', {
            'fields': ('status', 'admin_notes')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_replied', 'mark_as_archived']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(status='read')
        self.message_user(request, f'{updated} mensagem(ns) marcada(s) como lida(s).')
    mark_as_read.short_description = 'Marcar como lida'
    
    def mark_as_replied(self, request, queryset):
        updated = queryset.update(status='replied')
        self.message_user(request, f'{updated} mensagem(ns) marcada(s) como respondida(s).')
    mark_as_replied.short_description = 'Marcar como respondida'
    
    def mark_as_archived(self, request, queryset):
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} mensagem(ns) arquivada(s).')
    mark_as_archived.short_description = 'Arquivar'


@admin.register(RateLimitRecord)
class RateLimitRecordAdmin(admin.ModelAdmin):
    list_display = ['identifier', 'endpoint', 'request_count', 'limit', 'exceeded', 'created_at']
    list_filter = ['exceeded', 'created_at', 'endpoint']
    search_fields = ['identifier', 'endpoint']
    readonly_fields = ['identifier', 'endpoint', 'request_count', 'limit', 
                      'window_start', 'window_end', 'exceeded', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Rate Limit Information', {
            'fields': ('identifier', 'endpoint', 'request_count', 'limit', 'exceeded')
        }),
        ('Time Window', {
            'fields': ('window_start', 'window_end', 'created_at')
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent manual addition of rate limit records
        return False
    
    def has_change_permission(self, request, obj=None):
        # Make records read-only
        return False
    
    actions = ['delete_selected']
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        # Only allow deletion
        return {'delete_selected': actions['delete_selected']}



# ============================================================================
# Chat IA Assistant Admin
# ============================================================================

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'user_type', 'is_active', 'message_count', 'satisfaction_rating', 'created_at']
    list_filter = ['user_type', 'is_active', 'created_at']
    search_fields = ['session_id', 'user__username', 'anonymous_id']
    readonly_fields = ['session_id', 'created_at', 'updated_at', 'closed_at', 'message_count']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Session Information', {
            'fields': ('session_id', 'user', 'anonymous_id', 'user_type', 'is_active')
        }),
        ('Context Data', {
            'fields': ('context_data',),
            'classes': ('collapse',)
        }),
        ('Feedback', {
            'fields': ('satisfaction_rating',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'closed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def message_count(self, obj):
        return obj.message_count
    message_count.short_description = 'Messages'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['message_id', 'session', 'sender_type', 'content_preview', 'is_cached_response', 'processing_time_ms', 'created_at']
    list_filter = ['sender_type', 'is_cached_response', 'created_at']
    search_fields = ['message_id', 'session__session_id', 'content']
    readonly_fields = ['message_id', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Message Information', {
            'fields': ('message_id', 'session', 'sender_type', 'content')
        }),
        ('Metadata', {
            'fields': ('metadata', 'is_cached_response', 'processing_time_ms'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'



@admin.register(KnowledgeBaseEntry)
class KnowledgeBaseEntryAdmin(admin.ModelAdmin):
    list_display = ['entry_id', 'category', 'title', 'is_active', 'usage_count', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['entry_id', 'title', 'content', 'keywords']
    readonly_fields = ['entry_id', 'usage_count', 'created_at', 'updated_at']
    ordering = ['-usage_count', '-created_at']
    filter_horizontal = ['related_services']
    
    fieldsets = (
        ('Entry Information', {
            'fields': ('entry_id', 'category', 'title', 'content', 'is_active')
        }),
        ('Search & Relations', {
            'fields': ('keywords', 'related_services')
        }),
        ('Metadata', {
            'fields': ('metadata', 'usage_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ChatAnalytics)
class ChatAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['analytics_id', 'session', 'total_messages', 'user_messages', 'assistant_messages', 
                    'average_response_time_ms', 'resolved', 'escalated_to_human', 'engagement_score']
    list_filter = ['resolved', 'escalated_to_human', 'created_at']
    search_fields = ['analytics_id', 'session__session_id']
    readonly_fields = ['analytics_id', 'created_at', 'engagement_score']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Analytics Information', {
            'fields': ('analytics_id', 'session')
        }),
        ('Message Statistics', {
            'fields': ('total_messages', 'user_messages', 'assistant_messages', 'average_response_time_ms')
        }),
        ('Session Outcome', {
            'fields': ('resolved', 'escalated_to_human')
        }),
        ('Topics & Actions', {
            'fields': ('topics_discussed', 'actions_taken'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def engagement_score(self, obj):
        return obj.engagement_score
    engagement_score.short_description = 'Engagement Score'
