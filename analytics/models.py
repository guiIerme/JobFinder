from django.db import models
from django.contrib.auth.models import User

class PageView(models.Model):
    """Track page views for analytics"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    path = models.CharField(max_length=500)
    referrer = models.URLField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Page View'
        verbose_name_plural = 'Page Views'
        app_label = 'analytics'
    
    def __str__(self):
        if self.user:
            return f"{getattr(self.user, 'username', 'Unknown')} - {self.path}"
        else:
            return f"Anonymous - {self.path}"

class UserAction(models.Model):
    """Track user actions for analytics"""
    ACTION_TYPES = [
        ('click', 'Click'),
        ('form_submit', 'Form Submit'),
        ('page_view', 'Page View'),
        ('search', 'Search'),
        ('purchase', 'Purchase'),
        ('login', 'Login'),
        ('register', 'Register'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    element_id = models.CharField(max_length=100, blank=True)
    page_path = models.CharField(max_length=500)
    additional_data = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'User Action'
        verbose_name_plural = 'User Actions'
        app_label = 'analytics'
    
    def __str__(self):
        if self.user:
            return f"{getattr(self.user, 'username', 'Unknown')} - {self.action_type} on {self.page_path}"
        else:
            return f"Anonymous - {self.action_type} on {self.page_path}"