"""
Cache Middleware

Adds cache-related headers to HTTP responses to indicate cache status
and control client-side caching behavior.
"""

from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
import time


class CacheHeaderMiddleware(MiddlewareMixin):
    """
    Middleware to add cache-related headers to responses.
    
    Adds the following headers:
    - X-Cache: HIT or MISS to indicate if response came from cache
    - X-Cache-Key: The cache key used (for debugging)
    - Cache-Control: Directives for client-side caching
    """
    
    def process_request(self, request):
        """
        Store request start time for cache timing.
        """
        request._cache_start_time = time.time()
        request._cache_hit = False
        request._cache_key = None
    
    def process_response(self, request, response):
        """
        Add cache headers to the response.
        """
        # Only add headers for successful responses
        if response.status_code == 200:
            # Add X-Cache header
            if hasattr(request, '_cache_hit'):
                cache_status = 'HIT' if request._cache_hit else 'MISS'
                response['X-Cache'] = cache_status
            
            # Add X-Cache-Key header for debugging (only in DEBUG mode)
            from django.conf import settings
            if settings.DEBUG and hasattr(request, '_cache_key') and request._cache_key:
                response['X-Cache-Key'] = request._cache_key
            
            # Add Cache-Control headers based on content type and path
            if not response.has_header('Cache-Control'):
                cache_control = self._get_cache_control(request, response)
                if cache_control:
                    response['Cache-Control'] = cache_control
            
            # Add timing header for performance monitoring
            if hasattr(request, '_cache_start_time'):
                duration = time.time() - request._cache_start_time
                response['X-Response-Time'] = f"{duration:.3f}s"
        
        return response
    
    def _get_cache_control(self, request, response):
        """
        Determine appropriate Cache-Control header based on request path.
        
        Returns:
            str: Cache-Control directive or None
        """
        path = request.path
        
        # Static files - long cache
        if path.startswith('/static/') or path.startswith('/media/'):
            return 'public, max-age=2592000'  # 30 days
        
        # API endpoints - short cache with revalidation
        if path.startswith('/api/'):
            # Check if user is authenticated
            if request.user.is_authenticated:
                return 'private, max-age=300, must-revalidate'  # 5 minutes
            else:
                return 'public, max-age=900, must-revalidate'  # 15 minutes
        
        # HTML pages - no cache for authenticated users
        if request.user.is_authenticated:
            return 'private, no-cache, must-revalidate'
        
        # Public pages - short cache
        return 'public, max-age=300'  # 5 minutes


class CacheTrackingMiddleware(MiddlewareMixin):
    """
    Middleware to track cache usage and mark requests that hit cache.
    
    This should be used in conjunction with views that use the cache.
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Check if the view result might be cached.
        """
        # Store original cache get method
        if not hasattr(cache, '_original_get'):
            cache._original_get = cache.get
            
            # Wrap cache.get to track hits
            def tracked_get(key, default=None, version=None):
                value = cache._original_get(key, default, version)
                if value is not None and value != default:
                    # Cache hit
                    if hasattr(request, '_cache_hit'):
                        request._cache_hit = True
                        request._cache_key = key
                return value
            
            cache.get = tracked_get
        
        return None
