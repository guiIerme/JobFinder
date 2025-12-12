#!/usr/bin/env python3
"""
Script automático para deploy no Railway
"""

import subprocess
import sys
import os
import json

def run_command(command, description=""):
    """Executa um comando e mostra o resultado"""
    if description:
        print(f"🔄 {description}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Sucesso: {description}")
            if result.stdout.strip():
                print(f"   {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Erro: {description}")
            print(f"   {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Exceção: {e}")
        return False

def check_railway_cli():
    """Verifica se Railway CLI está instalado"""
    return run_command("railway --version", "Verificando Railway CLI")

def check_git():
    """Verifica se Git está instalado"""
    return run_command("git --version", "Verificando Git")

def create_railway_config():
    """Cria arquivo de configuração do Railway"""
    config = {
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "daphne home_services.asgi:application --port $PORT --bind 0.0.0.0",
            "healthcheckPath": "/",
            "healthcheckTimeout": 100
        }
    }
    
    try:
        with open('railway.json', 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Arquivo railway.json criado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar railway.json: {e}")
        return False

def main():
    print("=" * 60)
    print("🚂 DEPLOY AUTOMÁTICO PARA RAILWAY")
    print("=" * 60)
    print()
    
    # Verificar pré-requisitos
    print("📋 Verificando pré-requisitos...")
    
    if not check_git():
        print("❌ Git não encontrado! Instale o Git primeiro.")
        return
    
    if not check_railway_cli():
        print("❌ Railway CLI não encontrado!")
        print("📥 Instale com: npm install -g @railway/cli")
        print("🔗 Ou baixe em: https://railway.app/cli")
        return
    
    print()
    
    # Criar configuração do Railway
    if not create_railway_config():
        return
    
    print()
    print("🚀 Iniciando deploy para Railway...")
    print()
    
    # Passos do deploy
    steps = [
        ("git init", "Inicializando repositório Git"),
        ("git add .", "Adicionando arquivos ao Git"),
        ('git commit -m "Deploy inicial para Railway"', "Fazendo commit inicial"),
        ("railway login", "Fazendo login no Railway"),
        ("railway init", "Inicializando projeto Railway"),
        ("railway add --database postgresql", "Adicionando PostgreSQL"),
        ("railway add --database redis", "Adicionando Redis"),
        ("railway up", "Fazendo deploy para Railway"),
    ]
    
    # Executar passos
    for command, description in steps:
        if command == "railway login":
            print(f"🔄 {description}")
            print("🌐 Uma página web será aberta para login...")
            
        if not run_command(command, description):
            print(f"\n❌ Falha no passo: {description}")
            print("🔧 Tente executar manualmente:")
            print(f"   {command}")
            
            if command == "railway login":
                print("💡 Dica: Faça login manualmente com 'railway login'")
            
            continue_deploy = input("\n❓ Continuar mesmo assim? (s/n): ").lower()
            if continue_deploy != 's':
                print("⏹️ Deploy cancelado.")
                return
    
    print()
    print("=" * 60)
    print("🎉 DEPLOY CONCLUÍDO!")
    print("=" * 60)
    print("🌐 Seu site estará disponível em breve!")
    print()
    print("📋 Próximos passos:")
    print("1. ✅ Verifique o status: railway status")
    print("2. 🔗 Obtenha a URL: railway domain")
    print("3. 📊 Monitore logs: railway logs")
    print("4. 🔧 Configure variáveis: railway variables")
    print("5. 👤 Crie superusuário: railway run python manage.py createsuperuser")
    print()

if __name__ == "__main__":
    main()