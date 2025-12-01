"""
Views for rate limit monitoring and management.

Provides dashboard and API endpoints for monitoring rate limit usage,
identifying potential abuse, and viewing statistics.
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Avg, Max, Q
from datetime import timedelta
from services.models import RateLimitRecord


@staff_member_required
def rate_limit_dashboard(request):
    """
    Dashboard view for monitoring rate limits.
    
    Shows:
    - Current rate limit violations
    - Top offenders
    - Endpoint statistics
    - Historical trends
    """
    # Get time range from query params (default: last 24 hours)
    hours = int(request.GET.get('hours', 24))
    cutoff_time = timezone.now() - timedelta(hours=hours)
    
    # Get overall statistics
    total_records = RateLimitRecord.objects.filter(created_at__gte=cutoff_time).count()
    total_violations = RateLimitRecord.objects.filter(
        created_at__gte=cutoff_time,
        exceeded=True
    ).count()
    
    violation_rate = (total_violations / total_records * 100) if total_records > 0 else 0
    
    # Get top offenders
    top_offenders = RateLimitRecord.get_top_offenders(limit=10, hours=hours)
    
    # Get endpoint statistics
    endpoint_stats = RateLimitRecord.get_endpoint_stats(hours=hours)
    
    # Get recent violations
    recent_violations = (RateLimitRecord.objects
                        .filter(exceeded=True, created_at__gte=cutoff_time)
                        .order_by('-created_at')[:20])
    
    context = {
        'hours': hours,
        'total_records': total_records,
        'total_violations': total_violations,
        'violation_rate': round(violation_rate, 2),
        'top_offenders': top_offenders,
        'endpoint_stats': endpoint_stats,
        'recent_violations': recent_violations,
    }
    
    return render(request, 'services/rate_limit_dashboard.html', context)


@staff_member_required
def rate_limit_stats_api(request):
    """
    API endpoint for rate limit statistics.
    
    Returns JSON data for charts and monitoring tools.
    """
    hours = int(request.GET.get('hours', 24))
    cutoff_time = timezone.now() - timedelta(hours=hours)
    
    # Get hourly breakdown
    hourly_stats = []
    for i in range(hours):
        hour_start = timezone.now() - timedelta(hours=i+1)
        hour_end = timezone.now() - timedelta(hours=i)
        
        hour_records = RateLimitRecord.objects.filter(
            created_at__gte=hour_start,
            created_at__lt=hour_end
        )
        
        hourly_stats.append({
            'hour': hour_start.strftime('%Y-%m-%d %H:00'),
            'total': hour_records.count(),
            'violations': hour_records.filter(exceeded=True).count(),
        })
    
    # Get top offenders
    top_offenders = list(RateLimitRecord.get_top_offenders(limit=10, hours=hours))
    
    # Get endpoint stats
    endpoint_stats = list(RateLimitRecord.get_endpoint_stats(hours=hours))
    
    return JsonResponse({
        'hourly_stats': hourly_stats,
        'top_offenders': top_offenders,
        'endpoint_stats': endpoint_stats,
    })


@staff_member_required
def rate_limit_cleanup(request):
    """
    Trigger manual cleanup of old rate limit records.
    
    POST endpoint that deletes records older than specified days.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    days = int(request.POST.get('days', 7))
    
    # Perform cleanup
    deleted_count = RateLimitRecord.cleanup_old_records(days=days)
    
    return JsonResponse({
        'success': True,
        'deleted_count': deleted_count,
        'message': f'Successfully deleted {deleted_count} records older than {days} days'
    })
