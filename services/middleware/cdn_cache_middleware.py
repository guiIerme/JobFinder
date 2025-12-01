"""
CDN Cache Middleware for optimizing cache headers and ETags.

This middleware adds appropriate cache headers for static and media files
to optimize CDN caching and reduce bandwidth usage.

Requirements:
- 9.2: Configure cache for static files (30 days)
- 9.5: Implement cache invalidation when necessary
"""

import hashlib
from django.utils.cache import patch_cache_control, get_max_age
from django.http import HttpResponseNotModified
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class CDNCacheMiddleware:
    """
    Middleware to add CDN-optimized cache headers to responses.
    
    This middleware:
    - Adds Cache-Control headers for static and media files
    - Generates and validates ETags for cache validation
    - Handles conditional requests (If-None-Match)
    - Supports cache invalidation
    
    Requirements:
    - 9.2: Configure cache for static files (30 days)
    - 9.5: Implement ETag validation and cache invalidation
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.cdn_enabled = getattr(settings, 'CDN_ENABLED', False)
        
        # Cache durations in seconds
        self.static_cache_duration = 60 * 60 * 24 * 30  # 30 days
        self.media_cache_duration = 60 * 60 * 24 * 30   # 30 days
        self.html_cache_duration = 60 * 5               # 5 minutes
        
    def __call__(self, request):
        """Process the request and add cache headers to the response."""
        
        # Get the response
        response = self.get_response(request)
        
        # Only process successful responses
        if response.status_code != 200:
            return response
        
        # Determine if this is a static or media file
        path = request.path
        is_static = self._is_static_file(path)
        is_media = self._is_media_file(path)
        
        if is_static or is_media:
            # Add cache headers for static/media files
            self._add_cache_headers(response, is_static, is_media)
            
            # Generate and add ETag
            etag = self._generate_etag(response)
            if etag:
                response['ETag'] = etag
                
                # Check if client has cached version
                if self._check_etag(request, etag):
                    return HttpResponseNotModified()
        
        elif self._is_html_response(response):
            # Add shorter cache for HTML pages
            self._add_html_cache_headers(response)
        
        return response
    
    def _is_static_file(self, path):
        """
        Check if the request path is for a static file.
        
        Args:
            path: Request path
            
        Returns:
            bool: True if this is a static file request
        """
        static_url = getattr(settings, 'STATIC_URL', '/static/')
        return path.startswith(static_url)
    
    def _is_media_file(self, path):
        """
        Check if the request path is for a media file.
        
        Args:
            path: Request path
            
        Returns:
            bool: True if this is a media file request
        """
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        return path.startswith(media_url)
    
    def _is_html_response(self, response):
        """
        Check if the response is HTML content.
        
        Args:
            response: Django response object
            
        Returns:
            bool: True if this is an HTML response
        """
        content_type = response.get('Content-Type', '')
        return 'text/html' in content_type
    
    def _add_cache_headers(self, response, is_static, is_media):
        """
        Add cache headers for static and media files.
        
        Requirement 9.2: Configure cache for static files (30 days)
        
        Args:
            response: Django response object
            is_static: Whether this is a static file
            is_media: Whether this is a media file
        """
        if is_static:
            # Static files: long cache with immutable flag
            # Requirement 9.2: 30 days cache for static files
            patch_cache_control(
                response,
                public=True,
                max_age=self.static_cache_duration,
                immutable=True
            )
            
            # Add additional headers for CDN
            response['X-Cache-Type'] = 'static'
            
        elif is_media:
            # Media files: long cache but not immutable (can be updated)
            # Requirement 9.2: 30 days cache for media files
            patch_cache_control(
                response,
                public=True,
                max_age=self.media_cache_duration
            )
            
            # Add additional headers for CDN
            response['X-Cache-Type'] = 'media'
        
        # Add Vary header to handle different encodings
        response['Vary'] = 'Accept-Encoding'
    
    def _add_html_cache_headers(self, response):
        """
        Add cache headers for HTML pages.
        
        HTML pages get shorter cache durations and must revalidate.
        
        Args:
            response: Django response object
        """
        patch_cache_control(
            response,
            public=True,
            max_age=self.html_cache_duration,
            must_revalidate=True
        )
        
        response['X-Cache-Type'] = 'html'
    
    def _generate_etag(self, response):
        """
        Generate an ETag for the response content.
        
        Requirement 9.5: Configure ETags for validation
        
        Args:
            response: Django response object
            
        Returns:
            str: ETag value or None
        """
        try:
            # Generate ETag from response content
            if hasattr(response, 'content'):
                content_hash = hashlib.md5(response.content).hexdigest()
                return f'"{content_hash}"'
        except Exception as e:
            logger.warning(f"Failed to generate ETag: {e}")
        
        return None
    
    def _check_etag(self, request, etag):
        """
        Check if the client's cached version matches the current ETag.
        
        Requirement 9.5: ETag validation for cache
        
        Args:
            request: Django request object
            etag: Current ETag value
            
        Returns:
            bool: True if client has valid cached version
        """
        # Get the If-None-Match header from the request
        if_none_match = request.META.get('HTTP_IF_NONE_MATCH')
        
        if if_none_match:
            # Check if any of the ETags match
            client_etags = [tag.strip() for tag in if_none_match.split(',')]
            return etag in client_etags
        
        return False


class CacheInvalidationMiddleware:
    """
    Middleware to handle cache invalidation for CDN.
    
    This middleware adds headers to trigger cache invalidation when
    content is updated.
    
    Requirement 9.5: Implement cache invalidation when necessary
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        """Process the request and handle cache invalidation."""
        
        response = self.get_response(request)
        
        # Check if this is a modification request
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Add cache invalidation headers
            self._add_invalidation_headers(response, request)
        
        return response
    
    def _add_invalidation_headers(self, response, request):
        """
        Add headers to trigger cache invalidation.
        
        Requirement 9.5: Cache invalidation when necessary
        
        Args:
            response: Django response object
            request: Django request object
        """
        # Add header to indicate cache should be invalidated
        response['X-Cache-Invalidate'] = 'true'
        
        # Add timestamp for cache invalidation tracking
        from django.utils import timezone
        response['X-Cache-Invalidate-Time'] = timezone.now().isoformat()
        
        # Prevent caching of the response itself
        patch_cache_control(
            response,
            no_cache=True,
            no_store=True,
            must_revalidate=True
        )


class CDNPerformanceMiddleware:
    """
    Middleware to track and optimize CDN performance.
    
    This middleware measures the impact of CDN caching on page load times
    and provides metrics for optimization.
    
    Requirement 9.5: Validate reduction of loading time > 70%
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.cdn_enabled = getattr(settings, 'CDN_ENABLED', False)
    
    def __call__(self, request):
        """Process the request and track performance metrics."""
        
        import time
        
        # Record start time
        start_time = time.time()
        
        # Get the response
        response = self.get_response(request)
        
        # Calculate response time
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Add performance headers
        response['X-Response-Time'] = f"{response_time:.2f}ms"
        
        if self.cdn_enabled:
            response['X-CDN-Enabled'] = 'true'
            
            # Check if response was served from cache
            if response.get('X-Cache-Type'):
                response['X-CDN-Cache-Type'] = response['X-Cache-Type']
        
        # Log performance metrics for analysis
        if self._should_log_performance(request):
            self._log_performance(request, response, response_time)
        
        return response
    
    def _should_log_performance(self, request):
        """
        Determine if performance should be logged for this request.
        
        Args:
            request: Django request object
            
        Returns:
            bool: True if performance should be logged
        """
        # Log static and media file requests
        path = request.path
        static_url = getattr(settings, 'STATIC_URL', '/static/')
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        
        return path.startswith(static_url) or path.startswith(media_url)
    
    def _log_performance(self, request, response, response_time):
        """
        Log performance metrics for analysis.
        
        Args:
            request: Django request object
            response: Django response object
            response_time: Response time in milliseconds
        """
        logger.info(
            f"CDN Performance - Path: {request.path}, "
            f"Time: {response_time:.2f}ms, "
            f"Size: {len(response.content) if hasattr(response, 'content') else 0} bytes, "
            f"Cache-Type: {response.get('X-Cache-Type', 'none')}"
        )
