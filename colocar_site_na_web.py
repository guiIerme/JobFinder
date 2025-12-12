#!/usr/bin/env python3
"""
Script Master - Colocar Site na Web
Escolha a plataforma e faça deploy automaticamente
"""

import subprocess
import sys
import os
import webbrowser

def print_header():
    print("=" * 60)
    print("🌐 COLOCAR SEU SITE NA WEB")
    print("=" * 60)
    print()

def print_options():
    print("🚀 ESCOLHA UMA PLATAFORMA:")
    print()
    print("1. 🚂 Railway (Recomendado - Mais fácil)")
    print("   ✅ $5/mês grátis")
    print("   ✅ Deploy em 2 minutos")
    print("   ✅ SSL automático")
    print()
    print("2. 🔥 Heroku (Clássico)")
    print("   ✅ 550 horas grátis/mês")
    print("   ✅ Muito documentado")
    print("   ✅ Comunidade grande")
    print()
    print("3. 🌟 Render (Moderno)")
    print("   ✅ Plano gratuito")
    print("   ✅ Deploy via GitHub")
    print("   ✅ Muito simples")
    print()
    print("4. 🐍 PythonAnywhere (Python especializado)")
    print("   ✅ Feito para Django")
    print("   ✅ Plano gratuito")
    print("   ✅ Fácil configuração")
    print()
    print("5. 📚 Ver guia completo")
    print("6. ❌ Sair")
    print()

def run_command(command):
    """Executa um comando"""
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except:
        return False

def deploy_railway():
    print("🚂 DEPLOY NO RAILWAY")
    print("=" * 40)
    print()
    
    # Verificar Node.js
    if not run_command("node --version"):
        print("❌ Node.js não encontrado!")
        print("📥 Baixe em: https://nodejs.org/")
        print("🔄 Depois execute: npm install -g @railway/cli")
        return
    
    # Instalar Railway CLI
    print("📦 Instalando Railway CLI...")
    if not run_command("npm install -g @railway/cli"):
        print("❌ Erro ao instalar Railway CLI")
        return
    
    # Executar script de deploy
    print("🚀 Iniciando deploy...")
    run_command("python deploy_railway.py")

def deploy_heroku():
    print("🔥 DEPLOY NO HEROKU")
    print("=" * 40)
    print()
    
    print("📋 Pré-requisitos:")
    print("1. Conta no Heroku: https://heroku.com")
    print("2. Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli")
    print()
    
    ready = input("✅ Já tem tudo instalado? (s/n): ").lower()
    if ready != 's':
        print("🔗 Abrir links de instalação...")
        webbrowser.open("https://heroku.com")
        webbrowser.open("https://devcenter.heroku.com/articles/heroku-cli")
        return
    
    # Executar script de deploy
    print("🚀 Iniciando deploy...")
    run_command("python deploy_heroku.py")

def deploy_render():
    print("🌟 DEPLOY NO RENDER")
    print("=" * 40)
    print()
    
    print("📋 Passos para Render:")
    print("1. ✅ Crie conta em: https://render.com")
    print("2. 📁 Faça push do código para GitHub")
    print("3. 🔗 No Render, clique 'New Web Service'")
    print("4. 📂 Conecte seu repositório GitHub")
    print("5. ⚙️ Configure:")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: daphne home_services.asgi:application --port $PORT --bind 0.0.0.0")
    print()
    
    open_render = input("🌐 Abrir Render.com? (s/n): ").lower()
    if open_render == 's':
        webbrowser.open("https://render.com")

def deploy_pythonanywhere():
    print("🐍 DEPLOY NO PYTHONANYWHERE")
    print("=" * 40)
    print()
    
    print("📋 Passos para PythonAnywhere:")
    print("1. ✅ Crie conta em: https://pythonanywhere.com")
    print("2. 📁 Faça upload do código")
    print("3. 🔧 Configure Web App")
    print("4. 🐍 Escolha Django")
    print("5. ⚙️ Configure paths e settings")
    print()
    
    open_pa = input("🌐 Abrir PythonAnywhere? (s/n): ").lower()
    if open_pa == 's':
        webbrowser.open("https://pythonanywhere.com")

def show_guide():
    print("📚 ABRINDO GUIA COMPLETO...")
    
    # Tentar abrir o arquivo
    guides = [
        "GUIA_DEPLOY_SIMPLES.md",
        "DEPLOY_WEB_COMPLETO.md"
    ]
    
    for guide in guides:
        if os.path.exists(guide):
            if sys.platform.startswith('win'):
                os.startfile(guide)
            else:
                run_command(f"open {guide}")
            break
    else:
        print("📄 Arquivos de guia criados:")
        print("- GUIA_DEPLOY_SIMPLES.md")
        print("- DEPLOY_WEB_COMPLETO.md")

def main():
    print_header()
    
    while True:
        print_options()
        
        try:
            choice = input("Escolha uma opção (1-6): ").strip()
            
            if choice == '1':
                deploy_railway()
            elif choice == '2':
                deploy_heroku()
            elif choice == '3':
                deploy_render()
            elif choice == '4':
                deploy_pythonanywhere()
            elif choice == '5':
                show_guide()
            elif choice == '6':
                print("👋 Até logo!")
                break
            else:
                print("❌ Opção inválida!")
                continue
            
            print()
            continue_menu = input("🔄 Voltar ao menu? (s/n): ").lower()
            if continue_menu != 's':
                break
                
        except KeyboardInterrupt:
            print("\n👋 Script interrompido.")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()