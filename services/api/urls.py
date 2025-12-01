"""
API URL configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    api_health_check,
    CustomServiceViewSet,
    UserProfileViewSet,
    ServiceRequestModalViewSet
)
from .search_views import (
    AdvancedSearchView,
    ProfessionalSearchView
)
from .analytics_views import (
    PerformanceMetricsView,
    ErrorMetricsView,
    EndpointStatsView,
    SlowestEndpointsView,
    AnalyticsSummaryView
)
from .batch_views import (
    BatchProcessingView,
    BatchStatusView,
    BatchHistoryView
)
from .mobile_views import (
    MobileServiceViewSet,
    MobileProfessionalViewSet,
    MobileOrderViewSet
)

# Create a router for viewsets
router = DefaultRouter()

# Register viewsets with optimized pagination
router.register(r'services', CustomServiceViewSet, basename='service')
router.register(r'professionals', UserProfileViewSet, basename='professional')
router.register(r'orders', ServiceRequestModalViewSet, basename='order')

# Create a separate router for mobile endpoints
mobile_router = DefaultRouter()
mobile_router.register(r'services', MobileServiceViewSet, basename='mobile-service')
mobile_router.register(r'professionals', MobileProfessionalViewSet, basename='mobile-professional')
mobile_router.register(r'orders', MobileOrderViewSet, basename='mobile-order')

app_name = 'api'

urlpatterns = [
    path('health/', api_health_check, name='health-check'),
    
    # Advanced search endpoints
    path('search/', AdvancedSearchView.as_view(), name='advanced-search'),
    path('search/professionals/', ProfessionalSearchView.as_view(), name='professional-search'),
    
    # Analytics endpoints
    path('analytics/performance/', PerformanceMetricsView.as_view(), name='analytics-performance'),
    path('analytics/errors/', ErrorMetricsView.as_view(), name='analytics-errors'),
    path('analytics/endpoints/', EndpointStatsView.as_view(), name='analytics-endpoints'),
    path('analytics/slowest/', SlowestEndpointsView.as_view(), name='analytics-slowest'),
    path('analytics/summary/', AnalyticsSummaryView.as_view(), name='analytics-summary'),
    
    # Batch processing endpoints
    path('batch/', BatchProcessingView.as_view(), name='batch-process'),
    path('batch/<int:batch_id>/', BatchStatusView.as_view(), name='batch-status'),
    path('batch/history/', BatchHistoryView.as_view(), name='batch-history'),
    
    # Mobile-optimized endpoints
    path('mobile/', include(mobile_router.urls)),
    
    # Include router URLs
    path('', include(router.urls)),
]
