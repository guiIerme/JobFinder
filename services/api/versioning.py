"""
API Versioning Middleware and Utilities

This module implements API versioning support through URL paths and headers.
Supports version specification via:
- URL path: /api/v1/...
- Accept-Version header: Accept-Version: v1

Requirements: 12.1, 12.5
"""
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from datetime import datetime, timedelta
import re
import json


class APIVersionMiddleware(MiddlewareMixin):
    """
    Middleware to handle API versioning and deprecation warnings.
    
    Extracts version from URL path or Accept-Version header and adds
    version information to the request object.
    """
    
    # Supported API versions
    SUPPORTED_VERSIONS = ['v1']
    DEFAULT_VERSION = 'v1'
    
    # Version pattern in URL
    VERSION_PATTERN = re.compile(r'/api/(v\d+)/')
    
    def process_request(self, request):
        """
        Extract API version from request and validate it.
        """
        # Skip non-API requests
        if not request.path.startswith('/api/'):
            return None
        
        # Extract version from URL
        version = self._extract_version_from_url(request.path)
        
        # If not in URL, check Accept-Version header
        if not version:
            version = request.META.get('HTTP_ACCEPT_VERSION', '').strip()
            if version and not version.startswith('v'):
                version = f'v{version}'
        
        # Use default version if none specified
        if not version:
            version = self.DEFAULT_VERSION
        
        # Validate version
        if version not in self.SUPPORTED_VERSIONS:
            return JsonResponse({
                'error': {
                    'code': 'UNSUPPORTED_API_VERSION',
                    'message': f'API version {version} is not supported.',
                    'details': {
                        'requested_version': version,
                        'supported_versions': self.SUPPORTED_VERSIONS
                    }
                }
            }, status=400)
        
        # Store version in request
        request.api_version = version
        
        return None
    
    def process_response(self, request, response):
        """
        Add version information and deprecation warnings to response headers.
        Requirements: 12.2, 12.4
        """
        # Skip non-API requests
        if not hasattr(request, 'api_version'):
            return response
        
        # Add API version header
        response['X-API-Version'] = request.api_version
        
        # Check for deprecation using DeprecationManager
        try:
            from .deprecation import DeprecationManager
            
            warning = DeprecationManager.get_deprecation_warning(request.api_version)
            
            if warning:
                # Add deprecation headers
                response['X-API-Deprecated'] = 'true'
                response['X-API-Deprecation-Date'] = warning['deprecation_date']
                response['X-API-Deprecation-Info'] = warning['message']
                
                # Add warning to response body if JSON
                if response.get('Content-Type', '').startswith('application/json'):
                    try:
                        data = json.loads(response.content)
                        if isinstance(data, dict):
                            data['_deprecation_warning'] = warning
                            response.content = json.dumps(data).encode('utf-8')
                    except (json.JSONDecodeError, ValueError):
                        pass
        except ImportError:
            # DeprecationManager not available, skip deprecation checks
            pass
        
        return response
    
    def _extract_version_from_url(self, path):
        """
        Extract version from URL path.
        
        Args:
            path: URL path string
            
        Returns:
            Version string (e.g., 'v1') or None
        """
        match = self.VERSION_PATTERN.search(path)
        if match:
            return match.group(1)
        return None


class VersionedAPIView:
    """
    Mixin for API views that need version-specific behavior.
    
    Usage:
        class MyAPIView(VersionedAPIView, APIView):
            def get_v1(self, request):
                # v1 implementation
                pass
            
            def get_v2(self, request):
                # v2 implementation
                pass
    """
    
    def dispatch(self, request, *args, **kwargs):
        """
        Route to version-specific method if available.
        """
        # Get the HTTP method and version
        method = request.method.lower()
        version = getattr(request, 'api_version', 'v1')
        
        # Try to find version-specific handler
        handler_name = f'{method}_{version}'
        handler = getattr(self, handler_name, None)
        
        # Fall back to default handler if version-specific not found
        if not handler:
            handler = getattr(self, method, None)
        
        if handler:
            return handler(request, *args, **kwargs)
        
        return super().dispatch(request, *args, **kwargs)


def get_api_version(request):
    """
    Utility function to get the API version from a request.
    
    Args:
        request: Django request object
        
    Returns:
        Version string (e.g., 'v1')
    """
    return getattr(request, 'api_version', APIVersionMiddleware.DEFAULT_VERSION)


def is_version_deprecated(version):
    """
    Check if an API version is deprecated.
    
    Args:
        version: Version string (e.g., 'v1')
        
    Returns:
        Boolean indicating if version is deprecated
    """
    try:
        from .deprecation import DeprecationManager
        return DeprecationManager.is_deprecated(version)
    except ImportError:
        return False


def get_version_eol_date(version):
    """
    Get the end-of-life date for a deprecated API version.
    
    Args:
        version: Version string (e.g., 'v1')
        
    Returns:
        datetime object or None if not deprecated
    """
    try:
        from .deprecation import DeprecationManager
        return DeprecationManager.get_version_eol_date(version)
    except ImportError:
        return None
