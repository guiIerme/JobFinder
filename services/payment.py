"""
Módulo de pagamento para o Job Finder
Integração com Stripe para processamento de pagamentos
"""

import stripe
from django.conf import settings
from django.http import JsonResponse
from .models import Order, PaymentMethod

# Configure Stripe API key
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

class PaymentProcessor:
    """
    Processador de pagamentos usando Stripe
    """
    
    @staticmethod
    def create_payment_intent(order_id, user):
        """
        Cria um PaymentIntent no Stripe para um pedido
        """
        try:
            # Obter o pedido
            order = Order.objects.get(id=order_id, customer=user)
            
            # Converter o preço para centavos (Stripe trabalha com centavos)
            amount = int(float(order.total_price) * 100)
            
            # Criar o PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='brl',  # Real brasileiro
                metadata={
                    'order_id': order.id,
                    'customer_id': user.id,
                }
            )
            
            return {
                'success': True,
                'client_secret': intent['client_secret'],
                'payment_intent_id': intent['id']
            }
            
        except Order.DoesNotExist:
            return {
                'success': False,
                'error': 'Pedido não encontrado'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def confirm_payment(payment_intent_id, order_id, user):
        """
        Confirma o pagamento e atualiza o status do pedido
        """
        try:
            # Verificar o status do PaymentIntent no Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent['status'] == 'succeeded':
                # Atualizar o pedido
                order = Order.objects.get(id=order_id, customer=user)
                order.status = 'confirmed'
                order.save()
                
                return {
                    'success': True,
                    'message': 'Pagamento confirmado com sucesso'
                }
            else:
                return {
                    'success': False,
                    'error': 'Pagamento não foi processado com sucesso'
                }
                
        except Order.DoesNotExist:
            return {
                'success': False,
                'error': 'Pedido não encontrado'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def create_customer(email, name=None):
        """
        Cria um cliente no Stripe
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name
            )
            return customer
        except Exception as e:
            return None
    
    @staticmethod
    def save_payment_method(customer_id, payment_method_id):
        """
        Salva um método de pagamento para um cliente
        """
        try:
            # Anexar o método de pagamento ao cliente
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id,
            )
            
            # Definir como método de pagamento padrão
            stripe.Customer.modify(
                customer_id,
                invoice_settings={
                    'default_payment_method': payment_method_id,
                },
            )
            
            return True
        except Exception as e:
            return False

def process_payment(request):
    """
    View para processar pagamentos via AJAX
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
    
    try:
        order_id = request.POST.get('order_id')
        payment_method_id = request.POST.get('payment_method_id')
        
        if not order_id or not payment_method_id:
            return JsonResponse({'error': 'Dados incompletos'}, status=400)
        
        # Criar PaymentIntent
        processor = PaymentProcessor()
        result = processor.create_payment_intent(order_id, request.user)
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'client_secret': result['client_secret']
            })
        else:
            return JsonResponse({'error': result['error']}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)

def confirm_payment_view(request):
    """
    View para confirmar pagamento via AJAX
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
    
    try:
        payment_intent_id = request.POST.get('payment_intent_id')
        order_id = request.POST.get('order_id')
        
        if not payment_intent_id or not order_id:
            return JsonResponse({'error': 'Dados incompletos'}, status=400)
        
        # Confirmar pagamento
        processor = PaymentProcessor()
        result = processor.confirm_payment(payment_intent_id, order_id, request.user)
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': result['message']
            })
        else:
            return JsonResponse({'error': result['error']}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)