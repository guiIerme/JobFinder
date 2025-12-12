#!/usr/bin/env python
"""
Script para testar a Sophie (Assistente Virtual)

Este script testa tanto o modo OpenAI quanto o modo fallback.
"""

import os
import sys
import django
import asyncio

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

from services.ai_processor import AIProcessor
from django.conf import settings

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_config():
    """Mostra configuração atual"""
    print_header("CONFIGURAÇÃO DA SOPHIE")
    
    api_key = settings.CHAT_CONFIG.get('OPENAI_API_KEY', '')
    has_key = bool(api_key and api_key != 'your_openai_api_key_here')
    
    print(f"🔑 Chave OpenAI: {'✅ Configurada' if has_key else '❌ Não configurada'}")
    print(f"🤖 Modelo: {settings.CHAT_CONFIG.get('OPENAI_MODEL', 'N/A')}")
    print(f"🌡️  Temperatura: {settings.CHAT_CONFIG.get('OPENAI_TEMPERATURE', 'N/A')}")
    print(f"📝 Max Tokens: {settings.CHAT_CONFIG.get('OPENAI_MAX_TOKENS', 'N/A')}")
    print(f"💾 Cache: {'✅ Ativo' if settings.CHAT_CONFIG.get('CACHE_ENABLED', False) else '❌ Inativo'}")
    
    if not has_key:
        print("\n⚠️  AVISO: Sem chave OpenAI - Sophie usará modo fallback")
        print("   Para configurar: edite .env e adicione OPENAI_API_KEY=sk-sua-chave")

async def test_messages():
    """Testa diferentes tipos de mensagens"""
    print_header("TESTANDO MENSAGENS")
    
    processor = AIProcessor()
    
    # Mensagens de teste
    test_cases = [
        {
            'message': 'Olá!',
            'context': {'user_type': 'anonymous'},
            'description': 'Saudação simples'
        },
        {
            'message': 'Como posso contratar um serviço de limpeza?',
            'context': {'user_type': 'client'},
            'description': 'Pergunta sobre serviços'
        },
        {
            'message': 'Onde fica a página de meus pedidos?',
            'context': {'user_type': 'client', 'current_page': '/home'},
            'description': 'Ajuda de navegação'
        },
        {
            'message': 'Como aceito uma solicitação?',
            'context': {'user_type': 'provider'},
            'description': 'Pergunta de prestador'
        },
        {
            'message': 'Quanto custa um serviço?',
            'context': {'user_type': 'client'},
            'description': 'Pergunta sobre preços'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Teste {i}: {test['description']}")
        print(f"👤 Usuário: {test['message']}")
        
        try:
            # Processar mensagem
            response, metadata = await processor.process_message(
                test['message'],
                test['context'],
                []  # Sem histórico
            )
            
            print(f"🤖 Sophie: {response}")
            print(f"📊 Metadata:")
            print(f"   - Intenção: {metadata.get('intent', 'N/A')}")
            print(f"   - Cached: {metadata.get('cached', False)}")
            print(f"   - Fallback: {metadata.get('fallback', False)}")
            print(f"   - Tempo: {metadata.get('processing_time_ms', 0)}ms")
            
        except Exception as e:
            print(f"❌ Erro: {e}")

def test_intents():
    """Testa detecção de intenções"""
    print_header("TESTANDO DETECÇÃO DE INTENÇÕES")
    
    processor = AIProcessor()
    
    intent_tests = [
        ('Oi, tudo bem?', 'greeting'),
        ('Preciso de ajuda', 'help_request'),
        ('Quero contratar um eletricista', 'service_inquiry'),
        ('Onde fica o menu?', 'navigation_help'),
        ('Como aceito pedidos?', 'provider_question'),
        ('Quanto vou pagar?', 'payment_question'),
        ('Obrigado pela ajuda', 'gratitude'),
        ('Tchau!', 'goodbye'),
        ('Qual é o horário de funcionamento?', 'general_question')
    ]
    
    print("Testando detecção de intenções:")
    for message, expected in intent_tests:
        detected = processor.extract_intent(message)
        status = "✅" if detected == expected else "❌"
        print(f"{status} '{message}' → {detected} (esperado: {expected})")

async def test_conversation():
    """Testa uma conversa completa"""
    print_header("TESTANDO CONVERSA COMPLETA")
    
    processor = AIProcessor()
    history = []
    context = {'user_type': 'client'}
    
    conversation = [
        "Olá!",
        "Preciso contratar um serviço de limpeza",
        "Quanto custa em média?",
        "Como faço para solicitar?",
        "Obrigado!"
    ]
    
    print("🗣️  Simulando conversa:")
    
    for i, message in enumerate(conversation, 1):
        print(f"\n{i}. 👤 Usuário: {message}")
        
        try:
            response, metadata = await processor.process_message(
                message, context, history
            )
            
            print(f"   🤖 Sophie: {response}")
            
            # Adicionar ao histórico
            history.append({
                'sender_type': 'user',
                'content': message,
                'created_at': '2024-01-01T00:00:00Z'
            })
            history.append({
                'sender_type': 'assistant', 
                'content': response,
                'created_at': '2024-01-01T00:00:00Z'
            })
            
            # Limitar histórico
            if len(history) > 10:
                history = history[-10:]
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def main():
    """Função principal"""
    print("🤖 TESTE DA SOPHIE - ASSISTENTE VIRTUAL")
    print("=" * 60)
    
    # Mostrar configuração
    print_config()
    
    # Executar testes
    try:
        # Teste de intenções (síncrono)
        test_intents()
        
        # Testes assíncronos
        asyncio.run(test_messages())
        asyncio.run(test_conversation())
        
        print_header("TESTE CONCLUÍDO")
        print("✅ Todos os testes executados!")
        print("\n💡 Dicas:")
        print("   - Para usar OpenAI: configure OPENAI_API_KEY no .env")
        print("   - Para testar no site: acesse http://localhost:8000")
        print("   - Para ver logs: tail -f django.log")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()