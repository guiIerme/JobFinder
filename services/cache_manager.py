"""
Cache Manager Module

Provides centralized cache management with consistent key generation,
automatic invalidation, and user-specific cache isolation.
"""

from django.core.cache import cache
from django.conf import settings
from typing import Any, Callable, Optional, List
import hashlib
import json


class CacheManager:
    """
    Centralized cache management system for the application.
    
    Provides methods for:
    - Getting or setting cached values with callbacks
    - Invalidating cache by pattern
    - User-specific cache management
    - Consistent cache key generation
    """
    
    # Default timeouts for different data types (in seconds)
    TIMEOUT_LISTINGS = 15 * 60  # 15 minutes
    TIMEOUT_DETAILS = 30 * 60   # 30 minutes
    TIMEOUT_USER = 5 * 60       # 5 minutes
    TIMEOUT_SEARCH = 10 * 60    # 10 minutes
    
    @staticmethod
    def get_cache_key(prefix: str, *args, **kwargs) -> str:
        """
        Generate a consistent cache key from prefix and arguments.
        
        Args:
            prefix: Cache key prefix (e.g., 'services:list', 'user:profile')
            *args: Positional arguments to include in key
            **kwargs: Keyword arguments to include in key
            
        Returns:
            str: Generated cache key
            
        Example:
            >>> CacheManager.get_cache_key('services:list', category='cleaning', page=1)
            'services:list:category=cleaning:page=1'
        """
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            if arg is not None:
                key_parts.append(str(arg))
        
        # Add keyword arguments (sorted for consistency)
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            for k, v in sorted_kwargs:
                if v is not None:
                    key_parts.append(f"{k}={v}")
        
        cache_key = ":".join(key_parts)
        
        # If key is too long, hash it
        if len(cache_key) > 200:
            hash_suffix = hashlib.md5(cache_key.encode()).hexdigest()[:16]
            cache_key = f"{prefix}:hash:{hash_suffix}"
        
        return cache_key
    
    @staticmethod
    def get_or_set(
        key: str,
        callback: Callable[[], Any],
        timeout: Optional[int] = None
    ) -> Any:
        """
        Get value from cache or set it using callback if not found.
        
        Args:
            key: Cache key
            callback: Function to call if cache miss (should return value to cache)
            timeout: Cache timeout in seconds (None = default)
            
        Returns:
            Cached or freshly computed value
            
        Example:
            >>> def get_services():
            ...     return Service.objects.all()
            >>> services = CacheManager.get_or_set(
            ...     'services:list:all',
            ...     get_services,
            ...     timeout=900
            ... )
        """
        # Try to get from cache
        cached_value = cache.get(key)
        
        if cached_value is not None:
            return cached_value
        
        # Cache miss - compute value
        value = callback()
        
        # Set in cache
        if timeout is None:
            timeout = CacheManager.TIMEOUT_LISTINGS
        
        cache.set(key, value, timeout)
        
        return value
    
    @staticmethod
    def invalidate(pattern: str) -> int:
        """
        Invalidate all cache keys matching a pattern.
        
        Args:
            pattern: Cache key pattern to match (e.g., 'services:*', 'user:123:*')
            
        Returns:
            int: Number of keys invalidated
            
        Note:
            This implementation works with LocMem cache. For Redis,
            use SCAN with pattern matching for better performance.
            
        Example:
            >>> CacheManager.invalidate('services:list:*')
            5
        """
        # For LocMem cache, we need to track keys manually
        # In production with Redis, use SCAN command
        
        if hasattr(cache, '_cache'):
            # LocMem backend
            keys_to_delete = []
            cache_dict = cache._cache
            
            # Convert pattern to simple matching
            pattern_prefix = pattern.replace('*', '')
            
            for key in list(cache_dict.keys()):
                if isinstance(key, str) and key.startswith(pattern_prefix):
                    keys_to_delete.append(key)
            
            # Delete matched keys
            for key in keys_to_delete:
                cache.delete(key)
            
            return len(keys_to_delete)
        else:
            # For other backends, delete specific key
            cache.delete(pattern)
            return 1
    
    @staticmethod
    def invalidate_user_cache(user_id: int) -> int:
        """
        Invalidate all cache entries for a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            int: Number of keys invalidated
            
        Example:
            >>> CacheManager.invalidate_user_cache(123)
            3
        """
        pattern = f"user:{user_id}:*"
        return CacheManager.invalidate(pattern)
    
    @staticmethod
    def invalidate_service_cache(service_id: Optional[int] = None) -> int:
        """
        Invalidate service-related cache entries.
        
        Args:
            service_id: Specific service ID, or None to invalidate all services
            
        Returns:
            int: Number of keys invalidated
        """
        if service_id:
            # Invalidate specific service
            count = 0
            count += CacheManager.invalidate(f"service:detail:{service_id}")
            count += CacheManager.invalidate(f"service:{service_id}:*")
            return count
        else:
            # Invalidate all service listings
            return CacheManager.invalidate("services:list:*")
    
    @staticmethod
    def invalidate_professional_cache(user_id: Optional[int] = None) -> int:
        """
        Invalidate professional-related cache entries.
        
        Args:
            user_id: Specific professional user ID, or None to invalidate all
            
        Returns:
            int: Number of keys invalidated
        """
        if user_id:
            count = 0
            count += CacheManager.invalidate(f"professional:detail:{user_id}")
            count += CacheManager.invalidate(f"professional:{user_id}:*")
            return count
        else:
            return CacheManager.invalidate("professional:list:*")
    
    @staticmethod
    def invalidate_order_cache(user_id: int) -> int:
        """
        Invalidate order-related cache for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            int: Number of keys invalidated
        """
        return CacheManager.invalidate(f"orders:user:{user_id}:*")
    
    @staticmethod
    def clear_all() -> None:
        """
        Clear all cache entries.
        
        Warning: Use with caution, especially in production.
        """
        cache.clear()
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        return cache.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any, timeout: Optional[int] = None) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            timeout: Cache timeout in seconds
        """
        if timeout is None:
            timeout = CacheManager.TIMEOUT_LISTINGS
        cache.set(key, value, timeout)
    
    @staticmethod
    def delete(key: str) -> None:
        """
        Delete specific cache key.
        
        Args:
            key: Cache key to delete
        """
        cache.delete(key)
