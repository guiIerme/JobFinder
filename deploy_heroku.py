#!/usr/bin/env python3
"""
Script automático para deploy no Heroku
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

def check_heroku_cli():
    """Verifica se Heroku CLI está instalado"""
    return run_command("heroku --version", "Verificando Heroku CLI")

def check_git():
    """Verifica se Git está instalado"""
    return run_command("git --version", "Verificando Git")

def main():
    print("=" * 60)
    print("🚀 DEPLOY AUTOMÁTICO PARA HEROKU")
    print("=" * 60)
    print()
    
    # Verificar pré-requisitos
    print("📋 Verificando pré-requisitos...")
    
    if not check_git():
        print("❌ Git não encontrado! Instale o Git primeiro.")
        return
    
    if not check_heroku_cli():
        print("❌ Heroku CLI não encontrado!")
        print("📥 Baixe em: https://devcenter.heroku.com/articles/heroku-cli")
        return
    
    print()
    
    # Obter nome do app
    app_name = input("📝 Digite o nome do seu app no Heroku (ex: meu-site-servicos): ").strip()
    if not app_name:
        print("❌ Nome do app é obrigatório!")
        return
    
    print()
    print(f"🚀 Iniciando deploy para: {app_name}")
    print()
    
    # Passos do deploy
    steps = [
        ("git init", "Inicializando repositório Git"),
        ("git add .", "Adicionando arquivos ao Git"),
        ('git commit -m "Deploy inicial"', "Fazendo commit inicial"),
        (f"heroku create {app_name}", f"Criando app {app_name} no Heroku"),
        ("heroku addons:create heroku-postgresql:mini", "Adicionando PostgreSQL"),
        ("heroku addons:create heroku-redis:mini", "Adicionando Redis"),
        ("git push heroku main", "Fazendo deploy para Heroku"),
        ("heroku run python manage.py migrate", "Executando migrações"),
        ("heroku run python manage.py collectstatic --noinput", "Coletando arquivos estáticos"),
    ]
    
    # Executar passos
    for command, description in steps:
        if not run_command(command, description):
            print(f"\n❌ Falha no passo: {description}")
            print("🔧 Tente executar manualmente:")
            print(f"   {command}")
            
            continue_deploy = input("\n❓ Continuar mesmo assim? (s/n): ").lower()
            if continue_deploy != 's':
                print("⏹️ Deploy cancelado.")
                return
    
    print()
    print("=" * 60)
    print("🎉 DEPLOY CONCLUÍDO!")
    print("=" * 60)
    print(f"🌐 Seu site está disponível em: https://{app_name}.herokuapp.com")
    print()
    print("📋 Próximos passos:")
    print("1. ✅ Teste seu site no link acima")
    print("2. 🔧 Configure variáveis de ambiente se necessário:")
    print(f"   heroku config:set DJANGO_SETTINGS_MODULE=home_services.settings_production")
    print("3. 👤 Crie um superusuário:")
    print("   heroku run python manage.py createsuperuser")
    print("4. 📊 Monitore logs:")
    print("   heroku logs --tail")
    print()

if __name__ == "__main__":
    main()