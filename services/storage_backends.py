"""
CDN Storage Backends for serving static and media files through CDN.

This module implements custom storage backends that integrate with CDN services
to optimize delivery of static assets and user-uploaded media files.

Requirements:
- 9.1: Serve all static files through CDN
- 9.2: Configure cache for images (30 days)
- 9.3: Optimize images automatically for different devices
- 9.4: Support modern formats like WebP and AVIF
"""

import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.staticfiles.storage import StaticFilesStorage
from django.utils.encoding import filepath_to_uri
from PIL import Image
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


class CDNStaticStorage(StaticFilesStorage):
    """
    Custom storage backend for serving static files through CDN.
    
    This storage backend prepends the CDN URL to static file paths when
    CDN is enabled, allowing seamless integration with CDN services.
    
    Requirement 9.1: Serve all static files through CDN
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cdn_enabled = getattr(settings, 'CDN_ENABLED', False)
        self.cdn_url = getattr(settings, 'CDN_URL', '')
        self.cdn_static_path = getattr(settings, 'CDN_STATIC_PATH', '/static/')
    
    def url(self, name):
        """
        Return the URL for accessing a static file.
        
        If CDN is enabled, returns the CDN URL. Otherwise, returns the
        standard static URL.
        
        Args:
            name: The name/path of the static file
            
        Returns:
            str: The full URL to access the file
        """
        if self.cdn_enabled and self.cdn_url:
            # Clean up the name to ensure proper path
            name = filepath_to_uri(name)
            # Construct CDN URL
            cdn_url = self.cdn_url.rstrip('/')
            static_path = self.cdn_static_path.rstrip('/')
            return f"{cdn_url}{static_path}/{name}"
        
        # Fall back to default behavior
        return super().url(name)
    
    def get_cache_control_header(self):
        """
        Get the Cache-Control header value for static files.
        
        Requirement 9.2: Configure cache for static files (30 days)
        
        Returns:
            str: Cache-Control header value
        """
        # 30 days = 2592000 seconds
        return 'public, max-age=2592000, immutable'


class CDNMediaStorage(FileSystemStorage):
    """
    Custom storage backend for serving user-uploaded media files through CDN.
    
    This storage backend handles media file uploads and serves them through
    CDN when enabled. It also provides image optimization capabilities.
    
    Requirements:
    - 9.1: Serve media files through CDN
    - 9.2: Configure cache for images (30 days)
    - 9.3: Optimize images for different devices
    - 9.4: Support WebP and AVIF formats
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cdn_enabled = getattr(settings, 'CDN_ENABLED', False)
        self.cdn_url = getattr(settings, 'CDN_URL', '')
        self.cdn_media_path = getattr(settings, 'CDN_MEDIA_PATH', '/media/')
        self.optimize_images = getattr(settings, 'CDN_OPTIMIZE_IMAGES', True)
        self.webp_enabled = getattr(settings, 'CDN_WEBP_ENABLED', True)
        self.avif_enabled = getattr(settings, 'CDN_AVIF_ENABLED', False)
    
    def url(self, name):
        """
        Return the URL for accessing a media file.
        
        If CDN is enabled, returns the CDN URL. Otherwise, returns the
        standard media URL.
        
        Args:
            name: The name/path of the media file
            
        Returns:
            str: The full URL to access the file
        """
        if self.cdn_enabled and self.cdn_url:
            # Clean up the name to ensure proper path
            name = filepath_to_uri(name)
            # Construct CDN URL
            cdn_url = self.cdn_url.rstrip('/')
            media_path = self.cdn_media_path.rstrip('/')
            return f"{cdn_url}{media_path}/{name}"
        
        # Fall back to default behavior
        return super().url(name)
    
    def _save(self, name, content):
        """
        Save a file and optionally optimize it.
        
        Requirement 9.3: Optimize images automatically
        Requirement 9.4: Support WebP and AVIF formats
        
        Args:
            name: The name to save the file as
            content: The file content
            
        Returns:
            str: The name of the saved file
        """
        # Check if this is an image file that should be optimized
        if self.optimize_images and self._is_image(name):
            try:
                content = self._optimize_image(name, content)
            except Exception as e:
                logger.warning(f"Failed to optimize image {name}: {e}")
                # Continue with original content if optimization fails
        
        # Save the file using parent class method
        return super()._save(name, content)
    
    def _is_image(self, name):
        """
        Check if a file is an image based on its extension.
        
        Args:
            name: The filename
            
        Returns:
            bool: True if the file is an image
        """
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.avif']
        ext = os.path.splitext(name)[1].lower()
        return ext in image_extensions
    
    def _optimize_image(self, name, content):
        """
        Optimize an image by compressing it and optionally converting to modern formats.
        
        Requirements:
        - 9.3: Optimize images for different devices
        - 9.4: Support WebP and AVIF formats
        
        Args:
            name: The filename
            content: The file content
            
        Returns:
            File-like object with optimized image content
        """
        try:
            # Open the image
            image = Image.open(content)
            
            # Convert RGBA to RGB if saving as JPEG
            if image.mode == 'RGBA' and name.lower().endswith(('.jpg', '.jpeg')):
                # Create a white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])  # Use alpha channel as mask
                image = background
            
            # Determine output format
            output_format = self._get_output_format(name, image)
            
            # Optimize and save
            output = BytesIO()
            
            if output_format == 'JPEG':
                # Optimize JPEG with quality setting
                image.save(output, format='JPEG', quality=85, optimize=True, progressive=True)
            elif output_format == 'PNG':
                # Optimize PNG
                image.save(output, format='PNG', optimize=True)
            elif output_format == 'WEBP':
                # Save as WebP with quality setting
                image.save(output, format='WEBP', quality=85, method=6)
            elif output_format == 'AVIF':
                # Save as AVIF (requires pillow-avif-plugin)
                image.save(output, format='AVIF', quality=85)
            else:
                # Default: save in original format
                image.save(output, format=image.format, optimize=True)
            
            output.seek(0)
            
            # Wrap in a file-like object with name attribute
            from django.core.files.base import ContentFile
            return ContentFile(output.read(), name=name)
            
        except Exception as e:
            logger.error(f"Error optimizing image {name}: {e}")
            # Reset content position and return original
            content.seek(0)
            return content
    
    def _get_output_format(self, name, image):
        """
        Determine the best output format for an image.
        
        Requirement 9.4: Support WebP and AVIF formats
        
        Args:
            name: The filename
            content: The PIL Image object
            
        Returns:
            str: The output format (JPEG, PNG, WEBP, AVIF)
        """
        ext = os.path.splitext(name)[1].lower()
        
        # If already in a modern format, keep it
        if ext == '.webp' and self.webp_enabled:
            return 'WEBP'
        if ext == '.avif' and self.avif_enabled:
            return 'AVIF'
        
        # For traditional formats, keep them as-is for compatibility
        # In production, you might want to generate multiple versions
        if ext in ['.jpg', '.jpeg']:
            return 'JPEG'
        elif ext == '.png':
            return 'PNG'
        
        # Default to original format
        return image.format or 'JPEG'
    
    def get_cache_control_header(self):
        """
        Get the Cache-Control header value for media files.
        
        Requirement 9.2: Configure cache for images (30 days)
        
        Returns:
            str: Cache-Control header value
        """
        # 30 days = 2592000 seconds
        return 'public, max-age=2592000'
    
    def generate_responsive_versions(self, name, sizes=None):
        """
        Generate multiple versions of an image for responsive design.
        
        Requirement 9.3: Optimize images for different devices
        
        Args:
            name: The original image filename
            sizes: List of (width, height) tuples for different versions
                   If None, uses default responsive sizes
            
        Returns:
            dict: Mapping of size names to file paths
        """
        if sizes is None:
            # Default responsive sizes
            sizes = {
                'thumbnail': (150, 150),
                'small': (320, 320),
                'medium': (640, 640),
                'large': (1024, 1024),
                'xlarge': (1920, 1920),
            }
        
        versions = {}
        
        try:
            # Open the original image
            with self.open(name) as content:
                image = Image.open(content)
                
                # Generate each size
                for size_name, (width, height) in sizes.items():
                    # Calculate new size maintaining aspect ratio
                    image.thumbnail((width, height), Image.Resampling.LANCZOS)
                    
                    # Generate new filename
                    base_name, ext = os.path.splitext(name)
                    new_name = f"{base_name}_{size_name}{ext}"
                    
                    # Save the resized image
                    output = BytesIO()
                    image.save(output, format=image.format, quality=85, optimize=True)
                    output.seek(0)
                    
                    # Save using storage backend
                    from django.core.files.base import ContentFile
                    saved_name = self.save(new_name, ContentFile(output.read()))
                    versions[size_name] = saved_name
                    
        except Exception as e:
            logger.error(f"Error generating responsive versions for {name}: {e}")
        
        return versions
