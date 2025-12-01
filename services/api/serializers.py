"""
Base serializers for API endpoints
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from services.models import CustomService, UserProfile, ServiceRequestModal


class BaseSerializer(serializers.ModelSerializer):
    """Base serializer with common configurations"""
    
    class Meta:
        abstract = True


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for nested serialization"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class CustomServiceSerializer(serializers.ModelSerializer):
    """Serializer for CustomService model with optimized fields"""
    provider_username = serializers.CharField(source='provider.username', read_only=True)
    provider_name = serializers.SerializerMethodField()
    provider_rating = serializers.ReadOnlyField()
    provider_rating_count = serializers.ReadOnlyField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = CustomService
        fields = [
            'id', 'name', 'description', 'category', 'category_display',
            'estimated_price', 'estimated_duration', 'is_active',
            'provider', 'provider_username', 'provider_name',
            'provider_rating', 'provider_rating_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_provider_name(self, obj):
        """Get provider's full name or username"""
        if obj.provider.first_name and obj.provider.last_name:
            return f"{obj.provider.first_name} {obj.provider.last_name}"
        return obj.provider.username


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model (professionals)"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.SerializerMethodField()
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    completion_rate = serializers.ReadOnlyField()
    specialties_list = serializers.ReadOnlyField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'username', 'email', 'full_name',
            'user_type', 'user_type_display', 'phone', 'address',
            'city', 'state', 'zip_code', 'rating', 'review_count',
            'latitude', 'longitude', 'avatar',
            'bio', 'experience_years', 'specialties', 'specialties_list',
            'certifications', 'portfolio_url', 'linkedin_url', 'website_url',
            'business_name', 'business_hours', 'service_radius',
            'is_verified', 'is_premium', 'is_available',
            'total_jobs', 'completed_jobs', 'completion_rate',
            'response_time_hours', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'rating', 'review_count', 
                           'total_jobs', 'completed_jobs']
    
    def get_full_name(self, obj):
        """Get user's full name"""
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.username


class ServiceRequestModalSerializer(serializers.ModelSerializer):
    """Serializer for ServiceRequestModal model (orders)"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    provider_username = serializers.CharField(source='provider.username', read_only=True)
    service_name_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    preferred_period_display = serializers.CharField(source='get_preferred_period_display', read_only=True)
    
    class Meta:
        model = ServiceRequestModal
        fields = [
            'id', 'user', 'user_username', 'provider', 'provider_username',
            'service', 'service_name', 'service_name_display', 'service_description',
            'estimated_price', 'contact_name', 'contact_phone', 'contact_email',
            'contact_cpf', 'address_cep', 'address_street', 'address_number',
            'address_complement', 'address_neighborhood', 'address_city', 'address_state',
            'preferred_date', 'preferred_time', 'preferred_period', 'preferred_period_display',
            'schedule_notes', 'payment_method', 'payment_method_display',
            'payment_notes', 'card_type', 'card_installments', 'needs_change',
            'client_money_amount', 'pix_identifier', 'notes',
            'status', 'status_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_service_name_display(self, obj):
        """Get service name from related service or stored name"""
        if obj.service:
            return obj.service.name
        return obj.service_name
