"""
API v1 URL configuration

This module defines all endpoints for API version 1.
All endpoints under /api/v1/ are routed through this configuration.

Requirements: 12.1
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
from .admin_bulk_views import (
    BulkOrderUpdateView,
    BulkProfessionalApprovalView,
    BulkServiceUpdateView
)
from .admin_export_views import (
    ExportOrdersView,
    ExportUsersView,
    ExportServicesView
)
from .admin_async_views import (
    AsyncBulkOperationView,
    AsyncBatchStatusView,
    AsyncBatchCancelView
)
from .deprecation_views import (
    PublicVersionInfoView
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

app_name = 'api_v1'

urlpatterns = [
    # Health check
    path('health/', api_health_check, name='health-check'),
    
    # Version information (Requirements: 12.1, 12.4)
    path('version/', PublicVersionInfoView.as_view(), name='version-info'),
    
    # Advanced search endpoints (Requirements: 3.1, 3.2, 3.3)
    path('search/', AdvancedSearchView.as_view(), name='advanced-search'),
    path('search/professionals/', ProfessionalSearchView.as_view(), name='professional-search'),
    
    # Analytics endpoints (Requirements: 6.1, 6.2, 6.3, 6.4, 6.5)
    path('analytics/performance/', PerformanceMetricsView.as_view(), name='analytics-performance'),
    path('analytics/errors/', ErrorMetricsView.as_view(), name='analytics-errors'),
    path('analytics/endpoints/', EndpointStatsView.as_view(), name='analytics-endpoints'),
    path('analytics/slowest/', SlowestEndpointsView.as_view(), name='analytics-slowest'),
    path('analytics/summary/', AnalyticsSummaryView.as_view(), name='analytics-summary'),
    
    # Batch processing endpoints (Requirements: 7.1, 7.2, 7.3, 7.4, 7.5)
    path('batch/', BatchProcessingView.as_view(), name='batch-process'),
    path('batch/<int:batch_id>/', BatchStatusView.as_view(), name='batch-status'),
    path('batch/history/', BatchHistoryView.as_view(), name='batch-history'),
    
    # Mobile-optimized endpoints (Requirements: 10.1, 10.2, 10.3, 10.4, 10.5)
    path('mobile/', include(mobile_router.urls)),
    
    # Admin bulk operations (Requirements: 11.1, 11.2)
    path('admin/bulk/orders/update-status/', BulkOrderUpdateView.as_view(), name='admin-bulk-order-update'),
    path('admin/bulk/professionals/approve/', BulkProfessionalApprovalView.as_view(), name='admin-bulk-professional-approval'),
    path('admin/bulk/services/update/', BulkServiceUpdateView.as_view(), name='admin-bulk-service-update'),
    
    # Admin data export (Requirement: 11.3)
    path('admin/export/orders/', ExportOrdersView.as_view(), name='admin-export-orders'),
    path('admin/export/users/', ExportUsersView.as_view(), name='admin-export-users'),
    path('admin/export/services/', ExportServicesView.as_view(), name='admin-export-services'),
    
    # Admin async processing (Requirements: 11.4, 11.5)
    path('admin/async/submit/', AsyncBulkOperationView.as_view(), name='admin-async-submit'),
    path('admin/async/status/<int:batch_id>/', AsyncBatchStatusView.as_view(), name='admin-async-status'),
    path('admin/async/cancel/<int:batch_id>/', AsyncBatchCancelView.as_view(), name='admin-async-cancel'),
    
    # Include router URLs (Requirements: 1.1, 2.1, 2.2)
    path('', include(router.urls)),
]
