from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import PageView, UserAction

@csrf_exempt
@require_http_methods(["POST"])
def track_page_view(request):
    """Track a page view"""
    try:
        data = json.loads(request.body)
        path = data.get('path', '')
        referrer = data.get('referrer', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = get_client_ip(request)
        
        # Get session key if available
        session_key = request.session.session_key or ''
        
        # Create page view record
        PageView.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=session_key,
            ip_address=ip_address,
            user_agent=user_agent,
            path=path,
            referrer=referrer
        )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def track_user_action(request):
    """Track a user action"""
    try:
        data = json.loads(request.body)
        action_type = data.get('action_type', '')
        element_id = data.get('element_id', '')
        page_path = data.get('page_path', '')
        additional_data = data.get('additional_data', {})
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = get_client_ip(request)
        
        # Get session key if available
        session_key = request.session.session_key or ''
        
        # Create user action record
        UserAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=session_key,
            ip_address=ip_address,
            user_agent=user_agent,
            action_type=action_type,
            element_id=element_id,
            page_path=page_path,
            additional_data=additional_data
        )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip