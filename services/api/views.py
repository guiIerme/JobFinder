"""
Base API views and viewsets
"""
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import models
from services.models import CustomService, UserProfile, ServiceRequestModal
from .serializers import (
    CustomServiceSerializer, 
    UserProfileSerializer, 
    ServiceRequestModalSerializer
)
from .pagination import OptimizedPagination


class BaseAPIViewSet(viewsets.ModelViewSet):
    """Base viewset with common configurations"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Override to filter by user if needed"""
        return super().get_queryset()


class CustomServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CustomService model with optimized queries and pagination.
    
    Features:
    - Optimized queries using select_related for provider
    - Pagination with OptimizedPagination
    - Filtering by category and active status
    - Ordering by created_at, price, and name
    """
    serializer_class = CustomServiceSerializer
    pagination_class = OptimizedPagination
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'estimated_price', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Optimized queryset with select_related to reduce database queries.
        Filters by category and active status if provided.
        """
        queryset = CustomService.objects.select_related('provider').all()
        
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
        
        return queryset


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserProfile model (professionals) with optimized queries and pagination.
    
    Features:
    - Optimized queries using select_related for user
    - Pagination with OptimizedPagination
    - Filtering by user_type, city, and availability
    - Ordering by rating, experience, and created_at
    """
    serializer_class = UserProfileSerializer
    pagination_class = OptimizedPagination
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['rating', 'experience_years', 'created_at', 'review_count']
    ordering = ['-rating']
    
    def get_queryset(self):
        """
        Optimized queryset with select_related to reduce database queries.
        Filters by user_type, city, and availability if provided.
        """
        queryset = UserProfile.objects.select_related('user').all()
        
        # Filter by user type (default to professionals)
        user_type = self.request.query_params.get('user_type', 'professional')
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        
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
        
        # Filter by premium status
        is_premium = self.request.query_params.get('is_premium', None)
        if is_premium is not None:
            queryset = queryset.filter(is_premium=is_premium.lower() == 'true')
        
        return queryset


class ServiceRequestModalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ServiceRequestModal model (orders) with optimized queries and pagination.
    
    Features:
    - Optimized queries using select_related for user, provider, and service
    - Pagination with OptimizedPagination
    - Filtering by status, user, and provider
    - Ordering by created_at and status
    """
    serializer_class = ServiceRequestModalSerializer
    pagination_class = OptimizedPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'updated_at', 'status', 'preferred_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Optimized queryset with select_related to reduce database queries.
        Filters by status, user, and provider if provided.
        Users can only see their own orders (as customer or provider).
        """
        user = self.request.user
        
        # Base queryset with optimized joins
        queryset = ServiceRequestModal.objects.select_related(
            'user', 'provider', 'service'
        ).all()
        
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
        
        # Filter by user (for admin)
        user_id = self.request.query_params.get('user', None)
        if user_id and user.is_staff:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by provider (for admin)
        provider_id = self.request.query_params.get('provider', None)
        if provider_id and user.is_staff:
            queryset = queryset.filter(provider_id=provider_id)
        
        return queryset


@api_view(['GET'])
def api_health_check(request):
    """Health check endpoint for API"""
    return Response({
        'status': 'healthy',
        'message': 'API is running'
    }, status=status.HTTP_200_OK)
