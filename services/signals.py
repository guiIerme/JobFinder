"""
Signals for social authentication events and cache invalidation
"""

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from allauth.socialaccount.signals import pre_social_login, social_account_added
from django.contrib.auth.signals import user_logged_in
import logging

logger = logging.getLogger(__name__)


@receiver(pre_social_login)
def on_pre_social_login(sender, request, sociallogin, **kwargs):
    """
    Log when a user attempts to login via social account
    """
    provider = sociallogin.account.provider
    email = sociallogin.account.extra_data.get('email', 'No email')
    logger.info(f"Social login attempt via {provider} for email: {email}")


@receiver(social_account_added)
def on_social_account_added(sender, request, sociallogin, **kwargs):
    """
    Log when a new social account is connected
    """
    provider = sociallogin.account.provider
    user = sociallogin.user
    logger.info(f"Social account {provider} connected to user: {user.email}")


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    """
    Log successful logins
    """
    logger.info(f"User logged in: {user.email}")


# ============================================================================
# Cache Invalidation Signals
# ============================================================================

from services.cache_manager import CacheManager
from services.models import (
    Service, CustomService, UserProfile, Order, 
    PortfolioItem, ProfessionalAvailability
)


@receiver(post_save, sender=Service)
def invalidate_service_cache_on_save(sender, instance, created, **kwargs):
    """
    Invalidate service cache when a Service is created or updated.
    """
    logger.info(f"Invalidating cache for Service: {instance.id}")
    
    # Invalidate specific service detail cache
    CacheManager.invalidate_service_cache(instance.id)
    
    # Invalidate all service listings
    CacheManager.invalidate_service_cache()
    
    # Invalidate search cache
    CacheManager.invalidate("search:*")


@receiver(post_delete, sender=Service)
def invalidate_service_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate service cache when a Service is deleted.
    """
    logger.info(f"Invalidating cache for deleted Service: {instance.id}")
    
    # Invalidate specific service and all listings
    CacheManager.invalidate_service_cache(instance.id)
    CacheManager.invalidate_service_cache()
    CacheManager.invalidate("search:*")


@receiver(post_save, sender=CustomService)
def invalidate_custom_service_cache_on_save(sender, instance, created, **kwargs):
    """
    Invalidate custom service cache when a CustomService is created or updated.
    """
    logger.info(f"Invalidating cache for CustomService: {instance.id}")
    
    # Invalidate service listings
    CacheManager.invalidate("services:list:*")
    CacheManager.invalidate("search:*")
    
    # Invalidate professional's cache
    CacheManager.invalidate_professional_cache(instance.provider.id)


@receiver(post_delete, sender=CustomService)
def invalidate_custom_service_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate custom service cache when a CustomService is deleted.
    """
    logger.info(f"Invalidating cache for deleted CustomService: {instance.id}")
    
    CacheManager.invalidate("services:list:*")
    CacheManager.invalidate("search:*")
    CacheManager.invalidate_professional_cache(instance.provider.id)


@receiver(post_save, sender=UserProfile)
def invalidate_user_profile_cache_on_save(sender, instance, created, **kwargs):
    """
    Invalidate user profile cache when a UserProfile is created or updated.
    """
    logger.info(f"Invalidating cache for UserProfile: {instance.user.id}")
    
    # Invalidate user-specific cache
    CacheManager.invalidate_user_cache(instance.user.id)
    
    # If professional, invalidate professional listings
    if instance.user_type == 'professional':
        CacheManager.invalidate_professional_cache(instance.user.id)
        CacheManager.invalidate("professional:list:*")
        CacheManager.invalidate("search:*")


@receiver(post_delete, sender=UserProfile)
def invalidate_user_profile_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate user profile cache when a UserProfile is deleted.
    """
    logger.info(f"Invalidating cache for deleted UserProfile: {instance.user.id}")
    
    CacheManager.invalidate_user_cache(instance.user.id)
    
    if instance.user_type == 'professional':
        CacheManager.invalidate_professional_cache(instance.user.id)
        CacheManager.invalidate("professional:list:*")


@receiver(post_save, sender=Order)
def invalidate_order_cache_on_save(sender, instance, created, **kwargs):
    """
    Invalidate order cache when an Order is created or updated.
    """
    logger.info(f"Invalidating cache for Order: {instance.id}")
    
    # Invalidate customer's order cache
    CacheManager.invalidate_order_cache(instance.customer.id)
    
    # Invalidate professional's order cache if assigned
    if instance.professional:
        CacheManager.invalidate_order_cache(instance.professional.id)
        
        # Update professional statistics cache
        CacheManager.invalidate_professional_cache(instance.professional.id)


@receiver(post_delete, sender=Order)
def invalidate_order_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate order cache when an Order is deleted.
    """
    logger.info(f"Invalidating cache for deleted Order: {instance.id}")
    
    CacheManager.invalidate_order_cache(instance.customer.id)
    
    if instance.professional:
        CacheManager.invalidate_order_cache(instance.professional.id)
        CacheManager.invalidate_professional_cache(instance.professional.id)


@receiver(post_save, sender=PortfolioItem)
def invalidate_portfolio_cache_on_save(sender, instance, created, **kwargs):
    """
    Invalidate portfolio cache when a PortfolioItem is created or updated.
    """
    logger.info(f"Invalidating cache for PortfolioItem: {instance.id}")
    
    # Invalidate professional's cache
    CacheManager.invalidate_professional_cache(instance.professional.id)
    CacheManager.invalidate(f"portfolio:{instance.professional.id}:*")


@receiver(post_delete, sender=PortfolioItem)
def invalidate_portfolio_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate portfolio cache when a PortfolioItem is deleted.
    """
    logger.info(f"Invalidating cache for deleted PortfolioItem: {instance.id}")
    
    CacheManager.invalidate_professional_cache(instance.professional.id)
    CacheManager.invalidate(f"portfolio:{instance.professional.id}:*")


@receiver(post_save, sender=ProfessionalAvailability)
def invalidate_availability_cache_on_save(sender, instance, created, **kwargs):
    """
    Invalidate availability cache when ProfessionalAvailability is created or updated.
    """
    logger.info(f"Invalidating cache for ProfessionalAvailability: {instance.id}")
    
    # Invalidate professional's cache
    CacheManager.invalidate_professional_cache(instance.professional.id)
    CacheManager.invalidate(f"availability:{instance.professional.id}:*")


@receiver(post_delete, sender=ProfessionalAvailability)
def invalidate_availability_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate availability cache when ProfessionalAvailability is deleted.
    """
    logger.info(f"Invalidating cache for deleted ProfessionalAvailability: {instance.id}")
    
    CacheManager.invalidate_professional_cache(instance.professional.id)
    CacheManager.invalidate(f"availability:{instance.professional.id}:*")
