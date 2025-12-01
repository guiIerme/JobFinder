"""
Mobile-optimized API views with compact responses.

These views provide streamlined endpoints specifically designed for mobile
applications with reduced data payloads and optimized queries.
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import models
from services.models import CustomService, UserProfile, ServiceRequestModal
from .mobile_serializers import (
    MobileServiceSerializer,
    MobileProfessionalSerializer,
    MobileOrderSerializer
)
from .pagination import OptimizedPagination
from .dynamic_fields_mixin import CompactResponseMixin


class MobileServiceViewSet(CompactResponseMixin, viewsets.ReadOnlyModelViewSet):
    """
    Mobile-optimized endpoint for services.
    
    GET /api/v1/mobile/services/
    
    Features:
    - Compact response with essential fields only
    - Optimized queries with select_related
    - Dynamic field selection support
    - Filtering by category and active status
    - Pagination enabled
    
    Query Parameters:
    - category: Filter by service category
    - is_active: Filter by active status (true/false)
    - provider: Filter by provider ID
    - ordering: Sort by created_at, estimated_price, or name
    - fields: Comma-separated list of fields to return (e.g., ?fields=id,name,estimated_price)
    - compact: Return minimal fields and minified JSON (e.g., ?compact=true)
    """
    serializer_class = MobileServiceSerializer
    pagination_class = OptimizedPagination
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'estimated_price', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Optimized queryset with select_related to reduce database queries.
        Only fetches fields that will be used based on field selection.
        """
        # Check if we need provider data
        fields_param = self.request.query_params.get('fields', '')
        compact = self.request.query_params.get('compact', '').lower() == 'true'
        
        # Start with base queryset
        queryset = CustomService.objects.all()
        
        # Only use select_related if provider fields are needed
        if not fields_param or 'provider' in fields_param or 'provider_name' in fields_param or not compact:
            queryset = queryset.select_related('provider')
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by provider
        provider_id = self.request.query_params.get('provider', None)
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        
        # Optimize by only selecting needed fields
        if compact or fields_param:
            # Determine which fields to fetch
            if compact:
                queryset = queryset.only('id', 'name', 'estimated_price')
            elif fields_param:
                fields = [f.strip() for f in fields_param.split(',') if f.strip()]
                # Map serializer fields to model fields
                model_fields = []
                for field in fields:
                    if field in ['id', 'name', 'category', 'estimated_price', 'is_active']:
                        model_fields.append(field)
                    elif field == 'provider_name':
                        model_fields.extend(['provider_id'])
                if model_fields:
                    queryset = queryset.only(*model_fields)
        
        return queryset


class MobileProfessionalViewSet(CompactResponseMixin, viewsets.ReadOnlyModelViewSet):
    """
    Mobile-optimized endpoint for professionals.
    
    GET /api/v1/mobile/professionals/
    
    Features:
    - Compact response with essential profile data
    - Optimized queries with select_related
    - Dynamic field selection support
    - Filtering by city, state, and availability
    - Pagination enabled
    
    Query Parameters:
    - city: Filter by city name
    - state: Filter by state code
    - is_available: Filter by availability (true/false)
    - is_verified: Filter by verification status (true/false)
    - ordering: Sort by rating, review_count, or created_at
    - fields: Comma-separated list of fields to return (e.g., ?fields=id,full_name,rating)
    - compact: Return minimal fields and minified JSON (e.g., ?compact=true)
    """
    serializer_class = MobileProfessionalSerializer
    pagination_class = OptimizedPagination
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['rating', 'review_count', 'created_at']
    ordering = ['-rating']
    
    def get_queryset(self):
        """
        Optimized queryset with select_related to reduce database queries.
        Defaults to professional user type. Only fetches needed fields.
        """
        # Check field selection
        fields_param = self.request.query_params.get('fields', '')
        compact = self.request.query_params.get('compact', '').lower() == 'true'
        
        queryset = UserProfile.objects.filter(user_type='professional')
        
        # Always need user for username and full_name
        queryset = queryset.select_related('user')
        
        # Filter by city
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Filter by state
        state = self.request.query_params.get('state', None)
        if state:
            queryset = queryset.filter(state__iexact=state)
        
        # Filter by availability
        is_available = self.request.query_params.get('is_available', None)
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')
        
        # Filter by verified status
        is_verified = self.request.query_params.get('is_verified', None)
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        
        # Optimize by only selecting needed fields
        if compact:
            queryset = queryset.only('id', 'user_id', 'rating', 'city')
        elif fields_param:
            fields = [f.strip() for f in fields_param.split(',') if f.strip()]
            model_fields = ['id', 'user_id']  # Always need these
            for field in fields:
                if field in ['phone', 'city', 'state', 'rating', 'review_count', 
                           'is_verified', 'is_available', 'avatar']:
                    model_fields.append(field)
            if model_fields:
                queryset = queryset.only(*model_fields)
        
        return queryset


class MobileOrderViewSet(CompactResponseMixin, viewsets.ReadOnlyModelViewSet):
    """
    Mobile-optimized endpoint for orders.
    
    GET /api/v1/mobile/orders/
    
    Features:
    - Compact response with essential order data
    - Optimized queries with select_related
    - Dynamic field selection support
    - User-specific filtering (own orders only)
    - Filtering by status
    - Pagination enabled
    
    Query Parameters:
    - status: Filter by order status
    - ordering: Sort by created_at, preferred_date, or status
    - fields: Comma-separated list of fields to return (e.g., ?fields=id,service_name,status)
    - compact: Return minimal fields and minified JSON (e.g., ?compact=true)
    
    Note: Users can only see their own orders (as customer or provider).
    """
    serializer_class = MobileOrderSerializer
    pagination_class = OptimizedPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'preferred_date', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Optimized queryset with select_related to reduce database queries.
        Users can only see their own orders (as customer or provider).
        Only fetches needed fields based on field selection.
        """
        user = self.request.user
        
        # Check field selection
        fields_param = self.request.query_params.get('fields', '')
        compact = self.request.query_params.get('compact', '').lower() == 'true'
        
        # Base queryset
        queryset = ServiceRequestModal.objects.all()
        
        # Only use select_related if related fields are needed
        if not compact or 'provider_name' in fields_param:
            queryset = queryset.select_related('user', 'provider', 'service')
        
        # Filter by user role
        if user.is_staff:
            # Admin can see all orders
            pass
        else:
            # Regular users see only their orders (as customer or provider)
            queryset = queryset.filter(
                models.Q(user=user) | models.Q(provider=user)
            )
        
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        # Optimize by only selecting needed fields
        if compact:
            queryset = queryset.only('id', 'service_name', 'status', 'created_at')
        elif fields_param:
            fields = [f.strip() for f in fields_param.split(',') if f.strip()]
            model_fields = ['id']  # Always need id
            for field in fields:
                if field in ['service_name', 'estimated_price', 'status', 
                           'preferred_date', 'created_at']:
                    model_fields.append(field)
                elif field == 'provider_name':
                    model_fields.append('provider_id')
            if model_fields:
                queryset = queryset.only(*model_fields)
        
        return queryset
