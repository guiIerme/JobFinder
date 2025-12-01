"""
Mobile-optimized serializers with reduced fields for better performance.

These serializers provide compact versions of data models specifically
designed for mobile applications to reduce bandwidth and improve load times.
"""
from rest_framework import serializers
from services.models import CustomService, UserProfile, ServiceRequestModal
from .dynamic_fields_mixin import DynamicFieldsMixin
from .mobile_image_utils import optimize_image_field


class MobileServiceSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """
    Compact serializer for services on mobile devices.
    Only includes essential fields to minimize data transfer.
    
    Supports dynamic field selection:
    - ?fields=id,name,estimated_price - Only return specified fields
    - ?compact=true - Return minimal fields (id, name, estimated_price)
    """
    provider_name = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = CustomService
        fields = [
            'id',
            'name',
            'category',
            'category_display',
            'estimated_price',
            'provider',
            'provider_name',
            'is_active',
        ]
        # Minimal fields for compact mode
        compact_fields = ['id', 'name', 'estimated_price']
    
    def get_provider_name(self, obj):
        """Get provider's name or username"""
        if obj.provider.first_name:
            return f"{obj.provider.first_name} {obj.provider.last_name}".strip()
        return obj.provider.username


class MobileProfessionalSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """
    Compact serializer for professionals on mobile devices.
    Only includes essential profile information.
    
    Supports dynamic field selection:
    - ?fields=id,full_name,rating - Only return specified fields
    - ?compact=true - Return minimal fields (id, full_name, rating, city)
    
    Images are automatically optimized based on device type (mobile/tablet/desktop).
    """
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id',
            'username',
            'full_name',
            'phone',
            'city',
            'state',
            'rating',
            'review_count',
            'is_verified',
            'is_available',
            'avatar',
        ]
        # Minimal fields for compact mode
        compact_fields = ['id', 'full_name', 'rating', 'city']
    
    def get_full_name(self, obj):
        """Get user's full name"""
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.username
    
    def get_avatar(self, obj):
        """Get optimized avatar URL based on device type"""
        request = self.context.get('request')
        if not request or not obj.avatar:
            return None
        
        # Return optimized image URL for mobile devices
        return optimize_image_field(obj.avatar, request, size='avatar')


class MobileOrderSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """
    Compact serializer for orders on mobile devices.
    Simplified view of service requests.
    
    Supports dynamic field selection:
    - ?fields=id,service_name,status - Only return specified fields
    - ?compact=true - Return minimal fields (id, service_name, status, created_at)
    """
    provider_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ServiceRequestModal
        fields = [
            'id',
            'service_name',
            'estimated_price',
            'provider',
            'provider_name',
            'status',
            'status_display',
            'preferred_date',
            'created_at',
        ]
        # Minimal fields for compact mode
        compact_fields = ['id', 'service_name', 'status', 'created_at']
    
    def get_provider_name(self, obj):
        """Get provider's name"""
        if obj.provider:
            if obj.provider.first_name:
                return f"{obj.provider.first_name} {obj.provider.last_name}".strip()
            return obj.provider.username
        return None
