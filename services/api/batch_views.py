"""
Batch Processing API Views

This module implements the batch processing API that allows clients to submit
multiple operations in a single request, reducing network latency and improving
efficiency for bulk operations.

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from services.models import BatchOperation, Order, UserProfile, CustomService
import logging

logger = logging.getLogger(__name__)


class BatchProcessingView(APIView):
    """
    API endpoint for processing multiple operations in a single request.
    
    Supports batch operations for orders, users, services, and other resources.
    Validates that no more than 50 operations are submitted per request.
    
    Implements comprehensive error handling with:
    - Transactional processing for data consistency (Requirement 7.2)
    - Continued processing despite individual failures (Requirement 7.2)
    - Individual status reporting for each operation (Requirement 7.3)
    
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
    """
    permission_classes = [IsAuthenticated]
    
    # Maximum number of operations allowed per batch (Requirement 7.5)
    MAX_OPERATIONS = 50
    
    # Error codes for standardized error responses
    ERROR_CODES = {
        'MISSING_OPERATION_TYPE': 'operation_type is required',
        'INVALID_OPERATIONS': 'operations must be a non-empty list',
        'BATCH_SIZE_EXCEEDED': 'Maximum operations limit exceeded',
        'INVALID_OPERATION_STRUCTURE': 'Invalid operation structure',
        'PERMISSION_DENIED': 'Permission denied',
        'RESOURCE_NOT_FOUND': 'Resource not found',
        'VALIDATION_ERROR': 'Validation error',
        'TRANSACTION_FAILED': 'Transaction failed'
    }
    
    def post(self, request):
        """
        Process a batch of operations.
        
        Request format:
        {
            "operation_type": "order_update",
            "operations": [
                {
                    "method": "PATCH",
                    "resource_id": 123,
                    "data": {"status": "completed"}
                },
                ...
            ]
        }
        
        Response format:
        {
            "batch_id": 1,
            "total_operations": 2,
            "results": [
                {
                    "index": 0,
                    "status": 200,
                    "success": true,
                    "data": {...}
                },
                {
                    "index": 1,
                    "status": 404,
                    "success": false,
                    "error": "Resource not found"
                }
            ],
            "summary": {
                "completed": 1,
                "failed": 1,
                "success_rate": 50.0
            }
        }
        """
        # Validate request data
        operation_type = request.data.get('operation_type')
        operations = request.data.get('operations', [])
        
        if not operation_type:
            return Response(
                {
                    'error': {
                        'code': 'MISSING_OPERATION_TYPE',
                        'message': 'operation_type is required'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not operations or not isinstance(operations, list):
            return Response(
                {
                    'error': {
                        'code': 'INVALID_OPERATIONS',
                        'message': 'operations must be a non-empty list'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate batch size (Requirement 7.5)
        if len(operations) > self.MAX_OPERATIONS:
            return Response(
                {
                    'error': {
                        'code': 'BATCH_SIZE_EXCEEDED',
                        'message': f'Maximum {self.MAX_OPERATIONS} operations allowed per batch',
                        'details': {
                            'max_operations': self.MAX_OPERATIONS,
                            'submitted_operations': len(operations)
                        }
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create batch operation record
        batch = BatchOperation.objects.create(
            user=request.user,
            operation_type=operation_type if operation_type in dict(BatchOperation.OPERATION_TYPE_CHOICES) else 'custom',
            total_operations=len(operations)
        )
        
        # Start processing
        batch.start_processing()
        
        # Process operations sequentially (Requirement 7.5)
        results = []
        for index, operation in enumerate(operations):
            result = self._process_single_operation(
                batch=batch,
                index=index,
                operation=operation,
                operation_type=operation_type,
                user=request.user
            )
            results.append(result)
        
        # Prepare response
        response_data = {
            'batch_id': batch.id,
            'total_operations': batch.total_operations,
            'results': results,
            'summary': {
                'completed': batch.completed_operations,
                'failed': batch.failed_operations,
                'success_rate': batch.success_rate,
                'progress': batch.progress_percentage
            },
            'status': batch.get_status_display(),
            'created_at': batch.created_at.isoformat(),
            'completed_at': batch.completed_at.isoformat() if batch.completed_at else None
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def _process_single_operation(self, batch, index, operation, operation_type, user):
        """
        Process a single operation within the batch.
        
        Requirements: 7.2, 7.3, 7.4
        
        Args:
            batch: BatchOperation instance
            index: Index of the operation in the batch
            operation: Operation data
            operation_type: Type of batch operation
            user: User performing the operation
            
        Returns:
            dict: Result of the operation
        """
        try:
            method = operation.get('method', 'PATCH').upper()
            resource_id = operation.get('resource_id')
            data = operation.get('data', {})
            
            # Validate operation structure
            if not resource_id:
                raise ValueError('resource_id is required for each operation')
            
            # Route to appropriate handler based on operation type
            if operation_type == 'order_update':
                result_data = self._handle_order_update(resource_id, data, method, user)
            elif operation_type == 'professional_approval':
                result_data = self._handle_professional_approval(resource_id, data, method, user)
            elif operation_type == 'service_update':
                result_data = self._handle_service_update(resource_id, data, method, user)
            elif operation_type == 'user_update':
                result_data = self._handle_user_update(resource_id, data, method, user)
            else:
                raise ValueError(f'Unsupported operation type: {operation_type}')
            
            # Mark operation as successful
            batch.complete_operation(success=True)
            batch.add_result(index, result_data)
            
            return {
                'index': index,
                'status': 200,
                'success': True,
                'data': result_data
            }
            
        except PermissionError as e:
            # Continue processing even with failures (Requirement 7.2)
            error_message = str(e)
            logger.warning(f'Batch operation {batch.id} - Operation {index} permission denied: {error_message}')
            
            batch.complete_operation(success=False)
            batch.add_error(index, {
                'code': 'PERMISSION_DENIED',
                'message': error_message,
                'operation': operation
            })
            
            return {
                'index': index,
                'status': 403,
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': error_message
                }
            }
        except ValueError as e:
            # Continue processing even with failures (Requirement 7.2)
            error_message = str(e)
            logger.warning(f'Batch operation {batch.id} - Operation {index} validation error: {error_message}')
            
            batch.complete_operation(success=False)
            batch.add_error(index, {
                'code': 'VALIDATION_ERROR',
                'message': error_message,
                'operation': operation
            })
            
            return {
                'index': index,
                'status': 400,
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': error_message
                }
            }
        except Exception as e:
            # Continue processing even with failures (Requirement 7.2)
            error_message = str(e)
            logger.error(f'Batch operation {batch.id} - Operation {index} failed: {error_message}', exc_info=True)
            
            batch.complete_operation(success=False)
            batch.add_error(index, {
                'code': 'TRANSACTION_FAILED',
                'message': error_message,
                'operation': operation,
                'type': type(e).__name__
            })
            
            return {
                'index': index,
                'status': 500,
                'success': False,
                'error': {
                    'code': 'TRANSACTION_FAILED',
                    'message': error_message,
                    'type': type(e).__name__
                }
            }
    
    def _handle_order_update(self, resource_id, data, method, user):
        """
        Handle order update operations with transactional processing.
        
        Requirements: 7.2, 7.3
        """
        try:
            # Use transaction for data consistency (Requirement 7.2)
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=resource_id)
                
                # Check permissions
                if not (user.is_staff or order.customer == user or order.professional == user):
                    raise PermissionError('You do not have permission to update this order')
                
                # Validate status transition
                if 'status' in data:
                    new_status = data['status']
                    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
                    if new_status not in valid_statuses:
                        raise ValueError(f'Invalid status: {new_status}')
                    order.status = new_status
                
                # Update other fields
                if 'notes' in data:
                    order.notes = data['notes']
                if 'total_price' in data and user.is_staff:
                    try:
                        order.total_price = float(data['total_price'])
                    except (ValueError, TypeError):
                        raise ValueError('Invalid total_price value')
                
                order.save()
                
                return {
                    'id': order.id,
                    'status': order.status,
                    'total_price': str(order.total_price),
                    'updated_at': order.updated_at.isoformat()
                }
        except Order.DoesNotExist:
            raise ValueError(f'Order {resource_id} not found')
        except Exception as e:
            # Re-raise with more context
            raise ValueError(f'Failed to update order {resource_id}: {str(e)}')
    
    def _handle_professional_approval(self, resource_id, data, method, user):
        """
        Handle professional approval operations with transactional processing.
        
        Requirements: 7.2, 7.3
        """
        if not user.is_staff:
            raise PermissionError('Only administrators can approve professionals')
        
        try:
            # Use transaction for data consistency (Requirement 7.2)
            with transaction.atomic():
                profile = UserProfile.objects.select_for_update().get(
                    user_id=resource_id,
                    user_type='professional'
                )
                
                # Validate boolean fields
                for field in ['is_verified', 'is_premium', 'is_available']:
                    if field in data:
                        value = data[field]
                        if not isinstance(value, bool):
                            raise ValueError(f'{field} must be a boolean value')
                        setattr(profile, field, value)
                
                profile.save()
                
                return {
                    'user_id': profile.user_id,
                    'username': profile.user.username,
                    'is_verified': profile.is_verified,
                    'is_premium': profile.is_premium,
                    'is_available': profile.is_available,
                    'updated_at': profile.updated_at.isoformat()
                }
        except UserProfile.DoesNotExist:
            raise ValueError(f'Professional profile {resource_id} not found')
        except Exception as e:
            raise ValueError(f'Failed to update professional {resource_id}: {str(e)}')
    
    def _handle_service_update(self, resource_id, data, method, user):
        """
        Handle service update operations with transactional processing.
        
        Requirements: 7.2, 7.3
        """
        try:
            # Use transaction for data consistency (Requirement 7.2)
            with transaction.atomic():
                service = CustomService.objects.select_for_update().get(id=resource_id)
                
                # Check permissions
                if not (user.is_staff or service.provider == user):
                    raise PermissionError('You do not have permission to update this service')
                
                # Validate and update fields
                if 'is_active' in data:
                    if not isinstance(data['is_active'], bool):
                        raise ValueError('is_active must be a boolean value')
                    service.is_active = data['is_active']
                
                if 'estimated_price' in data:
                    try:
                        price = float(data['estimated_price'])
                        if price < 0:
                            raise ValueError('estimated_price must be non-negative')
                        service.estimated_price = price
                    except (ValueError, TypeError):
                        raise ValueError('Invalid estimated_price value')
                
                if 'description' in data:
                    if not data['description'].strip():
                        raise ValueError('description cannot be empty')
                    service.description = data['description']
                
                if 'name' in data:
                    if not data['name'].strip():
                        raise ValueError('name cannot be empty')
                    service.name = data['name']
                
                service.save()
                
                return {
                    'id': service.id,
                    'name': service.name,
                    'is_active': service.is_active,
                    'estimated_price': str(service.estimated_price),
                    'updated_at': service.updated_at.isoformat()
                }
        except CustomService.DoesNotExist:
            raise ValueError(f'Service {resource_id} not found')
        except Exception as e:
            raise ValueError(f'Failed to update service {resource_id}: {str(e)}')
    
    def _handle_user_update(self, resource_id, data, method, user):
        """
        Handle user update operations with transactional processing.
        
        Requirements: 7.2, 7.3
        """
        if not user.is_staff:
            raise PermissionError('Only administrators can perform bulk user updates')
        
        try:
            # Use transaction for data consistency (Requirement 7.2)
            with transaction.atomic():
                target_user = User.objects.select_for_update().get(id=resource_id)
                
                # Validate and update fields
                if 'is_active' in data:
                    if not isinstance(data['is_active'], bool):
                        raise ValueError('is_active must be a boolean value')
                    target_user.is_active = data['is_active']
                
                if 'email' in data:
                    email = data['email'].strip()
                    if not email:
                        raise ValueError('email cannot be empty')
                    # Check if email is already in use by another user
                    if User.objects.filter(email=email).exclude(id=resource_id).exists():
                        raise ValueError(f'Email {email} is already in use')
                    target_user.email = email
                
                if 'first_name' in data:
                    target_user.first_name = data['first_name']
                
                if 'last_name' in data:
                    target_user.last_name = data['last_name']
                
                target_user.save()
                
                return {
                    'id': target_user.id,
                    'username': target_user.username,
                    'email': target_user.email,
                    'is_active': target_user.is_active,
                    'first_name': target_user.first_name,
                    'last_name': target_user.last_name
                }
        except User.DoesNotExist:
            raise ValueError(f'User {resource_id} not found')
        except Exception as e:
            raise ValueError(f'Failed to update user {resource_id}: {str(e)}')


class BatchStatusView(APIView):
    """
    API endpoint for checking the status of a batch operation.
    
    Allows clients to poll for batch operation status and results.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, batch_id):
        """
        Get the status and results of a batch operation.
        
        Args:
            batch_id: ID of the batch operation
            
        Returns:
            Batch operation status and results
        """
        try:
            batch = BatchOperation.objects.get(id=batch_id, user=request.user)
        except BatchOperation.DoesNotExist:
            return Response(
                {
                    'error': {
                        'code': 'BATCH_NOT_FOUND',
                        'message': f'Batch operation {batch_id} not found'
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        response_data = {
            'batch_id': batch.id,
            'operation_type': batch.get_operation_type_display(),
            'status': batch.get_status_display(),
            'total_operations': batch.total_operations,
            'completed_operations': batch.completed_operations,
            'failed_operations': batch.failed_operations,
            'progress': batch.progress_percentage,
            'success_rate': batch.success_rate,
            'created_at': batch.created_at.isoformat(),
            'started_at': batch.started_at.isoformat() if batch.started_at else None,
            'completed_at': batch.completed_at.isoformat() if batch.completed_at else None,
            'duration_seconds': batch.duration_seconds,
            'result_data': batch.result_data,
            'error_details': batch.error_details
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class BatchHistoryView(APIView):
    """
    API endpoint for retrieving batch operation history.
    
    Allows users to view their past batch operations.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get batch operation history for the current user.
        
        Query parameters:
            - limit: Number of records to return (default: 20, max: 100)
            - offset: Offset for pagination (default: 0)
            - status: Filter by status (optional)
            - operation_type: Filter by operation type (optional)
        """
        limit = min(int(request.query_params.get('limit', 20)), 100)
        offset = int(request.query_params.get('offset', 0))
        status_filter = request.query_params.get('status')
        operation_type_filter = request.query_params.get('operation_type')
        
        # Build query
        queryset = BatchOperation.objects.filter(user=request.user)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if operation_type_filter:
            queryset = queryset.filter(operation_type=operation_type_filter)
        
        # Get total count
        total_count = queryset.count()
        
        # Apply pagination
        batches = queryset[offset:offset + limit]
        
        # Serialize results
        results = []
        for batch in batches:
            results.append({
                'batch_id': batch.id,
                'operation_type': batch.get_operation_type_display(),
                'status': batch.get_status_display(),
                'total_operations': batch.total_operations,
                'completed_operations': batch.completed_operations,
                'failed_operations': batch.failed_operations,
                'progress': batch.progress_percentage,
                'success_rate': batch.success_rate,
                'created_at': batch.created_at.isoformat(),
                'completed_at': batch.completed_at.isoformat() if batch.completed_at else None,
                'duration_seconds': batch.duration_seconds
            })
        
        response_data = {
            'count': total_count,
            'limit': limit,
            'offset': offset,
            'results': results
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
