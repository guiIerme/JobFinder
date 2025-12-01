import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

from django.contrib.auth.models import User
from services.models import (
    Service, UserProfile, Order, ServiceRequestModal,
    ContactMessage, Review
)
from services.chat_models import ChatSession, ChatMessage

print("=" * 60)
print("VERIFICAÇÃO DE DADOS NO BANCO")
print("=" * 60)

print(f"\n👥 Usuários: {User.objects.count()}")
print(f"📋 Perfis de Usuário: {UserProfile.objects.count()}")
print(f"🛠️  Serviços: {Service.objects.count()}")
print(f"📦 Pedidos: {Order.objects.count()}")
print(f"📝 Solicitações: {ServiceRequestModal.objects.count()}")
print(f"✉️  Mensagens: {ContactMessage.objects.count()}")
print(f"⭐ Avaliações: {Review.objects.count()}")
print(f"💬 Sessões de Chat: {ChatSession.objects.count()}")
print(f"💭 Mensagens de Chat: {ChatMessage.objects.count()}")

print("\n" + "=" * 60)

# Mostrar alguns usuários
if User.objects.exists():
    print("\n📋 Primeiros 5 usuários:")
    for user in User.objects.all()[:5]:
        print(f"  - {user.username} ({user.email})")
else:
    print("\n⚠️  Nenhum usuário encontrado no banco de dados!")

# Mostrar alguns serviços
if Service.objects.exists():
    print("\n🛠️  Primeiros 5 serviços:")
    for service in Service.objects.all()[:5]:
        print(f"  - {service.name}")
else:
    print("\n⚠️  Nenhum serviço encontrado no banco de dados!")

print("\n" + "=" * 60)
