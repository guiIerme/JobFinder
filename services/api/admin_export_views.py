"""
Admin Data Export API Views

This module implements data export endpoints for administrators to export
orders, users, and other data in CSV and JSON formats with pagination support.

Requirements: 11.3
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.http import HttpResponse, StreamingHttpResponse
from django.contrib.auth.models import User
from services.models import Order, UserProfile, CustomService, ServiceRequest
import csv
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Echo:
    """An object that implements just the write method of the file-like interface."""
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


class ExportOrdersView(APIView):
    """
    API endpoint for exporting order data.
    
    Supports both CSV and JSON formats with pagination for large datasets.
    
    Requirements: 11.3
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """
        Export orders in CSV or JSON format.
        
        Query parameters:
            - format: 'csv' or 'json' (default: 'json')
            - status: Filter by order status (optional)
            - start_date: Filter orders from this date (YYYY-MM-DD) (optional)
            - end_date: Filter orders until this date (YYYY-MM-DD) (optional)
            - limit: Maximum number of records (default: 1000, max: 10000)
            - offset: Offset for pagination (default: 0)
        
        Response:
            - CSV: Streaming CSV file download
            - JSON: Paginated JSON response
        """
        export_format = request.query_params.get('format', 'json').lower()
        status_filter = request.query_params.get('status')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        limit = min(int(request.query_params.get('limit', 1000)), 10000)
        offset = int(request.query_params.get('offset', 0))
        
        # Build query
        queryset = Order.objects.select_related('customer', 'service', 'professional').all()
        
        # Apply filters
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(created_at__gte=start_dt)
            except ValueError:
                return Response(
                    {
                        'error': {
                            'code': 'INVALID_START_DATE',
                            'message': 'start_date must be in YYYY-MM-DD format'
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(created_at__lte=end_dt)
            except ValueError:
                return Response(
                    {
                        'error': {
                            'code': 'INVALID_END_DATE',
                            'message': 'end_date must be in YYYY-MM-DD format'
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get total count before pagination
        total_count = queryset.count()
        
        # Apply pagination
        orders = queryset[offset:offset + limit]
        
        if export_format == 'csv':
            return self._export_csv(orders, total_count, offset, limit)
        else:
            return self._export_json(orders, total_count, offset, limit)
    
    def _export_csv(self, orders, total_count, offset, limit):
        """Export orders as CSV file with streaming support."""
        # Define CSV headers
        headers = [
            'ID', 'Customer', 'Customer Email', 'Service', 'Professional',
            'Status', 'Scheduled Date', 'Total Price', 'Address',
            'Created At', 'Updated At'
        ]
        
        def generate_rows():
            """Generator function for streaming CSV rows."""
            writer = csv.writer(Echo())
            # Write header
            yield writer.writerow(headers)
            
            # Write data rows
            for order in orders:
                yield writer.writerow([
                    order.id,
                    order.customer.username,
                    order.customer.email,
                    order.service.name if order.service else order.service_name or 'N/A',
                    order.professional.username if order.professional else 'N/A',
                    order.get_status_display(),
                    order.scheduled_date.strftime('%Y-%m-%d %H:%M') if order.scheduled_date else 'N/A',
                    str(order.total_price),
                    order.address,
                    order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    order.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        # Create streaming response
        response = StreamingHttpResponse(
            generate_rows(),
            content_type='text/csv'
        )
        response['Content-Disposition'] = f'attachment; filename="orders_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        response['X-Total-Count'] = str(total_count)
        response['X-Offset'] = str(offset)
        response['X-Limit'] = str(limit)
        
        return response
    
    def _export_json(self, orders, total_count, offset, limit):
        """Export orders as JSON with pagination metadata."""
        data = []
        for order in orders:
            data.append({
                'id': order.id,
                'customer': {
                    'id': order.customer.id,
                    'username': order.customer.username,
                    'email': order.customer.email
                },
                'service': {
                    'id': order.service.id if order.service else None,
                    'name': order.service.name if order.service else order.service_name or 'N/A'
                },
                'professional': {
                    'id': order.professional.id if order.professional else None,
                    'username': order.professional.username if order.professional else None
                },
                'status': order.status,
                'status_display': order.get_status_display(),
                'scheduled_date': order.scheduled_date.isoformat() if order.scheduled_date else None,
                'total_price': str(order.total_price),
                'address': order.address,
                'notes': order.notes,
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat()
            })
        
        response_data = {
            'count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count,
            'next_offset': offset + limit if (offset + limit) < total_count else None,
            'results': data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class ExportUsersView(APIView):
    """
    API endpoint for exporting user data.
    
    Supports both CSV and JSON formats with pagination for large datasets.
    
    Requirements: 11.3
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """
        Export users in CSV or JSON format.
        
        Query parameters:
            - format: 'csv' or 'json' (default: 'json')
            - user_type: Filter by user type (customer/professional/admin) (optional)
            - is_active: Filter by active status (true/false) (optional)
            - is_verified: Filter verified professionals (true/false) (optional)
            - limit: Maximum number of records (default: 1000, max: 10000)
            - offset: Offset for pagination (default: 0)
        
        Response:
            - CSV: Streaming CSV file download
            - JSON: Paginated JSON response
        """
        export_format = request.query_params.get('format', 'json').lower()
        user_type = request.query_params.get('user_type')
        is_active = request.query_params.get('is_active')
        is_verified = request.query_params.get('is_verified')
        limit = min(int(request.query_params.get('limit', 1000)), 10000)
        offset = int(request.query_params.get('offset', 0))
        
        # Build query
        queryset = User.objects.select_related('userprofile').all()
        
        # Apply filters
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        if user_type:
            queryset = queryset.filter(userprofile__user_type=user_type)
        
        if is_verified is not None:
            is_verified_bool = is_verified.lower() == 'true'
            queryset = queryset.filter(userprofile__is_verified=is_verified_bool)
        
        # Get total count before pagination
        total_count = queryset.count()
        
        # Apply pagination
        users = queryset[offset:offset + limit]
        
        if export_format == 'csv':
            return self._export_csv(users, total_count, offset, limit)
        else:
            return self._export_json(users, total_count, offset, limit)
    
    def _export_csv(self, users, total_count, offset, limit):
        """Export users as CSV file with streaming support."""
        # Define CSV headers
        headers = [
            'ID', 'Username', 'Email', 'First Name', 'Last Name',
            'User Type', 'Phone', 'City', 'State', 'Is Active',
            'Is Verified', 'Is Premium', 'Rating', 'Date Joined'
        ]
        
        def generate_rows():
            """Generator function for streaming CSV rows."""
            writer = csv.writer(Echo())
            # Write header
            yield writer.writerow(headers)
            
            # Write data rows
            for user in users:
                profile = getattr(user, 'userprofile', None)
                yield writer.writerow([
                    user.id,
                    user.username,
                    user.email,
                    user.first_name,
                    user.last_name,
                    profile.get_user_type_display() if profile else 'N/A',
                    profile.phone if profile else '',
                    profile.city if profile else '',
                    profile.state if profile else '',
                    'Yes' if user.is_active else 'No',
                    'Yes' if profile and profile.is_verified else 'No',
                    'Yes' if profile and profile.is_premium else 'No',
                    str(profile.rating) if profile else '0.00',
                    user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        # Create streaming response
        response = StreamingHttpResponse(
            generate_rows(),
            content_type='text/csv'
        )
        response['Content-Disposition'] = f'attachment; filename="users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        response['X-Total-Count'] = str(total_count)
        response['X-Offset'] = str(offset)
        response['X-Limit'] = str(limit)
        
        return response
    
    def _export_json(self, users, total_count, offset, limit):
        """Export users as JSON with pagination metadata."""
        data = []
        for user in users:
            profile = getattr(user, 'userprofile', None)
            data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat(),
                'profile': {
                    'user_type': profile.user_type if profile else None,
                    'phone': profile.phone if profile else None,
                    'city': profile.city if profile else None,
                    'state': profile.state if profile else None,
                    'is_verified': profile.is_verified if profile else False,
                    'is_premium': profile.is_premium if profile else False,
                    'is_available': profile.is_available if profile else False,
                    'rating': str(profile.rating) if profile else '0.00',
                    'review_count': profile.review_count if profile else 0
                } if profile else None
            })
        
        response_data = {
            'count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count,
            'next_offset': offset + limit if (offset + limit) < total_count else None,
            'results': data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class ExportServicesView(APIView):
    """
    API endpoint for exporting service data.
    
    Supports both CSV and JSON formats with pagination for large datasets.
    
    Requirements: 11.3
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """
        Export services in CSV or JSON format.
        
        Query parameters:
            - format: 'csv' or 'json' (default: 'json')
            - is_active: Filter by active status (true/false) (optional)
            - category: Filter by category (optional)
            - limit: Maximum number of records (default: 1000, max: 10000)
            - offset: Offset for pagination (default: 0)
        
        Response:
            - CSV: Streaming CSV file download
            - JSON: Paginated JSON response
        """
        export_format = request.query_params.get('format', 'json').lower()
        is_active = request.query_params.get('is_active')
        category = request.query_params.get('category')
        limit = min(int(request.query_params.get('limit', 1000)), 10000)
        offset = int(request.query_params.get('offset', 0))
        
        # Build query
        queryset = CustomService.objects.select_related('provider').all()
        
        # Apply filters
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        if category:
            queryset = queryset.filter(category=category)
        
        # Get total count before pagination
        total_count = queryset.count()
        
        # Apply pagination
        services = queryset[offset:offset + limit]
        
        if export_format == 'csv':
            return self._export_csv(services, total_count, offset, limit)
        else:
            return self._export_json(services, total_count, offset, limit)
    
    def _export_csv(self, services, total_count, offset, limit):
        """Export services as CSV file with streaming support."""
        # Define CSV headers
        headers = [
            'ID', 'Name', 'Category', 'Provider', 'Provider Email',
            'Estimated Price', 'Is Active', 'Created At', 'Updated At'
        ]
        
        def generate_rows():
            """Generator function for streaming CSV rows."""
            writer = csv.writer(Echo())
            # Write header
            yield writer.writerow(headers)
            
            # Write data rows
            for service in services:
                yield writer.writerow([
                    service.id,
                    service.name,
                    service.get_category_display(),
                    service.provider.username,
                    service.provider.email,
                    str(service.estimated_price),
                    'Yes' if service.is_active else 'No',
                    service.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    service.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        # Create streaming response
        response = StreamingHttpResponse(
            generate_rows(),
            content_type='text/csv'
        )
        response['Content-Disposition'] = f'attachment; filename="services_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        response['X-Total-Count'] = str(total_count)
        response['X-Offset'] = str(offset)
        response['X-Limit'] = str(limit)
        
        return response
    
    def _export_json(self, services, total_count, offset, limit):
        """Export services as JSON with pagination metadata."""
        data = []
        for service in services:
            data.append({
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'category': service.category,
                'category_display': service.get_category_display(),
                'provider': {
                    'id': service.provider.id,
                    'username': service.provider.username,
                    'email': service.provider.email
                },
                'estimated_price': str(service.estimated_price),
                'is_active': service.is_active,
                'created_at': service.created_at.isoformat(),
                'updated_at': service.updated_at.isoformat()
            })
        
        response_data = {
            'count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count,
            'next_offset': offset + limit if (offset + limit) < total_count else None,
            'results': data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
