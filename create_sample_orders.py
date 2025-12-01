"""
Script para criar pedidos de exemplo no banco de dados
Execute com: python manage.py shell < create_sample_orders.py
"""

from django.contrib.auth.models import User
from services.models import Order, Service, UserProfile, PaymentMethod
from datetime import datetime, timedelta
from django.utils import timezone

print("Criando pedidos de exemplo...")

# Buscar ou criar usuários
try:
    # Cliente
    customer = User.objects.filter(userprofile__user_type='customer').first()
    if not customer:
        customer = User.objects.create_user(
            username='cliente_teste',
            email='cliente@teste.com',
            password='senha123',
            first_name='João',
            last_name='Silva'
        )
        UserProfile.objects.create(
            user=customer,
            user_type='customer',
            phone='(11) 98765-4321',
            city='São Paulo',
            state='SP'
        )
        print(f"✓ Cliente criado: {customer.username}")
    else:
        print(f"✓ Usando cliente existente: {customer.username}")
    
    # Profissional
    professional = User.objects.filter(userprofile__user_type='professional').first()
    if not professional:
        professional = User.objects.create_user(
            username='profissional_teste',
            email='profissional@teste.com',
            password='senha123',
            first_name='Carlos',
            last_name='Santos'
        )
        UserProfile.objects.create(
            user=professional,
            user_type='professional',
            phone='(11) 91234-5678',
            city='São Paulo',
            state='SP',
            rating=4.8,
            review_count=25
        )
        print(f"✓ Profissional criado: {professional.username}")
    else:
        print(f"✓ Usando profissional existente: {professional.username}")
    
    # Buscar ou criar serviço
    service = Service.objects.first()
    if not service:
        service = Service.objects.create(
            name='Instalação Elétrica',
            category='eletrica',
            description='Instalação de tomadas e interruptores',
            estimated_price=150.00,
            is_active=True
        )
        print(f"✓ Serviço criado: {service.name}")
    else:
        print(f"✓ Usando serviço existente: {service.name}")
    
    # Buscar ou criar método de pagamento
    payment_method = PaymentMethod.objects.filter(user=customer).first()
    if not payment_method:
        payment_method = PaymentMethod.objects.create(
            user=customer,
            payment_type='credit_card',
            card_number_last4='1234',
            is_default=True
        )
        print(f"✓ Método de pagamento criado")
    else:
        print(f"✓ Usando método de pagamento existente")
    
    # Criar pedidos de exemplo
    hoje = timezone.now()
    
    pedidos = [
        {
            'status': 'pending',
            'scheduled_date': hoje + timedelta(days=2),
            'service_description': 'Preciso instalar 3 tomadas na sala',
            'total_price': 150.00,
            'address': 'Rua das Flores, 123 - São Paulo, SP'
        },
        {
            'status': 'confirmed',
            'scheduled_date': hoje + timedelta(days=1),
            'service_description': 'Instalação de ventilador de teto',
            'total_price': 200.00,
            'address': 'Av. Paulista, 1000 - São Paulo, SP'
        },
        {
            'status': 'in_progress',
            'scheduled_date': hoje,
            'service_description': 'Troca de disjuntores',
            'total_price': 180.00,
            'address': 'Rua Augusta, 500 - São Paulo, SP'
        },
        {
            'status': 'completed',
            'scheduled_date': hoje - timedelta(days=3),
            'service_description': 'Instalação de lustre',
            'total_price': 120.00,
            'address': 'Rua Oscar Freire, 200 - São Paulo, SP'
        },
        {
            'status': 'completed',
            'scheduled_date': hoje - timedelta(days=7),
            'service_description': 'Manutenção elétrica geral',
            'total_price': 250.00,
            'address': 'Rua Haddock Lobo, 300 - São Paulo, SP'
        },
    ]
    
    pedidos_criados = 0
    for pedido_data in pedidos:
        # Verificar se já existe um pedido similar
        existe = Order.objects.filter(
            customer=customer,
            status=pedido_data['status'],
            service_description=pedido_data['service_description']
        ).exists()
        
        if not existe:
            order = Order.objects.create(
                customer=customer,
                professional=professional,
                service=service,
                service_name=service.name,
                service_category=service.category,
                service_description=pedido_data['service_description'],
                scheduled_date=pedido_data['scheduled_date'],
                total_price=pedido_data['total_price'],
                address=pedido_data['address'],
                status=pedido_data['status'],
                payment_method=payment_method
            )
            pedidos_criados += 1
            print(f"✓ Pedido criado: #{order.id} - {pedido_data['status']}")
    
    if pedidos_criados == 0:
        print("ℹ Todos os pedidos já existem no banco de dados")
    else:
        print(f"\n✅ {pedidos_criados} pedidos criados com sucesso!")
    
    print(f"\n📊 Total de pedidos no sistema: {Order.objects.count()}")
    print(f"📊 Pedidos do cliente {customer.username}: {Order.objects.filter(customer=customer).count()}")
    
    print("\n" + "="*50)
    print("CREDENCIAIS PARA TESTE:")
    print("="*50)
    print(f"Cliente:")
    print(f"  Usuário: {customer.username}")
    print(f"  Senha: senha123")
    print(f"\nProfissional:")
    print(f"  Usuário: {professional.username}")
    print(f"  Senha: senha123")
    print("="*50)
    
except Exception as e:
    print(f"❌ Erro ao criar pedidos: {str(e)}")
    import traceback
    traceback.print_exc()
