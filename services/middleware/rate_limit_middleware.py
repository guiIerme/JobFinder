"""
Rate Limiting Middleware

Implements rate limiting to protect the API from abuse and ensure
fair usage across all users. Tracks requests per user/IP and enforces
configurable limits.
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
import time
from datetime import datetime, timedelta


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware to enforce rate limiting on API requests.
    
    Rate limits:
    - Anonymous users: 100 requests per hour
    - Authenticated users: 1000 requests per hour
    - Premium users: 5000 requests per hour
    
    Uses cache to track request counts per user/IP within time windows.
    """
    
    # Rate limit configurations (requests per hour)
    LIMITS = {
        'anonymous': 100,
        'authenticated': 1000,
        'premium': 5000,
    }
    
    # Time window in seconds (1 hour)
    WINDOW_SIZE = 3600
    
    # Paths that should be excluded from rate limiting
    EXCLUDED_PATHS = [
        '/admin/',
        '/static/',
        '/media/',
        '/health/',
    ]
    
    def process_request(self, request):
        """
        Check rate limit before processing the request.
        
        Returns:
            JsonResponse with 429 status if limit exceeded, None otherwise
        """
        # Skip rate limiting for excluded paths
        if self._is_excluded_path(request.path):
            return None
        
        # Get identifier (user_id or IP)
        identifier = self._get_identifier(request)
        
        # Get rate limit for this user type
        limit = self._get_limit(request)
        
        # Get current request count
        cache_key = f'rate_limit:{identifier}'
        request_data = cache.get(cache_key)
        
        current_time = time.time()
        
        if request_data is None:
            # First request in this window
            request_data = {
                'count': 1,
                'window_start': current_time,
                'window_end': current_time + self.WINDOW_SIZE
            }
            cache.set(cache_key, request_data, self.WINDOW_SIZE)
            
            # Log to database
            self._log_rate_limit(identifier, request.path, 1, limit, current_time, False)
        else:
            # Check if window has expired
            if current_time >= request_data['window_end']:
                # Reset window
                request_data = {
                    'count': 1,
                    'window_start': current_time,
                    'window_end': current_time + self.WINDOW_SIZE
                }
                cache.set(cache_key, request_data, self.WINDOW_SIZE)
                
                # Log to database
                self._log_rate_limit(identifier, request.path, 1, limit, current_time, False)
            else:
                # Increment count
                request_data['count'] += 1
                
                # Check if limit exceeded
                if request_data['count'] > limit:
                    # Calculate time until reset
                    reset_time = request_data['window_end']
                    wait_time = int(reset_time - current_time)
                    
                    # Log violation to database
                    self._log_rate_limit(
                        identifier, 
                        request.path, 
                        request_data['count'], 
                        limit, 
                        request_data['window_start'], 
                        True
                    )
                    
                    # Return 429 Too Many Requests
                    response = JsonResponse({
                        'error': {
                            'code': 'RATE_LIMIT_EXCEEDED',
                            'message': 'Too many requests. Please try again later.',
                            'details': {
                                'limit': limit,
                                'remaining': 0,
                                'reset_at': datetime.fromtimestamp(reset_time).isoformat(),
                                'retry_after': wait_time
                            }
                        }
                    }, status=429)
                    
                    # Add rate limit headers
                    response['X-RateLimit-Limit'] = str(limit)
                    response['X-RateLimit-Remaining'] = '0'
                    response['X-RateLimit-Reset'] = str(int(reset_time))
                    response['Retry-After'] = str(wait_time)
                    
                    return response
                
                # Update cache with new count
                remaining_ttl = int(request_data['window_end'] - current_time)
                cache.set(cache_key, request_data, remaining_ttl)
        
        # Store rate limit info in request for use in response headers
        request._rate_limit_info = {
            'limit': limit,
            'remaining': limit - request_data['count'],
            'reset': request_data['window_end']
        }
        
        return None
    
    def process_response(self, request, response):
        """
        Add rate limit headers to the response.
        """
        # Add rate limit headers if info is available
        if hasattr(request, '_rate_limit_info'):
            info = request._rate_limit_info
            response['X-RateLimit-Limit'] = str(info['limit'])
            response['X-RateLimit-Remaining'] = str(max(0, info['remaining']))
            response['X-RateLimit-Reset'] = str(int(info['reset']))
        
        return response
    
    def _get_identifier(self, request):
        """
        Get unique identifier for rate limiting.
        
        Uses user_id for authenticated users, IP address for anonymous users.
        
        Args:
            request: Django request object
            
        Returns:
            str: Unique identifier
        """
        if request.user.is_authenticated:
            return f'user:{request.user.id}'
        else:
            # Get IP address from request
            ip = self._get_client_ip(request)
            return f'ip:{ip}'
    
    def _get_client_ip(self, request):
        """
        Get client IP address from request.
        
        Handles proxy headers like X-Forwarded-For.
        
        Args:
            request: Django request object
            
        Returns:
            str: Client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _get_limit(self, request):
        """
        Get rate limit for the current user type.
        
        Args:
            request: Django request object
            
        Returns:
            int: Request limit per hour
        """
        if request.user.is_authenticated:
            # Check if user is premium
            if hasattr(request.user, 'userprofile') and request.user.userprofile.is_premium:
                return self.LIMITS['premium']
            return self.LIMITS['authenticated']
        return self.LIMITS['anonymous']
    
    def _is_excluded_path(self, path):
        """
        Check if path should be excluded from rate limiting.
        
        Args:
            path: Request path
            
        Returns:
            bool: True if path should be excluded
        """
        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded):
                return True
        return False
    
    def _log_rate_limit(self, identifier, endpoint, count, limit, window_start, exceeded):
        """
        Log rate limit record to database for monitoring.
        
        Args:
            identifier: User ID or IP address
            endpoint: Request endpoint
            count: Number of requests in window
            limit: Rate limit for this identifier
            window_start: Start time of the window
            exceeded: Whether limit was exceeded
        """
        try:
            from services.models import RateLimitRecord
            from django.utils import timezone
            
            window_start_dt = datetime.fromtimestamp(window_start)
            window_end_dt = datetime.fromtimestamp(window_start + self.WINDOW_SIZE)
            
            # Use get_or_create to avoid duplicates
            RateLimitRecord.objects.update_or_create(
                identifier=identifier,
                endpoint=endpoint,
                window_start=window_start_dt,
                defaults={
                    'request_count': count,
                    'limit': limit,
                    'window_end': window_end_dt,
                    'exceeded': exceeded,
                }
            )
        except Exception as e:
            # Don't let logging errors break the request
            # In production, you might want to log this error
            pass
