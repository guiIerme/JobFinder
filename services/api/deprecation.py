"""
API Deprecation Management

This module provides utilities for managing API version deprecation,
including scheduling deprecations, checking status, and generating warnings.

Requirements: 12.2, 12.3, 12.4
"""
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
import json


class DeprecationManager:
    """
    Manages API version deprecation lifecycle.
    
    Handles deprecation scheduling, warning generation, and status tracking.
    """
    
    # Minimum support period: 6 months (Requirement: 12.3)
    MINIMUM_SUPPORT_PERIOD_DAYS = 180
    
    # Cache key for deprecation data
    CACHE_KEY = 'api_deprecation_schedule'
    CACHE_TIMEOUT = 86400  # 24 hours
    
    @classmethod
    def schedule_deprecation(cls, version, deprecation_date=None, reason=None):
        """
        Schedule a version for deprecation.
        
        Args:
            version: API version string (e.g., 'v1')
            deprecation_date: datetime when version will be deprecated
                            (defaults to 6 months from now)
            reason: Optional reason for deprecation
            
        Returns:
            dict with deprecation details
            
        Raises:
            ValueError: If deprecation date is less than 6 months away
        """
        if deprecation_date is None:
            deprecation_date = datetime.now() + timedelta(days=cls.MINIMUM_SUPPORT_PERIOD_DAYS)
        
        # Validate minimum support period
        days_until_deprecation = (deprecation_date - datetime.now()).days
        if days_until_deprecation < cls.MINIMUM_SUPPORT_PERIOD_DAYS:
            raise ValueError(
                f"Deprecation date must be at least {cls.MINIMUM_SUPPORT_PERIOD_DAYS} days "
                f"in the future. Provided date is only {days_until_deprecation} days away."
            )
        
        # Get current schedule
        schedule = cls.get_deprecation_schedule()
        
        # Add or update version
        schedule[version] = {
            'version': version,
            'deprecation_date': deprecation_date.isoformat(),
            'scheduled_date': datetime.now().isoformat(),
            'reason': reason or 'Version superseded by newer release',
            'status': 'scheduled',
            'days_remaining': days_until_deprecation
        }
        
        # Save schedule
        cls._save_schedule(schedule)
        
        return schedule[version]
    
    @classmethod
    def cancel_deprecation(cls, version):
        """
        Cancel a scheduled deprecation.
        
        Args:
            version: API version string
            
        Returns:
            bool indicating success
        """
        schedule = cls.get_deprecation_schedule()
        
        if version in schedule:
            del schedule[version]
            cls._save_schedule(schedule)
            return True
        
        return False
    
    @classmethod
    def get_deprecation_schedule(cls):
        """
        Get the current deprecation schedule.
        
        Returns:
            dict mapping version to deprecation details
        """
        # Try cache first
        schedule = cache.get(cls.CACHE_KEY)
        
        if schedule is None:
            # Load from settings or initialize empty
            schedule = getattr(settings, 'API_DEPRECATION_SCHEDULE', {})
            cache.set(cls.CACHE_KEY, schedule, cls.CACHE_TIMEOUT)
        
        return schedule
    
    @classmethod
    def is_deprecated(cls, version):
        """
        Check if a version is deprecated.
        
        Args:
            version: API version string
            
        Returns:
            bool indicating if version is deprecated
        """
        schedule = cls.get_deprecation_schedule()
        
        if version not in schedule:
            return False
        
        deprecation_date = datetime.fromisoformat(schedule[version]['deprecation_date'])
        return datetime.now() >= deprecation_date
    
    @classmethod
    def get_deprecation_info(cls, version):
        """
        Get deprecation information for a version.
        
        Args:
            version: API version string
            
        Returns:
            dict with deprecation details or None if not deprecated
        """
        schedule = cls.get_deprecation_schedule()
        
        if version not in schedule:
            return None
        
        info = schedule[version].copy()
        
        # Calculate current days remaining
        deprecation_date = datetime.fromisoformat(info['deprecation_date'])
        days_remaining = (deprecation_date - datetime.now()).days
        info['days_remaining'] = max(0, days_remaining)
        
        # Update status
        if days_remaining <= 0:
            info['status'] = 'deprecated'
        elif days_remaining <= 30:
            info['status'] = 'imminent'
        else:
            info['status'] = 'scheduled'
        
        return info
    
    @classmethod
    def get_deprecation_warning(cls, version):
        """
        Generate a deprecation warning message for a version.
        
        Args:
            version: API version string
            
        Returns:
            dict with warning details or None if not deprecated
        """
        info = cls.get_deprecation_info(version)
        
        if info is None:
            return None
        
        deprecation_date = datetime.fromisoformat(info['deprecation_date'])
        days_remaining = info['days_remaining']
        
        # Generate appropriate message based on status
        if info['status'] == 'deprecated':
            message = (
                f"API version {version} has been deprecated and is no longer supported. "
                f"Please migrate to the latest version immediately."
            )
        elif info['status'] == 'imminent':
            message = (
                f"API version {version} will be deprecated in {days_remaining} days "
                f"on {deprecation_date.strftime('%Y-%m-%d')}. "
                f"Please migrate to the latest version as soon as possible."
            )
        else:
            message = (
                f"API version {version} is scheduled for deprecation on "
                f"{deprecation_date.strftime('%Y-%m-%d')} ({days_remaining} days remaining). "
                f"Please plan your migration to the latest version."
            )
        
        return {
            'message': message,
            'version': version,
            'deprecation_date': deprecation_date.strftime('%Y-%m-%d'),
            'days_remaining': days_remaining,
            'status': info['status'],
            'reason': info['reason'],
            'migration_guide': f'/api/docs/migration/{version}/'
        }
    
    @classmethod
    def get_all_warnings(cls):
        """
        Get deprecation warnings for all scheduled versions.
        
        Returns:
            list of warning dicts
        """
        schedule = cls.get_deprecation_schedule()
        warnings = []
        
        for version in schedule:
            warning = cls.get_deprecation_warning(version)
            if warning:
                warnings.append(warning)
        
        return warnings
    
    @classmethod
    def _save_schedule(cls, schedule):
        """
        Save deprecation schedule to cache.
        
        Args:
            schedule: dict of deprecation data
        """
        cache.set(cls.CACHE_KEY, schedule, cls.CACHE_TIMEOUT)
        
        # Also update settings if possible (for persistence)
        # Note: This requires manual update to settings file for production
        # In production, schedule should be managed via admin interface or config file


def get_version_support_status(version):
    """
    Get the support status for an API version.
    
    Args:
        version: API version string
        
    Returns:
        dict with support status information
    """
    info = DeprecationManager.get_deprecation_info(version)
    
    if info is None:
        return {
            'version': version,
            'status': 'active',
            'supported': True,
            'message': 'This version is fully supported.'
        }
    
    if info['status'] == 'deprecated':
        return {
            'version': version,
            'status': 'deprecated',
            'supported': False,
            'message': 'This version is no longer supported.',
            'deprecation_date': info['deprecation_date'],
            'migration_guide': f'/api/docs/migration/{version}/'
        }
    
    return {
        'version': version,
        'status': 'active_with_warning',
        'supported': True,
        'message': f'This version is supported but scheduled for deprecation.',
        'deprecation_date': info['deprecation_date'],
        'days_remaining': info['days_remaining'],
        'migration_guide': f'/api/docs/migration/{version}/'
    }


def check_version_compatibility(requested_version, minimum_version='v1'):
    """
    Check if a requested version is compatible with the minimum required version.
    
    Args:
        requested_version: Version requested by client
        minimum_version: Minimum version required
        
    Returns:
        bool indicating compatibility
    """
    # Extract numeric version
    def get_version_number(v):
        return int(v.replace('v', ''))
    
    try:
        requested = get_version_number(requested_version)
        minimum = get_version_number(minimum_version)
        return requested >= minimum
    except (ValueError, AttributeError):
        return False
