"""
Chat Analytics Views

Views for displaying chat analytics and metrics in the admin dashboard.
Requirements: 7.2, 7.4
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Avg, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from services.chat_models import ChatSession, ChatMessage, ChatAnalytics
from django.contrib.auth.models import User
import csv
import json


@staff_member_required
def chat_analytics_dashboard(request):
    """
    Display chat analytics dashboard with session statistics.
    
    Shows:
    - Active sessions count
    - Average response time
    - Satisfaction ratings
    - Total messages
    - Resolution rate
    - Top topics discussed
    
    Requirements: 7.2
    """
    # Get time range from query params (default: last 7 days)
    days = int(request.GET.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)
    
    # Active sessions
    active_sessions = ChatSession.objects.filter(
        is_active=True
    ).count()
    
    # Total sessions in time range
    total_sessions = ChatSession.objects.filter(
        created_at__gte=start_date
    ).count()
    
    # Get analytics for time range
    analytics_qs = ChatAnalytics.objects.filter(
        created_at__gte=start_date
    )
    
    # Calculate aggregate metrics
    analytics_stats = analytics_qs.aggregate(
        avg_response_time=Avg('average_response_time_ms'),
        total_messages=Count('analytics_id'),
        resolved_count=Count('analytics_id', filter=Q(resolved=True)),
        escalated_count=Count('analytics_id', filter=Q(escalated_to_human=True))
    )
    
    # Calculate average satisfaction rating
    satisfaction_stats = ChatSession.objects.filter(
        created_at__gte=start_date,
        satisfaction_rating__isnull=False
    ).aggregate(
        avg_rating=Avg('satisfaction_rating'),
        rating_count=Count('satisfaction_rating')
    )
    
    # Resolution rate
    resolution_rate = 0
    if total_sessions > 0:
        resolution_rate = round(
            (analytics_stats['resolved_count'] / total_sessions) * 100, 1
        )
    
    # Get top topics discussed
    all_topics = []
    for analytics in analytics_qs:
        all_topics.extend(analytics.topics_discussed)
    
    # Count topic frequency
    topic_counts = {}
    for topic in all_topics:
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    # Sort by frequency and get top 10
    top_topics = sorted(
        topic_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    # Get user type distribution
    user_type_stats = ChatSession.objects.filter(
        created_at__gte=start_date
    ).values('user_type').annotate(
        count=Count('session_id')
    ).order_by('-count')
    
    # Get recent sessions with analytics
    recent_sessions = ChatSession.objects.filter(
        created_at__gte=start_date
    ).select_related('user').prefetch_related('analytics').order_by('-created_at')[:20]
    
    # Prepare session data with analytics
    session_data = []
    for session in recent_sessions:
        try:
            analytics = session.analytics
            session_data.append({
                'session': session,
                'analytics': analytics,
                'engagement_score': analytics.engagement_score
            })
        except ChatAnalytics.DoesNotExist:
            session_data.append({
                'session': session,
                'analytics': None,
                'engagement_score': 0
            })
    
    # Get hourly message distribution for chart
    hourly_stats = []
    for hour in range(24):
        count = ChatMessage.objects.filter(
            created_at__gte=start_date,
            created_at__hour=hour
        ).count()
        hourly_stats.append({
            'hour': hour,
            'count': count
        })
    
    # Get daily session counts for trend chart
    daily_stats = []
    for i in range(days):
        day_start = timezone.now() - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = ChatSession.objects.filter(
            created_at__gte=day_start,
            created_at__lt=day_end
        ).count()
        daily_stats.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'count': count
        })
    daily_stats.reverse()
    
    context = {
        'active_sessions': active_sessions,
        'total_sessions': total_sessions,
        'avg_response_time': round(analytics_stats['avg_response_time'] or 0, 2),
        'avg_satisfaction': round(satisfaction_stats['avg_rating'] or 0, 2),
        'satisfaction_count': satisfaction_stats['rating_count'],
        'resolution_rate': resolution_rate,
        'resolved_count': analytics_stats['resolved_count'],
        'escalated_count': analytics_stats['escalated_count'],
        'top_topics': top_topics,
        'user_type_stats': user_type_stats,
        'session_data': session_data,
        'hourly_stats': hourly_stats,
        'daily_stats': daily_stats,
        'days': days,
        'start_date': start_date,
    }
    
    return render(request, 'services/chat_analytics_dashboard.html', context)


@staff_member_required
def chat_analytics_api(request):
    """
    API endpoint for real-time chat analytics data.
    
    Returns JSON with current metrics for dashboard updates.
    Requirements: 7.2
    """
    # Get active sessions
    active_sessions = ChatSession.objects.filter(is_active=True).count()
    
    # Get recent analytics (last hour)
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_analytics = ChatAnalytics.objects.filter(
        created_at__gte=one_hour_ago
    ).aggregate(
        avg_response_time=Avg('average_response_time_ms'),
        total_messages=Count('total_messages')
    )
    
    # Get recent satisfaction ratings
    recent_satisfaction = ChatSession.objects.filter(
        updated_at__gte=one_hour_ago,
        satisfaction_rating__isnull=False
    ).aggregate(
        avg_rating=Avg('satisfaction_rating')
    )
    
    return JsonResponse({
        'active_sessions': active_sessions,
        'avg_response_time': round(recent_analytics['avg_response_time'] or 0, 2),
        'avg_satisfaction': round(recent_satisfaction['avg_rating'] or 0, 2),
        'timestamp': timezone.now().isoformat()
    })



@staff_member_required
def export_chat_sessions(request):
    """
    Export chat sessions to CSV format.
    
    Supports filtering by:
    - Date range (start_date, end_date)
    - User type (user_type)
    - Status (is_active)
    
    Requirements: 7.4
    """
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    user_type = request.GET.get('user_type')
    is_active = request.GET.get('is_active')
    
    # Build query
    queryset = ChatSession.objects.all()
    
    if start_date:
        queryset = queryset.filter(created_at__gte=start_date)
    
    if end_date:
        queryset = queryset.filter(created_at__lte=end_date)
    
    if user_type:
        queryset = queryset.filter(user_type=user_type)
    
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active == 'true')
    
    # Select related data for efficiency
    queryset = queryset.select_related('user').prefetch_related('analytics')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="chat_sessions_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Session ID',
        'User',
        'User Type',
        'Status',
        'Created At',
        'Updated At',
        'Closed At',
        'Total Messages',
        'User Messages',
        'Assistant Messages',
        'Avg Response Time (ms)',
        'Satisfaction Rating',
        'Resolved',
        'Escalated',
        'Topics Discussed',
        'Engagement Score'
    ])
    
    # Write data rows
    for session in queryset:
        try:
            analytics = session.analytics
            total_messages = analytics.total_messages
            user_messages = analytics.user_messages
            assistant_messages = analytics.assistant_messages
            avg_response_time = analytics.average_response_time_ms
            resolved = analytics.resolved
            escalated = analytics.escalated_to_human
            topics = ', '.join(analytics.topics_discussed)
            engagement_score = analytics.engagement_score
        except ChatAnalytics.DoesNotExist:
            total_messages = 0
            user_messages = 0
            assistant_messages = 0
            avg_response_time = None
            resolved = False
            escalated = False
            topics = ''
            engagement_score = 0
        
        writer.writerow([
            str(session.session_id),
            session.user.username if session.user else 'Anonymous',
            session.user_type,
            'Active' if session.is_active else 'Closed',
            session.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            session.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            session.closed_at.strftime('%Y-%m-%d %H:%M:%S') if session.closed_at else '',
            total_messages,
            user_messages,
            assistant_messages,
            round(avg_response_time, 2) if avg_response_time else '',
            session.satisfaction_rating or '',
            'Yes' if resolved else 'No',
            'Yes' if escalated else 'No',
            topics,
            engagement_score
        ])
    
    return response


@staff_member_required
def export_chat_messages(request):
    """
    Export chat messages to CSV format.
    
    Supports filtering by:
    - Date range (start_date, end_date)
    - Session ID (session_id)
    - Sender type (sender_type)
    
    Requirements: 7.4
    """
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    session_id = request.GET.get('session_id')
    sender_type = request.GET.get('sender_type')
    
    # Build query
    queryset = ChatMessage.objects.all()
    
    if start_date:
        queryset = queryset.filter(created_at__gte=start_date)
    
    if end_date:
        queryset = queryset.filter(created_at__lte=end_date)
    
    if session_id:
        queryset = queryset.filter(session__session_id=session_id)
    
    if sender_type:
        queryset = queryset.filter(sender_type=sender_type)
    
    # Select related data for efficiency
    queryset = queryset.select_related('session', 'session__user')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="chat_messages_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Message ID',
        'Session ID',
        'User',
        'Sender Type',
        'Content',
        'Created At',
        'Processing Time (ms)',
        'Cached Response',
        'Metadata'
    ])
    
    # Write data rows
    for message in queryset:
        writer.writerow([
            str(message.message_id),
            str(message.session.session_id),
            message.session.user.username if message.session.user else 'Anonymous',
            message.sender_type,
            message.content,
            message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            message.processing_time_ms or '',
            'Yes' if message.is_cached_response else 'No',
            json.dumps(message.metadata) if message.metadata else ''
        ])
    
    return response


@staff_member_required
def export_chat_analytics(request):
    """
    Export detailed analytics data to CSV format.
    
    Supports filtering by:
    - Date range (start_date, end_date)
    - User type (user_type)
    - Resolved status (resolved)
    
    Requirements: 7.4
    """
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    user_type = request.GET.get('user_type')
    resolved = request.GET.get('resolved')
    
    # Build query
    queryset = ChatAnalytics.objects.all()
    
    if start_date:
        queryset = queryset.filter(created_at__gte=start_date)
    
    if end_date:
        queryset = queryset.filter(created_at__lte=end_date)
    
    if user_type:
        queryset = queryset.filter(session__user_type=user_type)
    
    if resolved is not None:
        queryset = queryset.filter(resolved=resolved == 'true')
    
    # Select related data for efficiency
    queryset = queryset.select_related('session', 'session__user')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="chat_analytics_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Analytics ID',
        'Session ID',
        'User',
        'User Type',
        'Total Messages',
        'User Messages',
        'Assistant Messages',
        'Avg Response Time (ms)',
        'Resolved',
        'Escalated to Human',
        'Topics Discussed',
        'Actions Taken',
        'Engagement Score',
        'Satisfaction Rating',
        'Session Created',
        'Session Duration (minutes)'
    ])
    
    # Write data rows
    for analytics in queryset:
        session = analytics.session
        
        # Calculate session duration
        if session.closed_at:
            duration = (session.closed_at - session.created_at).total_seconds() / 60
        else:
            duration = (session.updated_at - session.created_at).total_seconds() / 60
        
        writer.writerow([
            str(analytics.analytics_id),
            str(session.session_id),
            session.user.username if session.user else 'Anonymous',
            session.user_type,
            analytics.total_messages,
            analytics.user_messages,
            analytics.assistant_messages,
            round(analytics.average_response_time_ms, 2) if analytics.average_response_time_ms else '',
            'Yes' if analytics.resolved else 'No',
            'Yes' if analytics.escalated_to_human else 'No',
            ', '.join(analytics.topics_discussed),
            json.dumps(analytics.actions_taken) if analytics.actions_taken else '',
            analytics.engagement_score,
            session.satisfaction_rating or '',
            session.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            round(duration, 2)
        ])
    
    return response
