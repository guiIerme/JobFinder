#!/usr/bin/env python
"""
Teste simples de conexão WebSocket
"""

import asyncio
import websockets
import json
import sys

async def test_websocket():
    """Testa conexão WebSocket"""
    uri = "ws://localhost:8000/ws/chat/"
    
    try:
        print(f"🔌 Tentando conectar ao WebSocket: {uri}")
        
        # Adicionar headers necessários
        headers = [("Origin", "http://localhost:8000")]
        
        async with websockets.connect(uri, additional_headers=headers) as websocket:
            print("✅ Conexão WebSocket estabelecida!")
            
            # Aguardar mensagem de boas-vindas
            try:
                welcome_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Mensagem recebida: {welcome_msg}")
                
                # Tentar inicializar sessão
                init_msg = {
                    "type": "session_init",
                    "context": {
                        "current_page": "/test",
                        "user_agent": "test-client"
                    }
                }
                
                await websocket.send(json.dumps(init_msg))
                print(f"📤 Mensagem enviada: {init_msg}")
                
                # Aguardar resposta
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Resposta recebida: {response}")
                
                # Enviar mensagem de teste
                test_msg = {
                    "type": "message",
                    "content": "Olá, Sophie!"
                }
                
                await websocket.send(json.dumps(test_msg))
                print(f"📤 Mensagem de teste enviada: {test_msg}")
                
                # Aguardar resposta da Sophie
                sophie_response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"🤖 Resposta da Sophie: {sophie_response}")
                
                print("✅ Teste WebSocket concluído com sucesso!")
                return True
                
            except asyncio.TimeoutError:
                print("⏰ Timeout aguardando resposta")
                return False
                
    except ConnectionRefusedError:
        print("❌ Conexão recusada - servidor não está rodando?")
        return False
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Código de status inválido: {e}")
        return False
    except websockets.exceptions.InvalidHandshake as e:
        print(f"❌ Handshake inválido: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE DE CONEXÃO WEBSOCKET")
    print("=" * 40)
    
    try:
        result = asyncio.run(test_websocket())
        
        if result:
            print("\n🎉 WebSocket está funcionando corretamente!")
            print("💡 Se o chat no navegador não funciona, tente:")
            print("   - Recarregar a página (Ctrl+F5)")
            print("   - Abrir uma aba anônima")
            print("   - Verificar o console do navegador (F12)")
        else:
            print("\n⚠️ WebSocket não está funcionando corretamente")
            print("💡 Possíveis soluções:")
            print("   - Verificar se o servidor Django está rodando")
            print("   - Verificar logs do servidor")
            print("   - Verificar configurações de CORS")
            
        return result
        
    except KeyboardInterrupt:
        print("\n⏹️ Teste interrompido pelo usuário")
        return False
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)