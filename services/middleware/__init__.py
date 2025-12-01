"""
Middleware package for services app.
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.views import redirect_to_login

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Pages that don't require login
        exempt_urls = [
            '/admin/',
            '/admin/login/',
            '/static/',
            '/media/',
            '/api/',  # Exempt all API endpoints (they handle their own auth)
        ]
        
        # Named URLs that don't require login
        exempt_url_names = [
            'login',
            'logout',
            'register',
        ]
        
        # Check if the path is exempt
        is_exempt = False
        for url in exempt_urls:
            if request.path.startswith(url):
                is_exempt = True
                break
        
        # Check if the URL name is exempt
        try:
            current_url_name = request.resolver_match.url_name if request.resolver_match else None
            if current_url_name in exempt_url_names:
                is_exempt = True
        except:
            pass
        
        # Special case for register - now accessible to everyone
        if request.path == '/register/':
            # Allow access to registration page for all users
            is_exempt = True
        
        # If user is not authenticated and trying to access a protected page
        if not request.user.is_authenticated and not is_exempt:
            # Don't redirect for admin pages (Django handles that)
            if not request.path.startswith('/admin/'):
                # Prevent redirect loops by checking if we're already going to login
                login_url = reverse(settings.LOGIN_URL) if hasattr(settings, 'LOGIN_URL') else '/accounts/login/'
                if request.path == login_url:
                    is_exempt = True
                else:
                    return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)
        
        # If user is authenticated and trying to access login page, redirect to home
        if request.user.is_authenticated and request.resolver_match and request.resolver_match.url_name == 'login':
            return redirect(settings.LOGIN_REDIRECT_URL if hasattr(settings, 'LOGIN_REDIRECT_URL') else '/')
        
        response = self.get_response(request)
        return response

from .metrics_middleware import MetricsMiddleware

__all__ = ['LoginRequiredMiddleware', 'MetricsMiddleware']
