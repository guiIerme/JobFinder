#!/usr/bin/env python
"""
Script para diagnosticar e corrigir problemas de CSRF
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

from django.conf import settings
from django.core.cache import cache
from django.contrib.sessions.models import Session

def clear_cache():
    """Limpa o cache"""
    print("🧹 Limpando cache...")
    try:
        cache.clear()
        print("✅ Cache limpo com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao limpar cache: {e}")
        return False

def clear_sessions():
    """Limpa sessões antigas"""
    print("🧹 Limpando sessões antigas...")
    try:
        count = Session.objects.count()
        Session.objects.all().delete()
        print(f"✅ {count} sessões removidas")
        return True
    except Exception as e:
        print(f"❌ Erro ao limpar sessões: {e}")
        return False

def check_csrf_settings():
    """Verifica configurações de CSRF"""
    print("🔍 Verificando configurações de CSRF...")
    
    # Verificar DEBUG
    debug = getattr(settings, 'DEBUG', False)
    print(f"DEBUG: {debug}")
    
    # Verificar CSRF_TRUSTED_ORIGINS
    csrf_origins = getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])
    print(f"CSRF_TRUSTED_ORIGINS: {csrf_origins}")
    
    # Verificar CSRF_COOKIE_SECURE
    csrf_secure = getattr(settings, 'CSRF_COOKIE_SECURE', False)
    print(f"CSRF_COOKIE_SECURE: {csrf_secure}")
    
    # Verificar middleware
    middleware = getattr(settings, 'MIDDLEWARE', [])
    csrf_middleware = 'django.middleware.csrf.CsrfViewMiddleware'
    
    if csrf_middleware in middleware:
        index = middleware.index(csrf_middleware)
        print(f"✅ CsrfViewMiddleware encontrado na posição {index}")
        
        # Verificar se está após SessionMiddleware
        session_middleware = 'django.contrib.sessions.middleware.SessionMiddleware'
        if session_middleware in middleware:
            session_index = middleware.index(session_middleware)
            if session_index < index:
                print("✅ SessionMiddleware está antes do CsrfViewMiddleware")
            else:
                print("❌ SessionMiddleware deve estar antes do CsrfViewMiddleware")
                return False
        else:
            print("❌ SessionMiddleware não encontrado")
            return False
    else:
        print("❌ CsrfViewMiddleware não encontrado")
        return False
    
    return True

def create_test_user():
    """Cria um usuário de teste se não existir"""
    print("👤 Verificando usuário de teste...")
    
    try:
        from django.contrib.auth.models import User
        
        username = 'admin'
        email = 'admin@test.com'
        password = 'admin123'
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            print(f"✅ Usuário criado: {username} / {password}")
        else:
            print(f"✅ Usuário já existe: {username}")
            
        return True
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return False

def test_csrf_token():
    """Testa geração de token CSRF"""
    print("🔐 Testando geração de token CSRF...")
    
    try:
        from django.middleware.csrf import get_token
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/')
        
        # Simular sessão
        from django.contrib.sessions.backends.db import SessionStore
        session = SessionStore()
        session.create()
        request.session = session
        
        token = get_token(request)
        print(f"✅ Token CSRF gerado: {token[:20]}...")
        return True
    except Exception as e:
        print(f"❌ Erro ao gerar token CSRF: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 DIAGNÓSTICO E CORREÇÃO DE CSRF")
    print("=" * 50)
    
    tests = [
        ("Configurações CSRF", check_csrf_settings),
        ("Limpeza de Cache", clear_cache),
        ("Limpeza de Sessões", clear_sessions),
        ("Usuário de Teste", create_test_user),
        ("Token CSRF", test_csrf_token),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro crítico: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 RESUMO")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ OK" if result else "❌ ERRO"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(tests)} testes passaram")
    
    if passed == len(tests):
        print("\n🎉 Tudo OK! Tente fazer login novamente.")
        print("👤 Usuário de teste: admin / admin123")
        print("🌐 URL: http://localhost:8000/login/")
    else:
        print("\n⚠️ Alguns problemas foram encontrados.")
        print("💡 Dicas:")
        print("   - Limpe o cache do navegador (Ctrl+Shift+Del)")
        print("   - Tente em uma aba anônima/privada")
        print("   - Verifique se não há cookies antigos")
    
    return passed == len(tests)

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)