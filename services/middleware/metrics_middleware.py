"""
Middleware for collecting API performance metrics.

This middleware records response times, status codes, and other metrics
for each request to enable performance monitoring and analytics.
"""

import time
from django.utils.deprecation import MiddlewareMixin
from services.models import APIMetric


class MetricsMiddleware(MiddlewareMixin):
    """
    Middleware to collect API performance metrics.
    
    Records:
    - Response time in milliseconds
    - HTTP status code
    - Endpoint path
    - HTTP method
    - User information (if authenticated)
    - IP address
    - User agent
    """
    
    def process_request(self, request):
        """Store the start time of the request"""
        request._metrics_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Record metrics after the response is generated"""
        # Only record metrics if we have a start time
        if not hasattr(request, '_metrics_start_time'):
            return response
        
        # Calculate response time in milliseconds
        response_time = (time.time() - request._metrics_start_time) * 1000
        
        # Get user information
        user = request.user if request.user.is_authenticated else None
        
        # Get IP address
        ip_address = self._get_client_ip(request)
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Get endpoint path
        endpoint = request.path
        
        # Get HTTP method
        method = request.method
        
        # Get status code
        status_code = response.status_code
        
        # Record the metric asynchronously to avoid slowing down the response
        try:
            APIMetric.objects.create(
                endpoint=endpoint,
                method=method,
                response_time=round(response_time, 2),
                status_code=status_code,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent[:500]  # Limit user agent length
            )
        except Exception as e:
            # Log the error but don't fail the request
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to record API metric: {e}")
        
        return response
    
    def _get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        
        Checks X-Forwarded-For header first (for proxied requests),
        then falls back to REMOTE_ADDR.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip
