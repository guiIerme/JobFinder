"""
Middleware for mobile optimization.

Adds device detection and optimization hints to API responses.
"""
from services.api.mobile_image_utils import get_device_context


class MobileOptimizationMiddleware:
    """
    Middleware that detects mobile devices and adds optimization headers.
    
    This middleware:
    - Detects device type from User-Agent
    - Adds X-Device-Type header to responses
    - Adds X-Image-Lazy-Load hint for mobile devices
    - Provides device context to views via request
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add device context to request for use in views
        request.device_context = get_device_context(request)
        
        # Process the request
        response = self.get_response(request)
        
        # Add device detection headers to API responses
        if request.path.startswith('/api/'):
            device_context = request.device_context
            response['X-Device-Type'] = device_context['device_type']
            
            # Add lazy loading hint for mobile devices
            if device_context['lazy_load']:
                response['X-Image-Lazy-Load'] = 'recommended'
            
            # Add optimization hints
            if device_context['is_mobile']:
                response['X-Optimization-Hint'] = 'Use ?compact=true for minimal payload'
        
        return response
