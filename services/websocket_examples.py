"""
Example usage of WebSocket notification system.

This module demonstrates how to integrate WebSocket notifications
into your Django views and signals.

Requirements: 8.2, 8.3
"""

from django.contrib.auth.models import User
from services.websocket_utils import (
    create_and_send_notification,
    send_notification_to_user,
    broadcast_system_notification
)


# Example 1: Send notification when a service request is created
def example_service_request_created(service_request):
    """
    Send notification to provider when a new service request is created.
    
    This would typically be called from a view or signal handler.
    """
    if service_request.provider:
        create_and_send_notification(
            user=service_request.provider,
            notification_type='service_request',
            title='Nova Solicitação de Serviço',
            message=f'{service_request.customer.get_full_name() or service_request.customer.username} solicitou o serviço: {service_request.title}',
            sender=service_request.customer,
            related_object_id=service_request.id,
            related_object_type='ServiceRequest'
        )


# Example 2: Send notification when a service request is accepted
def example_service_request_accepted(service_request):
    """
    Send notification to customer when their service request is accepted.
    """
    create_and_send_notification(
        user=service_request.customer,
        notification_type='service_accepted',
        title='Serviço Aceito',
        message=f'{service_request.provider.get_full_name() or service_request.provider.username} aceitou sua solicitação de serviço!',
        sender=service_request.provider,
        related_object_id=service_request.id,
        related_object_type='ServiceRequest'
    )


# Example 3: Send notification when a service request is rejected
def example_service_request_rejected(service_request, reason=''):
    """
    Send notification to customer when their service request is rejected.
    """
    message = f'Sua solicitação de serviço foi recusada.'
    if reason:
        message += f' Motivo: {reason}'
    
    create_and_send_notification(
        user=service_request.customer,
        notification_type='service_rejected',
        title='Serviço Recusado',
        message=message,
        sender=service_request.provider,
        related_object_id=service_request.id,
        related_object_type='ServiceRequest'
    )


# Example 4: Send notification when a new message is received
def example_new_message(message):
    """
    Send notification when a new chat message is received.
    """
    # Determine the recipient (the other person in the chat)
    recipient = message.chat.professional if message.sender == message.chat.customer else message.chat.customer
    
    create_and_send_notification(
        user=recipient,
        notification_type='message',
        title='Nova Mensagem',
        message=f'{message.sender.get_full_name() or message.sender.username}: {message.content[:50]}...',
        sender=message.sender,
        related_object_id=message.chat.id,
        related_object_type='Chat'
    )


# Example 5: Send notification when an order status changes
def example_order_status_changed(order, old_status, new_status):
    """
    Send notification when an order status changes.
    """
    status_messages = {
        'confirmed': 'Seu pedido foi confirmado!',
        'in_progress': 'Seu pedido está em andamento.',
        'completed': 'Seu pedido foi concluído!',
        'cancelled': 'Seu pedido foi cancelado.'
    }
    
    message = status_messages.get(new_status, f'Status do pedido atualizado para: {new_status}')
    
    create_and_send_notification(
        user=order.customer,
        notification_type='system',
        title='Atualização de Pedido',
        message=message,
        related_object_id=order.id,
        related_object_type='Order'
    )


# Example 6: Broadcast system maintenance notification
def example_system_maintenance_notification():
    """
    Broadcast a system maintenance notification to all users.
    """
    count = broadcast_system_notification(
        title='Manutenção Programada',
        message='O sistema estará em manutenção das 2h às 4h da manhã. Pedimos desculpas pelo inconveniente.'
    )
    print(f'Sent maintenance notification to {count} users')


# Example 7: Send notification to specific users
def example_send_to_specific_users():
    """
    Send notification to specific users (e.g., all professionals).
    """
    from services.models import UserProfile
    
    # Get all professional users
    professional_profiles = UserProfile.objects.filter(user_type='professional')
    professional_ids = list(professional_profiles.values_list('user_id', flat=True))
    
    count = broadcast_system_notification(
        title='Nova Funcionalidade',
        message='Agora você pode receber notificações em tempo real!',
        user_ids=professional_ids
    )
    print(f'Sent notification to {count} professionals')


# Example 8: Integration with Django signals
from django.db.models.signals import post_save
from django.dispatch import receiver
from services.models import ServiceRequest


@receiver(post_save, sender=ServiceRequest)
def send_service_request_notification(sender, instance, created, **kwargs):
    """
    Automatically send notification when a ServiceRequest is created or updated.
    
    This is an example of how to integrate WebSocket notifications with Django signals.
    """
    if created and instance.provider:
        # New service request created
        example_service_request_created(instance)
    elif not created:
        # Service request updated - check status changes
        if instance.status == 'accepted':
            example_service_request_accepted(instance)
        elif instance.status == 'rejected':
            example_service_request_rejected(instance, instance.rejection_reason)


# Example 9: Manual notification sending (for testing)
def send_test_notification(user_id):
    """
    Send a test notification to a specific user.
    
    Useful for testing the WebSocket connection.
    
    Usage:
        from services.websocket_examples import send_test_notification
        send_test_notification(1)  # Send to user with ID 1
    """
    try:
        user = User.objects.get(id=user_id)
        notification_id = create_and_send_notification(
            user=user,
            notification_type='system',
            title='Notificação de Teste',
            message='Esta é uma notificação de teste do sistema WebSocket. Se você está vendo isso, o sistema está funcionando corretamente!'
        )
        print(f'Test notification sent to user {user_id}. Notification ID: {notification_id}')
        return notification_id
    except User.DoesNotExist:
        print(f'User with ID {user_id} does not exist')
        return None


# Example 10: Sending notification with custom data
def example_custom_notification_data(user, custom_data):
    """
    Example of sending a notification with custom data structure.
    
    While the database model has fixed fields, you can use related_object_id
    and related_object_type to link to any custom data.
    """
    from services.models import Notification
    from django.utils import timezone
    
    # Create notification
    notification = Notification.objects.create(
        user=user,
        notification_type='system',
        title=custom_data.get('title', 'Notification'),
        message=custom_data.get('message', ''),
        related_object_id=custom_data.get('object_id'),
        related_object_type=custom_data.get('object_type')
    )
    
    # Prepare data for WebSocket
    notification_data = {
        'id': notification.id,
        'title': notification.title,
        'message': notification.message,
        'notification_type': notification.notification_type,
        'created_at': notification.created_at.isoformat(),
        'is_read': False,
        'related_object_id': notification.related_object_id,
        'related_object_type': notification.related_object_type,
        # Add any custom fields here
        'custom_field': custom_data.get('custom_field')
    }
    
    # Send via WebSocket
    send_notification_to_user(user.id, notification_data)
    
    return notification.id
