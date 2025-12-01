"""
Custom adapters for django-allauth
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib import messages


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter for better user experience
    """
    
    def get_login_redirect_url(self, request):
        """
        Redirect to home after login
        """
        return settings.LOGIN_REDIRECT_URL
    
    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        """
        Customize messages
        """
        if 'successfully signed in' in message_template.lower():
            message_template = 'Login realizado com sucesso!'
        elif 'successfully signed out' in message_template.lower():
            message_template = 'Logout realizado com sucesso!'
        
        return super().add_message(request, level, message_template, message_context, extra_tags)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter for better user experience
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a social provider,
        but before the login is actually processed
        """
        # If user exists, connect this new social login to the existing user
        if sociallogin.is_existing:
            return
        
        # Check if user with this email already exists
        if 'email' in sociallogin.account.extra_data:
            email = sociallogin.account.extra_data['email']
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            try:
                user = User.objects.get(email=email)
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                pass
    
    def populate_user(self, request, sociallogin, data):
        """
        Populate user information from social provider
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Get additional data from social provider
        if not user.first_name and 'first_name' in data:
            user.first_name = data['first_name']
        
        if not user.last_name and 'last_name' in data:
            user.last_name = data['last_name']
        
        # For providers that give full name instead of first/last
        if not user.first_name and 'name' in data:
            name_parts = data['name'].split(' ', 1)
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = name_parts[1]
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save user and show success message
        """
        user = super().save_user(request, sociallogin, form)
        
        # Add success message
        provider_name = sociallogin.account.provider.capitalize()
        messages.success(
            request,
            f'Conta conectada com sucesso via {provider_name}!'
        )
        
        return user
