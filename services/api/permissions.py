"""
Custom API permissions
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsServiceProvider(permissions.BasePermission):
    """
    Permission to check if user is a service provider
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, 'userprofile') and request.user.userprofile.is_provider
