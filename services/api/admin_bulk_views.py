"""
Admin Bulk Operations API Views

This module implements bulk operation endpoints specifically for administrators
to efficiently manage orders, professionals, and other resources in batch.

Requirements: 11.1, 11.2
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.db import transaction
from django.contrib.auth.models import User
from services.models import Order, UserProfile, CustomService
import logging

logger = logging.getLogger(__name__)


class BulkOrderUpdateView(APIView):
    """
    API endpoint for bulk updating order statuses.
    
    Allows administrators to update the status of multiple orders in a single request.
    Implements transactional processing to ensure data consistency.
    
    Requirements: 11.1, 11.2
    """
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        """
        Bulk update order statuses.
        
        Request format:
        {
            "order_ids": [1, 2, 3, 4, 5],
            "status": "completed",
            "notes": "Bulk completion by admin"
        }
        
        Response format:
        {
            "success": true,
            "updated_count": 5,
            "failed_count": 0,
            "results": [
                {
                    "order_id": 1,
                    "success": true,
                    "status": "completed"
                },
                ...
            ]
        }
        """
        order_ids = request.data.get('order_ids', [])
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        # Validation
        if not order_ids or not isinstance(order_ids, list):
            return Response(
                {
                    'error': {
                        'code': 'INVALID_ORDER_IDS',
                        'message': 'order_ids must be a non-empty list'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not new_status:
            return Response(
                {
                    'error': {
                        'code': 'MISSING_STATUS',
                        'message': 'status is required'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate status value
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {
                    'error': {
                        'code': 'INVALID_STATUS',
                        'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process updates
        results = []
        updated_count = 0
        failed_count = 0
        
        for order_id in order_ids:
            try:
                with transaction.atomic():
                    order = Order.objects.select_for_update().get(id=order_id)
                    order.status = new_status
                    if notes:
                        order.notes = f"{order.notes}\n{notes}" if order.notes else notes
                    order.save()
                    
                    results.append({
                        'order_id': order_id,
                        'success': True,
                        'status': new_status,
                        'customer': order.customer.username
                    })
                    updated_count += 1
                    
            except Order.DoesNotExist:
                results.append({
                    'order_id': order_id,
                    'success': False,
                    'error': 'Order not found'
                })
                failed_count += 1
                logger.warning(f'Bulk update: Order {order_id} not found')
                
            except Exception as e:
                results.append({
                    'order_id': order_id,
                    'success': False,
                    'error': str(e)
                })
                failed_count += 1
                logger.error(f'Bulk update: Failed to update order {order_id}: {str(e)}')
        
        response_data = {
            'success': failed_count == 0,
            'updated_count': updated_count,
            'failed_count': failed_count,
            'total_count': len(order_ids),
            'results': results
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class BulkProfessionalApprovalView(APIView):
    """
    API endpoint for bulk approving/verifying professionals.
    
    Allows administrators to approve, verify, or update the status of multiple
    professionals in a single request.
    
    Requirements: 11.1, 11.2
    """
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        """
        Bulk approve or update professional profiles.
        
        Request format:
        {
            "user_ids": [1, 2, 3, 4, 5],
            "is_verified": true,
            "is_premium": false,
            "is_available": true
        }
        
        Response format:
        {
            "success": true,
            "updated_count": 5,
            "failed_count": 0,
            "results": [
                {
                    "user_id": 1,
                    "username": "john_plumber",
                    "success": true,
                    "is_verified": true
                },
                ...
            ]
        }
        """
        user_ids = request.data.get('user_ids', [])
        is_verified = request.data.get('is_verified')
        is_premium = request.data.get('is_premium')
        is_available = request.data.get('is_available')
        
        # Validation
        if not user_ids or not isinstance(user_ids, list):
            return Response(
                {
                    'error': {
                        'code': 'INVALID_USER_IDS',
                        'message': 'user_ids must be a non-empty list'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # At least one field must be provided
        if is_verified is None and is_premium is None and is_available is None:
            return Response(
                {
                    'error': {
                        'code': 'NO_FIELDS_TO_UPDATE',
                        'message': 'At least one field (is_verified, is_premium, is_available) must be provided'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process updates
        results = []
        updated_count = 0
        failed_count = 0
        
        for user_id in user_ids:
            try:
                with transaction.atomic():
                    profile = UserProfile.objects.select_for_update().get(
                        user_id=user_id,
                        user_type='professional'
                    )
                    
                    # Update fields if provided
                    if is_verified is not None:
                        profile.is_verified = is_verified
                    if is_premium is not None:
                        profile.is_premium = is_premium
                    if is_available is not None:
                        profile.is_available = is_available
                    
                    profile.save()
                    
                    results.append({
                        'user_id': user_id,
                        'username': profile.user.username,
                        'success': True,
                        'is_verified': profile.is_verified,
                        'is_premium': profile.is_premium,
                        'is_available': profile.is_available
                    })
                    updated_count += 1
                    
            except UserProfile.DoesNotExist:
                results.append({
                    'user_id': user_id,
                    'success': False,
                    'error': 'Professional profile not found'
                })
                failed_count += 1
                logger.warning(f'Bulk approval: Professional profile for user {user_id} not found')
                
            except Exception as e:
                results.append({
                    'user_id': user_id,
                    'success': False,
                    'error': str(e)
                })
                failed_count += 1
                logger.error(f'Bulk approval: Failed to update professional {user_id}: {str(e)}')
        
        response_data = {
            'success': failed_count == 0,
            'updated_count': updated_count,
            'failed_count': failed_count,
            'total_count': len(user_ids),
            'results': results
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class BulkServiceUpdateView(APIView):
    """
    API endpoint for bulk updating service statuses.
    
    Allows administrators to activate/deactivate multiple services in a single request.
    
    Requirements: 11.1, 11.2
    """
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        """
        Bulk update service statuses.
        
        Request format:
        {
            "service_ids": [1, 2, 3, 4, 5],
            "is_active": true
        }
        
        Response format:
        {
            "success": true,
            "updated_count": 5,
            "failed_count": 0,
            "results": [
                {
                    "service_id": 1,
                    "name": "Plumbing Service",
                    "success": true,
                    "is_active": true
                },
                ...
            ]
        }
        """
        service_ids = request.data.get('service_ids', [])
        is_active = request.data.get('is_active')
        
        # Validation
        if not service_ids or not isinstance(service_ids, list):
            return Response(
                {
                    'error': {
                        'code': 'INVALID_SERVICE_IDS',
                        'message': 'service_ids must be a non-empty list'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if is_active is None:
            return Response(
                {
                    'error': {
                        'code': 'MISSING_IS_ACTIVE',
                        'message': 'is_active field is required'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process updates
        results = []
        updated_count = 0
        failed_count = 0
        
        for service_id in service_ids:
            try:
                with transaction.atomic():
                    service = CustomService.objects.select_for_update().get(id=service_id)
                    service.is_active = is_active
                    service.save()
                    
                    results.append({
                        'service_id': service_id,
                        'name': service.name,
                        'provider': service.provider.username,
                        'success': True,
                        'is_active': is_active
                    })
                    updated_count += 1
                    
            except CustomService.DoesNotExist:
                results.append({
                    'service_id': service_id,
                    'success': False,
                    'error': 'Service not found'
                })
                failed_count += 1
                logger.warning(f'Bulk service update: Service {service_id} not found')
                
            except Exception as e:
                results.append({
                    'service_id': service_id,
                    'success': False,
                    'error': str(e)
                })
                failed_count += 1
                logger.error(f'Bulk service update: Failed to update service {service_id}: {str(e)}')
        
        response_data = {
            'success': failed_count == 0,
            'updated_count': updated_count,
            'failed_count': failed_count,
            'total_count': len(service_ids),
            'results': results
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
