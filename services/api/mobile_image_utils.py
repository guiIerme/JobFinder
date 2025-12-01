"""
Utilities for mobile image optimization.

Provides functions to detect mobile devices and serve appropriately
sized images to reduce bandwidth usage and improve load times.
"""
import re
from django.conf import settings


class MobileDeviceDetector:
    """
    Detects mobile devices from User-Agent header.
    """
    
    # Common mobile device patterns
    MOBILE_PATTERNS = [
        r'Android',
        r'iPhone',
        r'iPad',
        r'iPod',
        r'BlackBerry',
        r'Windows Phone',
        r'Mobile',
        r'webOS',
        r'Opera Mini',
        r'IEMobile',
    ]
    
    # Tablet patterns (considered mobile but may need different sizing)
    TABLET_PATTERNS = [
        r'iPad',
        r'Android.*Tablet',
        r'Kindle',
        r'Silk',
        r'PlayBook',
    ]
    
    @classmethod
    def is_mobile(cls, user_agent):
        """
        Check if the user agent indicates a mobile device.
        
        Args:
            user_agent (str): User-Agent header string
            
        Returns:
            bool: True if mobile device detected
        """
        if not user_agent:
            return False
        
        for pattern in cls.MOBILE_PATTERNS:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return True
        
        return False
    
    @classmethod
    def is_tablet(cls, user_agent):
        """
        Check if the user agent indicates a tablet device.
        
        Args:
            user_agent (str): User-Agent header string
            
        Returns:
            bool: True if tablet device detected
        """
        if not user_agent:
            return False
        
        for pattern in cls.TABLET_PATTERNS:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return True
        
        return False
    
    @classmethod
    def get_device_type(cls, user_agent):
        """
        Determine the device type from user agent.
        
        Args:
            user_agent (str): User-Agent header string
            
        Returns:
            str: 'mobile', 'tablet', or 'desktop'
        """
        if cls.is_tablet(user_agent):
            return 'tablet'
        elif cls.is_mobile(user_agent):
            return 'mobile'
        else:
            return 'desktop'


class ImageOptimizer:
    """
    Provides image optimization utilities for mobile devices.
    """
    
    # Image size configurations for different device types
    IMAGE_SIZES = {
        'mobile': {
            'avatar': (150, 150),
            'thumbnail': (300, 300),
            'medium': (600, 600),
            'large': (1024, 1024),
        },
        'tablet': {
            'avatar': (200, 200),
            'thumbnail': (400, 400),
            'medium': (800, 800),
            'large': (1280, 1280),
        },
        'desktop': {
            'avatar': (300, 300),
            'thumbnail': (600, 600),
            'medium': (1200, 1200),
            'large': (1920, 1920),
        },
    }
    
    @classmethod
    def get_optimized_image_url(cls, image_field, device_type='desktop', size='medium'):
        """
        Get optimized image URL based on device type.
        
        In a production environment, this would integrate with an image
        processing service or CDN to serve appropriately sized images.
        For now, it returns the original image URL with query parameters
        that could be used by a CDN or image proxy.
        
        Args:
            image_field: Django ImageField instance
            device_type (str): 'mobile', 'tablet', or 'desktop'
            size (str): 'avatar', 'thumbnail', 'medium', or 'large'
            
        Returns:
            str: Optimized image URL or None if no image
        """
        if not image_field:
            return None
        
        # Get the base URL
        try:
            base_url = image_field.url
        except (ValueError, AttributeError):
            return None
        
        # Get target dimensions
        dimensions = cls.IMAGE_SIZES.get(device_type, {}).get(size)
        if not dimensions:
            return base_url
        
        width, height = dimensions
        
        # In production, this would be handled by CDN or image service
        # For now, add query parameters that could be used by image proxy
        if '?' in base_url:
            return f"{base_url}&w={width}&h={height}&fit=cover"
        else:
            return f"{base_url}?w={width}&h={height}&fit=cover"
    
    @classmethod
    def should_lazy_load(cls, device_type):
        """
        Determine if images should be lazy loaded for this device type.
        
        Args:
            device_type (str): 'mobile', 'tablet', or 'desktop'
            
        Returns:
            bool: True if lazy loading is recommended
        """
        # Recommend lazy loading for mobile devices to save bandwidth
        return device_type in ['mobile', 'tablet']


def get_device_context(request):
    """
    Extract device information from request.
    
    Args:
        request: Django request object
        
    Returns:
        dict: Device context with type and optimization flags
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    device_type = MobileDeviceDetector.get_device_type(user_agent)
    
    return {
        'device_type': device_type,
        'is_mobile': device_type == 'mobile',
        'is_tablet': device_type == 'tablet',
        'is_desktop': device_type == 'desktop',
        'lazy_load': ImageOptimizer.should_lazy_load(device_type),
        'user_agent': user_agent,
    }


def optimize_image_field(image_field, request, size='medium'):
    """
    Get optimized image URL for the requesting device.
    
    Args:
        image_field: Django ImageField instance
        request: Django request object
        size (str): Desired image size
        
    Returns:
        str: Optimized image URL or None
    """
    device_context = get_device_context(request)
    device_type = device_context['device_type']
    
    return ImageOptimizer.get_optimized_image_url(
        image_field,
        device_type=device_type,
        size=size
    )
