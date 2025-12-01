"""
Compression middleware for HTTP responses.
Supports both Gzip and Brotli compression algorithms.
"""
import re
from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin


class BrotliMiddleware(MiddlewareMixin):
    """
    Middleware that compresses responses using Brotli compression when supported by the client.
    Falls back to gzip if brotli is not available or not supported by client.
    
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        
        # Load configuration from settings
        # Requirement 5.3: Define minimum size for compression (1KB)
        self.min_compression_size = getattr(settings, 'MIN_COMPRESSION_SIZE', 1024)
        
        # Requirement 5.2: Brotli compression level
        self.brotli_compression_level = getattr(settings, 'BROTLI_COMPRESSION_LEVEL', 5)
        
        # Requirement 5.5: Compress only specific MIME types
        compressible_types = getattr(settings, 'COMPRESSIBLE_MIME_TYPES', [
            'text/html',
            'text/css',
            'text/plain',
            'text/xml',
            'text/javascript',
            'application/json',
            'application/javascript',
            'application/xml',
            'application/xhtml+xml',
            'application/rss+xml',
            'application/atom+xml',
            'image/svg+xml',
        ])
        
        # Requirement 5.4: Minimum compression ratio
        self.min_compression_ratio = getattr(settings, 'MIN_COMPRESSION_RATIO', 60)
        
        # Regex to match compressible content types
        self.compressible_types_re = re.compile(
            r'^(' + '|'.join(re.escape(ct) for ct in compressible_types) + r')($|;)',
            re.IGNORECASE
        )
        
        # Try to import brotli
        try:
            import brotli
            self.brotli = brotli
            self.brotli_available = True
        except ImportError:
            self.brotli = None
            self.brotli_available = False
    
    def process_response(self, request, response):
        """
        Process the response and apply compression if appropriate.
        
        Requirements:
        - 5.1: Compress responses larger than 1KB using gzip
        - 5.2: Use brotli when client supports it
        - 5.3: Add Content-Encoding header
        - 5.4: Validate compression ratio > 60%
        - 5.5: Compress only specific MIME types
        """
        # Don't compress if already compressed
        # Requirement 5.3: Content-Encoding header check
        if response.has_header('Content-Encoding'):
            return response
        
        # Don't compress streaming responses
        if response.streaming:
            return response
        
        # Requirement 5.1 & 5.3: Don't compress if response is too small (< 1KB)
        if not response.content or len(response.content) < self.min_compression_size:
            return response
        
        # Requirement 5.5: Check if content type is compressible
        content_type = response.get('Content-Type', '')
        if not self.compressible_types_re.match(content_type):
            return response
        
        # Get accepted encodings from request
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '').lower()
        
        # Requirement 5.2: Try Brotli first if available and supported by client
        if self.brotli_available and 'br' in accept_encoding:
            original_length = len(response.content)
            compressed_content = self._compress_brotli(response.content)
            
            if compressed_content:
                response.content = compressed_content
                # Requirement 5.3: Add Content-Encoding header
                response['Content-Encoding'] = 'br'
                response['Content-Length'] = len(compressed_content)
                
                # Store original length for stats
                response._original_content_length = original_length
                
                # Add Vary header to indicate response varies by Accept-Encoding
                patch_vary_headers(response, ('Accept-Encoding',))
                
                return response
        
        # If brotli not available or not supported, let GZipMiddleware handle it
        return response
    
    def _compress_brotli(self, content):
        """
        Compress content using Brotli algorithm.
        Returns compressed content or None if compression fails.
        
        Requirement 5.4: Validate compression ratio > 60%
        """
        try:
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            # Requirement 5.2: Use configured brotli compression level
            compressed = self.brotli.compress(
                content,
                quality=self.brotli_compression_level
            )
            
            # Requirement 5.4: Only return compressed content if compression ratio >= 60%
            compression_ratio = (1 - len(compressed) / len(content)) * 100
            if compression_ratio >= self.min_compression_ratio:
                return compressed
            
            return None
        except Exception:
            # If compression fails, return None to fall back to uncompressed
            return None


class CompressionStatsMiddleware(MiddlewareMixin):
    """
    Middleware to track compression statistics.
    Adds headers with compression information for monitoring.
    """
    
    def process_response(self, request, response):
        """
        Add compression statistics to response headers for monitoring.
        """
        # Only add stats if response was compressed
        if response.has_header('Content-Encoding'):
            encoding = response.get('Content-Encoding')
            content_length = response.get('Content-Length', 0)
            
            # Add custom header with compression info (for debugging/monitoring)
            if hasattr(response, '_original_content_length'):
                original_length = response._original_content_length
                compressed_length = int(content_length)
                
                if original_length > 0:
                    ratio = (1 - compressed_length / original_length) * 100
                    response['X-Compression-Ratio'] = f'{ratio:.1f}%'
                    response['X-Compression-Algorithm'] = encoding
        
        return response
