"""
Módulo de notificações para o Job Finder
Envio de emails e notificações push
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from .models import Order, Chat, Message

class NotificationService:
    """
    Serviço de notificações para enviar emails e outras notificações
    """
    
    @staticmethod
    def send_order_confirmation(user, order):
        """
        Envia email de confirmação de pedido
        """
        try:
            subject = f'Confirmação de Pedido #{order.id} - Job Finder'
            
            # Renderizar template de email
            message = render_to_string('emails/order_confirmation.html', {
                'user': user,
                'order': order,
            })
            
            # Enviar email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=message
            )
            
            return True
        except Exception as e:
            # Em produção, isso deveria ser logado
            print(f"Erro ao enviar email de confirmação: {e}")
            return False
    
    @staticmethod
    def send_service_request_notification(professional, order):
        """
        Notifica o profissional sobre um novo pedido
        """
        try:
            subject = 'Novo Pedido de Serviço - Job Finder'
            
            # Renderizar template de email
            message = render_to_string('emails/new_service_request.html', {
                'professional': professional,
                'order': order,
            })
            
            # Enviar email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [professional.email],
                fail_silently=False,
                html_message=message
            )
            
            return True
        except Exception as e:
            # Em produção, isso deveria ser logado
            print(f"Erro ao enviar notificação de novo serviço: {e}")
            return False
    
    @staticmethod
    def send_message_notification(recipient, sender, chat):
        """
        Notifica usuário sobre nova mensagem no chat
        """
        try:
            subject = f'Nova Mensagem no Chat - Job Finder'
            
            # Renderizar template de email
            message = render_to_string('emails/new_message.html', {
                'recipient': recipient,
                'sender': sender,
                'chat': chat,
            })
            
            # Enviar email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient.email],
                fail_silently=False,
                html_message=message
            )
            
            return True
        except Exception as e:
            # Em produção, isso deveria ser logado
            print(f"Erro ao enviar notificação de mensagem: {e}")
            return False
    
    @staticmethod
    def send_service_completion_notification(user, order):
        """
        Notifica usuário sobre conclusão do serviço
        """
        try:
            subject = f'Serviço Concluído - Pedido #{order.id} - Job Finder'
            
            # Renderizar template de email
            message = render_to_string('emails/service_completed.html', {
                'user': user,
                'order': order,
            })
            
            # Enviar email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=message
            )
            
            return True
        except Exception as e:
            # Em produção, isso deveria ser logado
            print(f"Erro ao enviar notificação de conclusão: {e}")
            return False

# Templates de email (em produção, estes seriam arquivos HTML separados)

# services/templates/emails/order_confirmation.html
ORDER_CONFIRMATION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Confirmação de Pedido</title>
</head>
<body>
    <h2>Olá {{ user.username }},</h2>
    
    <p>Seu pedido de serviço foi confirmado com sucesso!</p>
    
    <h3>Detalhes do Pedido #{{ order.id }}:</h3>
    <ul>
        <li><strong>Serviço:</strong> {{ order.service.name if order.service else 'Serviço Personalizado' }}</li>
        <li><strong>Data Agendada:</strong> {{ order.scheduled_date|date:"d/m/Y H:i" }}</li>
        <li><strong>Valor Total:</strong> R$ {{ order.total_price }}</li>
        <li><strong>Status:</strong> {{ order.get_status_display }}</li>
    </ul>
    
    <p>Você pode acompanhar o status do seu pedido <a href="{{ request.build_absolute_uri(order.get_absolute_url) }}">clicando aqui</a>.</p>
    
    <p>Atenciosamente,<br>
    Equipe Job Finder</p>
</body>
</html>
"""

# services/templates/emails/new_service_request.html
NEW_SERVICE_REQUEST_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Novo Pedido de Serviço</title>
</head>
<body>
    <h2>Olá {{ professional.username }},</h2>
    
    <p>Você recebeu uma nova solicitação de serviço!</p>
    
    <h3>Detalhes do Pedido:</h3>
    <ul>
        <li><strong>Cliente:</strong> {{ order.customer.get_full_name|default:order.customer.username }}</li>
        <li><strong>Serviço:</strong> {{ order.service.name if order.service else 'Serviço Personalizado' }}</li>
        <li><strong>Data Agendada:</strong> {{ order.scheduled_date|date:"d/m/Y H:i" }}</li>
        <li><strong>Valor Estimado:</strong> R$ {{ order.total_price }}</li>
    </ul>
    
    <p>Você pode aceitar ou gerenciar este pedido <a href="{{ request.build_absolute_uri(order.get_absolute_url) }}">clicando aqui</a>.</p>
    
    <p>Atenciosamente,<br>
    Equipe Job Finder</p>
</body>
</html>
"""

# services/templates/emails/new_message.html
NEW_MESSAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Nova Mensagem no Chat</title>
</head>
<body>
    <h2>Olá {{ recipient.username }},</h2>
    
    <p>Você tem uma nova mensagem de {{ sender.get_full_name|default:sender.username }} no chat.</p>
    
    <p>Você pode responder a mensagem <a href="{{ request.build_absolute_uri(chat.get_absolute_url) }}">clicando aqui</a>.</p>
    
    <p>Atenciosamente,<br>
    Equipe Job Finder</p>
</body>
</html>
"""

# services/templates/emails/service_completed.html
SERVICE_COMPLETED_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Serviço Concluído</title>
</head>
<body>
    <h2>Olá {{ user.username }},</h2>
    
    <p>Seu serviço foi concluído com sucesso!</p>
    
    <h3>Detalhes do Pedido #{{ order.id }}:</h3>
    <ul>
        <li><strong>Serviço:</strong> {{ order.service.name if order.service else 'Serviço Personalizado' }}</li>
        <li><strong>Data de Conclusão:</strong> {{ order.updated_at|date:"d/m/Y H:i" }}</li>
        <li><strong>Valor Pago:</strong> R$ {{ order.total_price }}</li>
    </ul>
    
    <p>Gostaríamos de saber sua opinião sobre o serviço prestado. Por favor, <a href="{{ request.build_absolute_uri(order.get_review_url) }}">clique aqui</a> para deixar sua avaliação.</p>
    
    <p>Atenciosamente,<br>
    Equipe Job Finder</p>
</body>
</html>
"""