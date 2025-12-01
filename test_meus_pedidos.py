"""
Script de teste para validar a funcionalidade de Meus Pedidos
Execute com: python manage.py shell < test_meus_pedidos.py
"""

from django.contrib.auth.models import User
from services.models import ServiceRequestModal, CustomService
from datetime import date, time

print("=" * 60)
print("TESTE: Funcionalidade Meus Pedidos")
print("=" * 60)

# 1. Verificar se existem usuários
print("\n1. Verificando usuários...")
users = User.objects.all()
print(f"   Total de usuários: {users.count()}")

if users.count() == 0:
    print("   ⚠️  Nenhum usuário encontrado. Criando usuário de teste...")
    test_user = User.objects.create_user(
        username='cliente_teste',
        email='cliente@teste.com',
        password='senha123',
        first_name='Cliente',
        last_name='Teste'
    )
    print(f"   ✓ Usuário criado: {test_user.username}")
else:
    test_user = users.first()
    print(f"   ✓ Usando usuário existente: {test_user.username}")

# 2. Verificar solicitações existentes
print("\n2. Verificando solicitações existentes...")
solicitacoes = ServiceRequestModal.objects.filter(user=test_user)
print(f"   Total de solicitações do usuário: {solicitacoes.count()}")

# 3. Criar solicitações de teste se não existirem
if solicitacoes.count() == 0:
    print("   ⚠️  Nenhuma solicitação encontrada. Criando solicitações de teste...")
    
    # Criar solicitação pendente
    sol1 = ServiceRequestModal.objects.create(
        user=test_user,
        service_name='Reparo Elétrico',
        service_description='Troca de tomadas e interruptores',
        contact_name=test_user.get_full_name() or test_user.username,
        contact_phone='(11) 98765-4321',
        contact_email=test_user.email,
        address_street='Rua das Flores',
        address_number='123',
        address_neighborhood='Centro',
        address_city='São Paulo',
        address_state='SP',
        preferred_date=date.today(),
        preferred_period='manha',
        payment_method='dinheiro',
        status='pending'
    )
    print(f"   ✓ Solicitação criada: {sol1.service_name} (Status: {sol1.status})")
    
    # Criar solicitação agendada
    sol2 = ServiceRequestModal.objects.create(
        user=test_user,
        service_name='Limpeza Residencial',
        service_description='Limpeza completa de apartamento',
        contact_name=test_user.get_full_name() or test_user.username,
        contact_phone='(11) 98765-4321',
        contact_email=test_user.email,
        address_street='Av. Paulista',
        address_number='1000',
        address_neighborhood='Bela Vista',
        address_city='São Paulo',
        address_state='SP',
        preferred_date=date.today(),
        preferred_time=time(14, 0),
        payment_method='pix',
        status='scheduled'
    )
    print(f"   ✓ Solicitação criada: {sol2.service_name} (Status: {sol2.status})")
    
    # Criar solicitação concluída
    sol3 = ServiceRequestModal.objects.create(
        user=test_user,
        service_name='Encanamento',
        service_description='Conserto de vazamento',
        contact_name=test_user.get_full_name() or test_user.username,
        contact_phone='(11) 98765-4321',
        contact_email=test_user.email,
        address_street='Rua Augusta',
        address_number='500',
        address_neighborhood='Consolação',
        address_city='São Paulo',
        address_state='SP',
        preferred_date=date.today(),
        payment_method='cartao',
        status='completed'
    )
    print(f"   ✓ Solicitação criada: {sol3.service_name} (Status: {sol3.status})")

# 4. Testar queries da view
print("\n3. Testando queries da view...")
from django.db.models import Count, Q

# Query principal
solicitacoes_query = ServiceRequestModal.objects.filter(
    user=test_user
).select_related('provider', 'service').order_by('-created_at')
print(f"   ✓ Query principal retornou: {solicitacoes_query.count()} solicitações")

# Estatísticas otimizadas
stats = ServiceRequestModal.objects.filter(user=test_user).aggregate(
    total=Count('id'),
    pendentes=Count('id', filter=Q(status='pending')),
    agendadas=Count('id', filter=Q(status='scheduled')),
    concluidas=Count('id', filter=Q(status='completed'))
)
print(f"   ✓ Estatísticas calculadas:")
print(f"      - Total: {stats['total']}")
print(f"      - Pendentes: {stats['pendentes']}")
print(f"      - Agendadas: {stats['agendadas']}")
print(f"      - Concluídas: {stats['concluidas']}")

# 5. Testar filtros
print("\n4. Testando filtros...")
pending_filter = solicitacoes_query.filter(status='pending')
print(f"   ✓ Filtro 'pending': {pending_filter.count()} solicitações")

scheduled_filter = solicitacoes_query.filter(status='scheduled')
print(f"   ✓ Filtro 'scheduled': {scheduled_filter.count()} solicitações")

completed_filter = solicitacoes_query.filter(status='completed')
print(f"   ✓ Filtro 'completed': {completed_filter.count()} solicitações")

# 6. Verificar campos das solicitações
print("\n5. Verificando campos das solicitações...")
for sol in solicitacoes_query[:3]:
    print(f"\n   Solicitação #{sol.id}:")
    print(f"      - Serviço: {sol.service_name}")
    print(f"      - Status: {sol.get_status_display()}")
    print(f"      - Prestador: {sol.provider.get_full_name() if sol.provider else 'Não atribuído'}")
    print(f"      - Data: {sol.preferred_date}")
    print(f"      - Endereço: {sol.address_street}, {sol.address_number}")
    print(f"      - Pagamento: {sol.get_payment_method_display()}")
    print(f"      - Criado em: {sol.created_at}")

print("\n" + "=" * 60)
print("TESTE CONCLUÍDO COM SUCESSO!")
print("=" * 60)
print(f"\nAcesse a página em: http://localhost:8000/meus-pedidos/")
print(f"Usuário: {test_user.username}")
print(f"Senha: senha123 (se foi criado agora)")
print("=" * 60)
