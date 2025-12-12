#!/usr/bin/env python
"""
Script de diagnóstico para o chat da Sophie
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

def test_imports():
    """Testa todas as importações necessárias"""
    print("🔍 Testando importações...")
    
    try:
        from services.ai_processor import AIProcessor
        print("✅ AIProcessor importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar AIProcessor: {e}")
        return False
    
    try:
        from services.chat.consumers import ChatConsumer
        print("✅ ChatConsumer importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar ChatConsumer: {e}")
        return False
    
    try:
        from services.chat.manager import ChatManager
        print("✅ ChatManager importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar ChatManager: {e}")
        return False
    
    return True

def test_database():
    """Testa conexão com banco de dados"""
    print("\n🗄️ Testando banco de dados...")
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Conexão com banco de dados OK")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        return False

def test_chat_models():
    """Testa modelos do chat"""
    print("\n📊 Testando modelos do chat...")
    
    try:
        from services.chat_models import ChatSession, ChatMessage
        print("✅ Modelos do chat importados")
        
        # Testar criação de sessão
        session_count = ChatSession.objects.count()
        print(f"✅ Sessões existentes: {session_count}")
        
        message_count = ChatMessage.objects.count()
        print(f"✅ Mensagens existentes: {message_count}")
        
        return True
    except Exception as e:
        print(f"❌ Erro nos modelos do chat: {e}")
        return False

def test_websocket_routing():
    """Testa roteamento WebSocket"""
    print("\n🌐 Testando roteamento WebSocket...")
    
    try:
        from home_services.asgi import application
        print("✅ Aplicação ASGI configurada")
        
        from home_services.routing import websocket_urlpatterns
        print(f"✅ {len(websocket_urlpatterns)} rotas WebSocket configuradas")
        
        return True
    except Exception as e:
        print(f"❌ Erro no roteamento WebSocket: {e}")
        return False

def test_settings():
    """Testa configurações"""
    print("\n⚙️ Testando configurações...")
    
    try:
        from django.conf import settings
        
        # Testar CHAT_CONFIG
        chat_config = getattr(settings, 'CHAT_CONFIG', None)
        if chat_config:
            print("✅ CHAT_CONFIG encontrado")
            api_key = chat_config.get('OPENAI_API_KEY', '')
            if api_key and api_key != 'your_openai_api_key_here':
                print("✅ Chave OpenAI configurada")
            else:
                print("⚠️ Chave OpenAI não configurada (modo fallback)")
        else:
            print("❌ CHAT_CONFIG não encontrado")
            return False
        
        # Testar CHANNEL_LAYERS
        channel_layers = getattr(settings, 'CHANNEL_LAYERS', None)
        if channel_layers:
            print("✅ CHANNEL_LAYERS configurado")
        else:
            print("❌ CHANNEL_LAYERS não configurado")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Erro nas configurações: {e}")
        return False

def test_ai_processor():
    """Testa processador de IA"""
    print("\n🤖 Testando processador de IA...")
    
    try:
        import asyncio
        from services.ai_processor import AIProcessor
        
        async def test_message():
            processor = AIProcessor()
            response, metadata = await processor.process_message(
                "Olá!",
                {'user_type': 'anonymous'},
                []
            )
            return response, metadata
        
        response, metadata = asyncio.run(test_message())
        print(f"✅ Resposta gerada: {response[:50]}...")
        print(f"✅ Metadata: {metadata}")
        return True
    except Exception as e:
        print(f"❌ Erro no processador de IA: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    print("🔧 DIAGNÓSTICO DO CHAT DA SOPHIE")
    print("=" * 50)
    
    tests = [
        ("Importações", test_imports),
        ("Banco de Dados", test_database),
        ("Modelos do Chat", test_chat_models),
        ("Roteamento WebSocket", test_websocket_routing),
        ("Configurações", test_settings),
        ("Processador de IA", test_ai_processor),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro crítico em {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(tests)} testes passaram")
    
    if passed == len(tests):
        print("🎉 Todos os testes passaram! O chat deve estar funcionando.")
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
    
    return passed == len(tests)

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Diagnóstico interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico no diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)