"""
Script para criar um agente de suporte de exemplo
Execute: python create_support_agent.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

from django.contrib.auth.models import User
from services.models import SupportAgent, UserProfile

def create_support_agent():
    """Cria um agente de suporte de exemplo"""
    
    print("=" * 60)
    print("CRIAR AGENTE DE SUPORTE")
    print("=" * 60)
    
    # Dados do agente
    username = input("\nUsername do agente (ex: agente1): ").strip() or "agente1"
    email = input("Email (ex: agente1@jobfinder.com): ").strip() or "agente1@jobfinder.com"
    password = input("Senha (ex: senha123): ").strip() or "senha123"
    first_name = input("Primeiro nome (ex: João): ").strip() or "João"
    last_name = input("Sobrenome (ex: Silva): ").strip() or "Silva"
    
    # Verificar se usuário já existe
    if User.objects.filter(username=username).exists():
        print(f"\n❌ Erro: Usuário '{username}' já existe!")
        return
    
    # Criar usuário
    print(f"\n📝 Criando usuário '{username}'...")
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    print(f"✅ Usuário criado com sucesso!")
    
    # Criar perfil de agente
    print(f"\n🎧 Criando perfil de agente de suporte...")
    agent = SupportAgent.objects.create(
        user=user,
        department='general',
        is_active=True,
        is_available=True,
        max_concurrent_tickets=10
    )
    print(f"✅ Agente criado com sucesso!")
    print(f"   ID do Funcionário: {agent.employee_id}")
    print(f"   Departamento: {agent.get_department_display()}")
    
    # Verificar UserProfile
    try:
        profile = user.userprofile
        print(f"\n👤 Perfil do usuário:")
        print(f"   Tipo: {profile.get_user_type_display()}")
    except:
        print(f"\n⚠️  Perfil do usuário não encontrado (será criado automaticamente)")
    
    print("\n" + "=" * 60)
    print("✅ AGENTE DE SUPORTE CRIADO COM SUCESSO!")
    print("=" * 60)
    print(f"\n📋 Credenciais de Login:")
    print(f"   Username: {username}")
    print(f"   Senha: {password}")
    print(f"\n🌐 URLs de Acesso:")
    print(f"   Dashboard: http://127.0.0.1:8000/support/agent/")
    print(f"   Login: http://127.0.0.1:8000/login/")
    print("\n")

if __name__ == '__main__':
    try:
        create_support_agent()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
