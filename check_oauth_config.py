#!/usr/bin/env python
"""
Script para verificar a configuração OAuth
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def check_config():
    print("\n🔍 Verificando configuração OAuth...\n")
    
    # Check Site
    print("=" * 50)
    print("1. VERIFICANDO SITE")
    print("=" * 50)
    try:
        site = Site.objects.get(id=1)
        print(f"✅ Site ID: {site.id}")
        print(f"✅ Domain: {site.domain}")
        print(f"✅ Name: {site.name}")
    except Site.DoesNotExist:
        print("❌ Site não encontrado!")
        return
    
    # Check Social Apps
    print("\n" + "=" * 50)
    print("2. VERIFICANDO SOCIAL APPS")
    print("=" * 50)
    
    social_apps = SocialApp.objects.all()
    if not social_apps:
        print("❌ Nenhum Social App configurado!")
        return
    
    for app in social_apps:
        print(f"\n📱 {app.name} ({app.provider})")
        print(f"   Client ID: {app.client_id[:20]}..." if app.client_id else "   ❌ Client ID não configurado")
        print(f"   Secret: {'✅ Configurado' if app.secret else '❌ Não configurado'}")
        
        # Check if app is linked to site
        if site in app.sites.all():
            print(f"   ✅ Vinculado ao site {site.domain}")
        else:
            print(f"   ❌ NÃO vinculado ao site!")
            print(f"   🔧 Corrigindo...")
            app.sites.add(site)
            print(f"   ✅ Vinculado com sucesso!")
    
    # Check environment variables
    print("\n" + "=" * 50)
    print("3. VERIFICANDO VARIÁVEIS DE AMBIENTE")
    print("=" * 50)
    
    env_vars = {
        'GOOGLE_CLIENT_ID': os.environ.get('GOOGLE_CLIENT_ID'),
        'GOOGLE_CLIENT_SECRET': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'FACEBOOK_CLIENT_ID': os.environ.get('FACEBOOK_CLIENT_ID'),
        'FACEBOOK_CLIENT_SECRET': os.environ.get('FACEBOOK_CLIENT_SECRET'),
        'MICROSOFT_CLIENT_ID': os.environ.get('MICROSOFT_CLIENT_ID'),
        'MICROSOFT_CLIENT_SECRET': os.environ.get('MICROSOFT_CLIENT_SECRET'),
    }
    
    for var_name, var_value in env_vars.items():
        if var_value:
            print(f"✅ {var_name}: Configurado")
        else:
            print(f"⚠️  {var_name}: Não configurado (usando valor padrão vazio)")
    
    # Check URLs
    print("\n" + "=" * 50)
    print("4. URLs DE CALLBACK ESPERADAS")
    print("=" * 50)
    print(f"Google:    http://{site.domain}/accounts/google/login/callback/")
    print(f"Facebook:  http://{site.domain}/accounts/facebook/login/callback/")
    print(f"Microsoft: http://{site.domain}/accounts/microsoft/login/callback/")
    
    print("\n" + "=" * 50)
    print("5. PRÓXIMOS PASSOS")
    print("=" * 50)
    
    if not any(env_vars.values()):
        print("⚠️  Nenhuma credencial OAuth configurada no .env")
        print("\n📝 Para configurar:")
        print("1. Edite o arquivo .env")
        print("2. Adicione as credenciais OAuth")
        print("3. Execute: python manage.py setup_social_auth")
        print("4. Reinicie o servidor")
    else:
        print("✅ Configuração parece estar correta!")
        print("\n🧪 Para testar:")
        print("1. Inicie o servidor: python manage.py runserver")
        print("2. Acesse: http://localhost:8000/login/")
        print("3. Clique em um dos botões de login social")
        print("\n⚠️  IMPORTANTE:")
        print("- As credenciais OAuth devem estar configuradas nos consoles dos provedores")
        print("- As URLs de callback devem estar registradas")
        print("- Consulte OAUTH_SETUP_INSTRUCTIONS.md para mais detalhes")
    
    print("\n✨ Verificação concluída!\n")

if __name__ == '__main__':
    check_config()
