#!/usr/bin/env python3
"""
Script para criar link público para o site Django
Suporta múltiplas opções de tunneling
"""

import subprocess
import sys
import time
import threading
import os
import requests
from urllib.parse import urlparse

def check_django_running(port=8000):
    """Verifica se o Django está rodando na porta especificada"""
    try:
        response = requests.get(f'http://localhost:{port}', timeout=5)
        return True
    except:
        return False

def start_django_server(port=8000):
    """Inicia o servidor Django"""
    print(f"🚀 Iniciando servidor Django na porta {port}...")
    try:
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', f'0.0.0.0:{port}'
        ], check=True)
    except KeyboardInterrupt:
        print("\n✅ Servidor Django parado.")
    except Exception as e:
        print(f"❌ Erro ao iniciar Django: {e}")

def check_ngrok():
    """Verifica se ngrok está instalado"""
    try:
        result = subprocess.run(['ngrok', 'version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def start_ngrok(port=8000):
    """Inicia ngrok"""
    if not check_ngrok():
        print("❌ Ngrok não encontrado!")
        print("📥 Baixe em: https://ngrok.com/")
        print("⚙️  Configure com: ngrok authtoken SEU_TOKEN")
        return False
    
    print(f"🌐 Iniciando ngrok na porta {port}...")
    try:
        subprocess.run(['ngrok', 'http', str(port)], check=True)
    except KeyboardInterrupt:
        print("\n✅ Ngrok parado.")
    except Exception as e:
        print(f"❌ Erro no ngrok: {e}")
    return True

def start_serveo(port=8000):
    """Inicia serveo via SSH"""
    print(f"🌐 Criando túnel público via Serveo (porta {port})...")
    print("📝 Seu link público aparecerá abaixo:")
    try:
        subprocess.run([
            'ssh', '-R', f'80:localhost:{port}', 'serveo.net'
        ], check=True)
    except KeyboardInterrupt:
        print("\n✅ Serveo parado.")
    except Exception as e:
        print(f"❌ Erro no serveo: {e}")

def get_public_ip():
    """Obtém o IP público"""
    try:
        response = requests.get('https://api.ipify.org', timeout=10)
        return response.text.strip()
    except:
        try:
            response = requests.get('https://ifconfig.me', timeout=10)
            return response.text.strip()
        except:
            return "Não foi possível obter o IP público"

def main():
    print("=" * 50)
    print("🌐 CRIADOR DE LINK PÚBLICO PARA DJANGO")
    print("=" * 50)
    print()
    
    # Verificar se Django está rodando
    if check_django_running():
        print("✅ Django já está rodando em http://localhost:8000")
    else:
        print("⚠️  Django não está rodando")
    
    print()
    print("📋 OPÇÕES DISPONÍVEIS:")
    print("1. 🚀 Iniciar apenas Django (localhost)")
    print("2. 🌐 Django + Ngrok (público)")
    print("3. 🌐 Django + Serveo (público, sem instalação)")
    print("4. 📊 Mostrar status atual")
    print("5. 🌍 Mostrar IP público")
    print("6. ❌ Sair")
    print()
    
    try:
        choice = input("Escolha uma opção (1-6): ").strip()
        
        if choice == '1':
            start_django_server()
            
        elif choice == '2':
            if not check_django_running():
                print("⚠️  Inicie o Django primeiro em outro terminal:")
                print("   python manage.py runserver 0.0.0.0:8000")
                input("Pressione Enter quando o Django estiver rodando...")
            
            if check_django_running():
                start_ngrok()
            else:
                print("❌ Django não está rodando!")
                
        elif choice == '3':
            if not check_django_running():
                print("⚠️  Inicie o Django primeiro em outro terminal:")
                print("   python manage.py runserver 0.0.0.0:8000")
                input("Pressione Enter quando o Django estiver rodando...")
            
            if check_django_running():
                start_serveo()
            else:
                print("❌ Django não está rodando!")
                
        elif choice == '4':
            print("\n📊 STATUS ATUAL:")
            print(f"Django (porta 8000): {'✅ Rodando' if check_django_running() else '❌ Parado'}")
            print(f"Ngrok disponível: {'✅ Sim' if check_ngrok() else '❌ Não'}")
            print(f"IP público: {get_public_ip()}")
            
        elif choice == '5':
            ip = get_public_ip()
            print(f"\n🌍 Seu IP público: {ip}")
            print(f"🔗 Link direto (se port forwarding configurado): http://{ip}:8000")
            print("⚠️  Nota: Precisa configurar port forwarding no roteador")
            
        elif choice == '6':
            print("👋 Até logo!")
            return
            
        else:
            print("❌ Opção inválida!")
            
    except KeyboardInterrupt:
        print("\n👋 Script interrompido pelo usuário.")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()