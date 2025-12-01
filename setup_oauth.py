#!/usr/bin/env python
"""
Script de configuração rápida para OAuth Social Authentication
Execute este script após configurar as credenciais OAuth
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def setup_site():
    """Configura o Site padrão"""
    site, created = Site.objects.get_or_create(
        id=1,
        defaults={
            'domain': 'localhost:8000',
            'name': 'Job Finder Local'
        }
    )
    if created:
        print("✅ Site criado com sucesso!")
    else:
        print("ℹ️  Site já existe")
    return site

def setup_social_apps(site):
    """Configura os Social Apps se as credenciais estiverem disponíveis"""
    
    # Google
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    google_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    if google_client_id and google_secret:
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth',
                'client_id': google_client_id,
                'secret': google_secret,
            }
        )
        if created:
            google_app.sites.add(site)
            print("✅ Google OAuth configurado!")
        else:
            print("ℹ️  Google OAuth já existe")
    else:
        print("⚠️  Credenciais do Google não encontradas no .env")
    
    # Facebook
    facebook_client_id = os.environ.get('FACEBOOK_CLIENT_ID')
    facebook_secret = os.environ.get('FACEBOOK_CLIENT_SECRET')
    
    if facebook_client_id and facebook_secret:
        facebook_app, created = SocialApp.objects.get_or_create(
            provider='facebook',
            defaults={
                'name': 'Facebook OAuth',
                'client_id': facebook_client_id,
                'secret': facebook_secret,
            }
        )
        if created:
            facebook_app.sites.add(site)
            print("✅ Facebook OAuth configurado!")
        else:
            print("ℹ️  Facebook OAuth já existe")
    else:
        print("⚠️  Credenciais do Facebook não encontradas no .env")
    
    # Microsoft
    microsoft_client_id = os.environ.get('MICROSOFT_CLIENT_ID')
    microsoft_secret = os.environ.get('MICROSOFT_CLIENT_SECRET')
    
    if microsoft_client_id and microsoft_secret:
        microsoft_app, created = SocialApp.objects.get_or_create(
            provider='microsoft',
            defaults={
                'name': 'Microsoft OAuth',
                'client_id': microsoft_client_id,
                'secret': microsoft_secret,
            }
        )
        if created:
            microsoft_app.sites.add(site)
            print("✅ Microsoft OAuth configurado!")
        else:
            print("ℹ️  Microsoft OAuth já existe")
    else:
        print("⚠️  Credenciais do Microsoft não encontradas no .env")

def main():
    print("\n🚀 Iniciando configuração OAuth...\n")
    
    # Verifica se o arquivo .env existe
    if not os.path.exists('.env'):
        print("❌ Arquivo .env não encontrado!")
        print("📝 Copie .env.example para .env e configure as credenciais")
        print("   cp .env.example .env")
        return
    
    try:
        # Configura o site
        site = setup_site()
        
        # Configura os social apps
        setup_social_apps(site)
        
        print("\n✨ Configuração concluída!")
        print("\n📋 Próximos passos:")
        print("1. Execute as migrações: python manage.py migrate")
        print("2. Crie um superusuário: python manage.py createsuperuser")
        print("3. Inicie o servidor: python manage.py runserver")
        print("4. Acesse: http://localhost:8000/login/")
        print("\n📖 Consulte OAUTH_SETUP_INSTRUCTIONS.md para mais detalhes")
        
    except Exception as e:
        print(f"\n❌ Erro durante a configuração: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
