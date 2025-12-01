"""
API views for analytics and monitoring.

Provides endpoints for:
- Performance metrics (response times, throughput)
- Error statistics
- Endpoint usage statistics
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from services.models import APIMetric


class PerformanceMetricsView(APIView):
    """
    API endpoint for performance metrics.
    
    GET /api/v1/analytics/performance/
    
    Query parameters:
    - hours: Time window in hours (default: 24)
    
    Returns:
    - total_requests: Total number of requests
    - avg_response_time: Average response time in ms
    - p95_response_time: 95th percentile response time
    - p99_response_time: 99th percentile response time
    - error_rate: Percentage of requests that resulted in errors
    - requests_per_minute: Average requests per minute
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Get time window from query params (default: 24 hours)
        hours = int(request.query_params.get('hours', 24))
        
        # Validate hours parameter
        if hours < 1 or hours > 720:  # Max 30 days
            return Response(
                {'error': 'Hours parameter must be between 1 and 720'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get performance statistics
        stats = APIMetric.get_performance_stats(hours=hours)
        
        # Add time window info
        stats['time_window_hours'] = hours
        stats['time_window_start'] = (timezone.now() - timedelta(hours=hours)).isoformat()
        stats['time_window_end'] = timezone.now().isoformat()
        
        return Response(stats, status=status.HTTP_200_OK)


class ErrorMetricsView(APIView):
    """
    API endpoint for error statistics.
    
    GET /api/v1/analytics/errors/
    
    Query parameters:
    - hours: Time window in hours (default: 24)
    - limit: Maximum number of results (default: 20)
    
    Returns:
    - errors: List of errors grouped by endpoint and status code
    - total_errors: Total number of errors
    - error_rate: Overall error rate percentage
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Get parameters
        hours = int(request.query_params.get('hours', 24))
        limit = int(request.query_params.get('limit', 20))
        
        # Validate parameters
        if hours < 1 or hours > 720:
            return Response(
                {'error': 'Hours parameter must be between 1 and 720'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if limit < 1 or limit > 100:
            return Response(
                {'error': 'Limit parameter must be between 1 and 100'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get error statistics
        error_stats = list(APIMetric.get_error_stats(hours=hours)[:limit])
        
        # Calculate total errors and error rate
        cutoff_time = timezone.now() - timedelta(hours=hours)
        total_requests = APIMetric.objects.filter(timestamp__gte=cutoff_time).count()
        total_errors = sum(stat['error_count'] for stat in error_stats)
        error_rate = round((total_errors / total_requests) * 100, 2) if total_requests > 0 else 0
        
        return Response({
            'errors': error_stats,
            'total_errors': total_errors,
            'total_requests': total_requests,
            'error_rate': error_rate,
            'time_window_hours': hours,
            'time_window_start': cutoff_time.isoformat(),
            'time_window_end': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class EndpointStatsView(APIView):
    """
    API endpoint for endpoint statistics.
    
    GET /api/v1/analytics/endpoints/
    
    Query parameters:
    - hours: Time window in hours (default: 24)
    - limit: Maximum number of results (default: 20)
    - sort: Sort by field (requests, avg_time, errors) (default: requests)
    
    Returns:
    - endpoints: List of endpoints with statistics
    - total_endpoints: Total number of unique endpoints
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Get parameters
        hours = int(request.query_params.get('hours', 24))
        limit = int(request.query_params.get('limit', 20))
        sort_by = request.query_params.get('sort', 'requests')
        
        # Validate parameters
        if hours < 1 or hours > 720:
            return Response(
                {'error': 'Hours parameter must be between 1 and 720'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if limit < 1 or limit > 100:
            return Response(
                {'error': 'Limit parameter must be between 1 and 100'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if sort_by not in ['requests', 'avg_time', 'errors']:
            return Response(
                {'error': 'Sort parameter must be one of: requests, avg_time, errors'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get endpoint statistics
        endpoint_stats = list(APIMetric.get_endpoint_stats(hours=hours))
        
        # Sort based on parameter
        if sort_by == 'avg_time':
            endpoint_stats.sort(key=lambda x: x['avg_response_time'], reverse=True)
        elif sort_by == 'errors':
            endpoint_stats.sort(key=lambda x: x['error_count'], reverse=True)
        # Default is already sorted by total_requests
        
        # Limit results
        endpoint_stats = endpoint_stats[:limit]
        
        # Calculate error rate for each endpoint
        for stat in endpoint_stats:
            if stat['total_requests'] > 0:
                stat['error_rate'] = round((stat['error_count'] / stat['total_requests']) * 100, 2)
            else:
                stat['error_rate'] = 0
        
        return Response({
            'endpoints': endpoint_stats,
            'total_endpoints': len(endpoint_stats),
            'time_window_hours': hours,
            'time_window_start': (timezone.now() - timedelta(hours=hours)).isoformat(),
            'time_window_end': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class SlowestEndpointsView(APIView):
    """
    API endpoint for slowest endpoints.
    
    GET /api/v1/analytics/slowest/
    
    Query parameters:
    - hours: Time window in hours (default: 24)
    - limit: Maximum number of results (default: 10)
    
    Returns:
    - endpoints: List of slowest endpoints with statistics
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Get parameters
        hours = int(request.query_params.get('hours', 24))
        limit = int(request.query_params.get('limit', 10))
        
        # Validate parameters
        if hours < 1 or hours > 720:
            return Response(
                {'error': 'Hours parameter must be between 1 and 720'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if limit < 1 or limit > 50:
            return Response(
                {'error': 'Limit parameter must be between 1 and 50'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get slowest endpoints
        slowest = list(APIMetric.get_slowest_endpoints(limit=limit, hours=hours))
        
        return Response({
            'endpoints': slowest,
            'time_window_hours': hours,
            'time_window_start': (timezone.now() - timedelta(hours=hours)).isoformat(),
            'time_window_end': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class AnalyticsSummaryView(APIView):
    """
    API endpoint for comprehensive analytics summary.
    
    GET /api/v1/analytics/summary/
    
    Query parameters:
    - hours: Time window in hours (default: 24)
    
    Returns:
    - performance: Performance metrics
    - top_errors: Top error endpoints
    - slowest_endpoints: Slowest endpoints
    - busiest_endpoints: Busiest endpoints
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Get time window
        hours = int(request.query_params.get('hours', 24))
        
        # Validate hours parameter
        if hours < 1 or hours > 720:
            return Response(
                {'error': 'Hours parameter must be between 1 and 720'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all statistics
        performance = APIMetric.get_performance_stats(hours=hours)
        top_errors = list(APIMetric.get_error_stats(hours=hours)[:10])
        slowest = list(APIMetric.get_slowest_endpoints(limit=10, hours=hours))
        busiest = list(APIMetric.get_endpoint_stats(hours=hours)[:10])
        
        return Response({
            'performance': performance,
            'top_errors': top_errors,
            'slowest_endpoints': slowest,
            'busiest_endpoints': busiest,
            'time_window_hours': hours,
            'time_window_start': (timezone.now() - timedelta(hours=hours)).isoformat(),
            'time_window_end': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
