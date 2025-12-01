"""
Admin Asynchronous Processing API Views

This module implements asynchronous processing for long-running admin operations
with progress tracking and completion notifications.

Note: This implementation uses Django's database for task tracking. For production
environments with high load, consider integrating Celery for true async processing.

Requirements: 11.4, 11.5
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from services.models import BatchOperation, Order, UserProfile, CustomService, Notification
import logging
import threading

logger = logging.getLogger(__name__)


class AsyncBulkOperationView(APIView):
    """
    API endpoint for submitting bulk operations for asynchronous processing.
    
    Creates a batch operation record and processes it in the background,
    allowing the client to poll for status updates.
    
    Requirements: 11.4, 11.5
    """
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        """
        Submit a bulk operation for asynchronous processing.
        
        Request format:
        {
            "operation_type": "order_update",
            "operations": [
                {
                    "resource_id": 1,
                    "data": {"status": "completed"}
                },
                ...
            ],
            "notify_on_completion": true
        }
        
        Response format:
        {
            "batch_id": 123,
            "status": "pending",
            "message": "Batch operation submitted for processing",
            "poll_url": "/api/v1/admin/async/status/123/"
        }
        """
        operation_type = request.data.get('operation_type')
        operations = request.data.get('operations', [])
        notify_on_completion = request.data.get('notify_on_completion', True)
        
        # Validation
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
        
        # Validate batch size
        MAX_OPERATIONS = 1000  # Higher limit for async operations
        if len(operations) > MAX_OPERATIONS:
            return Response(
                {
                    'error': {
                        'code': 'BATCH_SIZE_EXCEEDED',
                        'message': f'Maximum {MAX_OPERATIONS} operations allowed per async batch',
                        'details': {
                            'max_operations': MAX_OPERATIONS,
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
            total_operations=len(operations),
            status='pending'
        )
        
        # Store operations data in result_data for processing
        batch.result_data = {
            'operations': operations,
            'notify_on_completion': notify_on_completion
        }
        batch.save()
        
        # Start async processing in background thread
        # Note: In production, this should use Celery or similar task queue
        thread = threading.Thread(
            target=self._process_batch_async,
            args=(batch.id, operation_type, operations, notify_on_completion, request.user.id)
        )
        thread.daemon = True
        thread.start()
        
        response_data = {
            'batch_id': batch.id,
            'status': 'pending',
            'message': 'Batch operation submitted for processing',
            'poll_url': f'/api/v1/admin/async/status/{batch.id}/',
            'total_operations': len(operations),
            'estimated_duration_seconds': self._estimate_duration(len(operations))
        }
        
        return Response(response_data, status=status.HTTP_202_ACCEPTED)
    
    def _estimate_duration(self, operation_count):
        """
        Estimate processing duration based on operation count.
        
        Args:
            operation_count: Number of operations to process
            
        Returns:
            int: Estimated duration in seconds
        """
        # Rough estimate: 0.1 seconds per operation
        return max(1, int(operation_count * 0.1))
    
    def _process_batch_async(self, batch_id, operation_type, operations, notify_on_completion, user_id):
        """
        Process batch operations asynchronously in background.
        
        This method runs in a separate thread and processes operations sequentially.
        
        Requirements: 11.4, 11.5
        
        Args:
            batch_id: ID of the batch operation
            operation_type: Type of operation to perform
            operations: List of operations to process
            notify_on_completion: Whether to send notification on completion
            user_id: ID of the user who initiated the operation
        """
        try:
            # Get batch and mark as processing
            batch = BatchOperation.objects.get(id=batch_id)
            batch.start_processing()
            
            # Get user for notifications
            user = User.objects.get(id=user_id)
            
            # Process each operation
            for index, operation in enumerate(operations):
                try:
                    self._process_single_operation(
                        batch=batch,
                        index=index,
                        operation=operation,
                        operation_type=operation_type,
                        user=user
                    )
                except Exception as e:
                    logger.error(f'Async batch {batch_id} - Operation {index} failed: {str(e)}', exc_info=True)
                    # Continue processing other operations
            
            # Send completion notification if requested (Requirement 11.5)
            if notify_on_completion:
                self._send_completion_notification(batch, user)
            
            logger.info(f'Async batch {batch_id} completed: {batch.completed_operations}/{batch.total_operations} successful')
            
        except Exception as e:
            logger.error(f'Async batch {batch_id} processing failed: {str(e)}', exc_info=True)
            try:
                batch = BatchOperation.objects.get(id=batch_id)
                batch.status = 'failed'
                batch.completed_at = timezone.now()
                batch.save()
            except:
                pass
    
    def _process_single_operation(self, batch, index, operation, operation_type, user):
        """
        Process a single operation within the async batch.
        
        Args:
            batch: BatchOperation instance
            index: Index of the operation
            operation: Operation data
            operation_type: Type of operation
            user: User performing the operation
        """
        try:
            resource_id = operation.get('resource_id')
            data = operation.get('data', {})
            
            if not resource_id:
                raise ValueError('resource_id is required for each operation')
            
            # Route to appropriate handler
            if operation_type == 'order_update':
                result_data = self._handle_order_update(resource_id, data, user)
            elif operation_type == 'professional_approval':
                result_data = self._handle_professional_approval(resource_id, data, user)
            elif operation_type == 'service_update':
                result_data = self._handle_service_update(resource_id, data, user)
            elif operation_type == 'user_update':
                result_data = self._handle_user_update(resource_id, data, user)
            else:
                raise ValueError(f'Unsupported operation type: {operation_type}')
            
            # Mark as successful
            batch.complete_operation(success=True)
            batch.add_result(index, result_data)
            
        except Exception as e:
            # Mark as failed but continue processing
            batch.complete_operation(success=False)
            batch.add_error(index, {
                'code': 'OPERATION_FAILED',
                'message': str(e),
                'operation': operation
            })
    
    def _handle_order_update(self, resource_id, data, user):
        """Handle order update with transaction."""
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=resource_id)
            
            if 'status' in data:
                order.status = data['status']
            if 'notes' in data:
                order.notes = data['notes']
            if 'total_price' in data:
                order.total_price = float(data['total_price'])
            
            order.save()
            
            return {
                'id': order.id,
                'status': order.status,
                'updated_at': order.updated_at.isoformat()
            }
    
    def _handle_professional_approval(self, resource_id, data, user):
        """Handle professional approval with transaction."""
        with transaction.atomic():
            profile = UserProfile.objects.select_for_update().get(
                user_id=resource_id,
                user_type='professional'
            )
            
            if 'is_verified' in data:
                profile.is_verified = data['is_verified']
            if 'is_premium' in data:
                profile.is_premium = data['is_premium']
            if 'is_available' in data:
                profile.is_available = data['is_available']
            
            profile.save()
            
            return {
                'user_id': profile.user_id,
                'is_verified': profile.is_verified,
                'updated_at': profile.updated_at.isoformat()
            }
    
    def _handle_service_update(self, resource_id, data, user):
        """Handle service update with transaction."""
        with transaction.atomic():
            service = CustomService.objects.select_for_update().get(id=resource_id)
            
            if 'is_active' in data:
                service.is_active = data['is_active']
            if 'estimated_price' in data:
                service.estimated_price = float(data['estimated_price'])
            
            service.save()
            
            return {
                'id': service.id,
                'is_active': service.is_active,
                'updated_at': service.updated_at.isoformat()
            }
    
    def _handle_user_update(self, resource_id, data, user):
        """Handle user update with transaction."""
        with transaction.atomic():
            target_user = User.objects.select_for_update().get(id=resource_id)
            
            if 'is_active' in data:
                target_user.is_active = data['is_active']
            if 'email' in data:
                target_user.email = data['email']
            
            target_user.save()
            
            return {
                'id': target_user.id,
                'is_active': target_user.is_active
            }
    
    def _send_completion_notification(self, batch, user):
        """
        Send notification to user when batch operation completes.
        
        Requirement: 11.5
        
        Args:
            batch: BatchOperation instance
            user: User to notify
        """
        try:
            # Determine notification message based on results
            if batch.failed_operations == 0:
                title = 'Operação em Lote Concluída com Sucesso'
                message = f'Todas as {batch.completed_operations} operações foram concluídas com sucesso.'
            elif batch.completed_operations == 0:
                title = 'Operação em Lote Falhou'
                message = f'Todas as {batch.failed_operations} operações falharam.'
            else:
                title = 'Operação em Lote Parcialmente Concluída'
                message = f'{batch.completed_operations} operações concluídas, {batch.failed_operations} falharam.'
            
            # Create notification
            Notification.objects.create(
                user=user,
                notification_type='system',
                title=title,
                message=message,
                related_object_id=batch.id,
                related_object_type='batch_operation'
            )
            
            logger.info(f'Completion notification sent to user {user.id} for batch {batch.id}')
            
        except Exception as e:
            logger.error(f'Failed to send completion notification for batch {batch.id}: {str(e)}')


class AsyncBatchStatusView(APIView):
    """
    API endpoint for checking the status of an asynchronous batch operation.
    
    Allows clients to poll for progress updates and retrieve results when complete.
    
    Requirements: 11.4, 11.5
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request, batch_id):
        """
        Get the current status and progress of an async batch operation.
        
        Args:
            batch_id: ID of the batch operation
            
        Response format:
        {
            "batch_id": 123,
            "status": "processing",
            "progress": {
                "total": 100,
                "completed": 45,
                "failed": 2,
                "percentage": 47.0
            },
            "started_at": "2025-11-17T10:30:00Z",
            "estimated_completion": "2025-11-17T10:31:00Z",
            "results": {...}  // Only included when complete
        }
        """
        try:
            batch = BatchOperation.objects.get(id=batch_id)
            
            # Check permissions - only admin or batch owner can view
            if not (request.user.is_staff or batch.user == request.user):
                return Response(
                    {
                        'error': {
                            'code': 'PERMISSION_DENIED',
                            'message': 'You do not have permission to view this batch operation'
                        }
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
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
        
        # Build response
        response_data = {
            'batch_id': batch.id,
            'operation_type': batch.get_operation_type_display(),
            'status': batch.status,
            'status_display': batch.get_status_display(),
            'progress': {
                'total': batch.total_operations,
                'completed': batch.completed_operations,
                'failed': batch.failed_operations,
                'percentage': batch.progress_percentage,
                'success_rate': batch.success_rate
            },
            'created_at': batch.created_at.isoformat(),
            'started_at': batch.started_at.isoformat() if batch.started_at else None,
            'completed_at': batch.completed_at.isoformat() if batch.completed_at else None,
            'duration_seconds': batch.duration_seconds
        }
        
        # Add estimated completion time if still processing
        if batch.status == 'processing' and batch.started_at:
            elapsed = (timezone.now() - batch.started_at).total_seconds()
            if batch.completed_operations > 0:
                avg_time_per_op = elapsed / batch.completed_operations
                remaining_ops = batch.total_operations - batch.completed_operations - batch.failed_operations
                estimated_remaining = avg_time_per_op * remaining_ops
                estimated_completion = timezone.now() + timezone.timedelta(seconds=estimated_remaining)
                response_data['estimated_completion'] = estimated_completion.isoformat()
        
        # Include results if complete
        if batch.is_complete:
            response_data['results'] = batch.result_data
            response_data['errors'] = batch.error_details
        
        return Response(response_data, status=status.HTTP_200_OK)


class AsyncBatchCancelView(APIView):
    """
    API endpoint for canceling a pending or processing async batch operation.
    
    Note: Operations already completed cannot be rolled back.
    """
    permission_classes = [IsAdminUser]
    
    def post(self, request, batch_id):
        """
        Cancel an async batch operation.
        
        Only pending or processing batches can be canceled.
        Already completed operations will not be rolled back.
        """
        try:
            batch = BatchOperation.objects.get(id=batch_id)
            
            # Check permissions
            if not (request.user.is_staff or batch.user == request.user):
                return Response(
                    {
                        'error': {
                            'code': 'PERMISSION_DENIED',
                            'message': 'You do not have permission to cancel this batch operation'
                        }
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if can be canceled
            if batch.status in ['completed', 'failed']:
                return Response(
                    {
                        'error': {
                            'code': 'CANNOT_CANCEL',
                            'message': f'Cannot cancel batch operation with status: {batch.status}'
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark as failed (canceled)
            batch.status = 'failed'
            batch.completed_at = timezone.now()
            batch.add_error('cancel', {
                'code': 'CANCELED_BY_USER',
                'message': f'Batch operation canceled by {request.user.username}',
                'canceled_at': timezone.now().isoformat()
            })
            batch.save()
            
            return Response(
                {
                    'success': True,
                    'message': 'Batch operation canceled',
                    'batch_id': batch.id,
                    'completed_operations': batch.completed_operations,
                    'canceled_operations': batch.total_operations - batch.completed_operations - batch.failed_operations
                },
                status=status.HTTP_200_OK
            )
            
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
