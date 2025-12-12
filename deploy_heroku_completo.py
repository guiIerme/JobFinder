#!/usr/bin/env python3
"""
Deploy completo no Heroku - Do zero ao ar!
"""

import subprocess
import sys
import os
import time

def print_step(step, description):
    """Imprime o passo atual"""
    print(f"\n{'='*60}")
    print(f"🔥 PASSO {step}: {description}")
    print(f"{'='*60}")

def run_command(command, description="", check_error=True):
    """Executa um comando e mostra o resultado"""
    if description:
        print(f"🔄 {description}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Sucesso!")
            if result.stdout.strip():
                print(f"📄 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Erro!")
            if result.stderr.strip():
                print(f"🚨 Erro: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Exceção: {e}")
        return False

def check_prerequisites():
    """Verifica pré-requisitos"""
    print_step(1, "VERIFICANDO PRÉ-REQUISITOS")
    
    # Verificar Git
    if not run_command("git --version", "Verificando Git"):
        print("❌ Git não encontrado! Instale: https://git-scm.com/")
        return False
    
    # Verificar Heroku CLI
    if not run_command("heroku --version", "Verificando Heroku CLI"):
        print("❌ Heroku CLI não encontrado!")
        print("📥 Instale: https://devcenter.heroku.com/articles/heroku-cli")
        return False
    
    # Verificar se está logado no Heroku
    if not run_command("heroku auth:whoami", "Verificando login no Heroku"):
        print("🔑 Você precisa fazer login no Heroku")
        print("Execute: heroku login")
        return False
    
    return True

def prepare_project():
    """Prepara o projeto para deploy"""
    print_step(2, "PREPARANDO PROJETO")
    
    # Verificar se já é um repositório Git
    if not os.path.exists('.git'):
        run_command("git init", "Inicializando repositório Git")
    
    # Adicionar arquivos
    run_command("git add .", "Adicionando arquivos ao Git")
    
    # Fazer commit
    run_command('git commit -m "Deploy para Heroku"', "Fazendo commit")
    
    return True

def create_heroku_app():
    """Cria app no Heroku"""
    print_step(3, "CRIANDO APP NO HEROKU")
    
    # Pedir nome do app
    print("📝 Escolha um nome para seu app (ou deixe em branco para nome aleatório):")
    app_name = input("Nome do app: ").strip()
    
    if app_name:
        command = f"heroku create {app_name}"
        description = f"Criando app '{app_name}'"
    else:
        command = "heroku create"
        description = "Criando app com nome aleatório"
    
    if run_command(command, description):
        # Extrair nome do app se foi aleatório
        if not app_name:
            result = subprocess.run("heroku apps:info --json", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                import json
                app_info = json.loads(result.stdout)
                app_name = app_info.get('name', 'seu-app')
        
        print(f"🎉 App criado! URL: https://{app_name}.herokuapp.com")
        return app_name
    
    return None

def add_addons():
    """Adiciona PostgreSQL e Redis"""
    print_step(4, "ADICIONANDO BANCO DE DADOS E REDIS")
    
    # Adicionar PostgreSQL
    run_command("heroku addons:create heroku-postgresql:mini", "Adicionando PostgreSQL")
    
    # Adicionar Redis
    run_command("heroku addons:create heroku-redis:mini", "Adicionando Redis")
    
    return True

def configure_environment():
    """Configura variáveis de ambiente"""
    print_step(5, "CONFIGURANDO VARIÁVEIS DE AMBIENTE")
    
    # Configurar Django
    run_command("heroku config:set DEBUG=False", "Configurando DEBUG=False")
    run_command("heroku config:set DJANGO_SETTINGS_MODULE=home_services.settings", "Configurando settings")
    
    return True

def deploy_code():
    """Faz deploy do código"""
    print_step(6, "FAZENDO DEPLOY DO CÓDIGO")
    
    print("🚀 Enviando código para Heroku... (isso pode demorar alguns minutos)")
    
    # Tentar main primeiro, depois master
    if not run_command("git push heroku main", "Deploy via branch main"):
        print("🔄 Tentando branch master...")
        run_command("git push heroku master", "Deploy via branch master")
    
    return True

def setup_database():
    """Configura banco de dados"""
    print_step(7, "CONFIGURANDO BANCO DE DADOS")
    
    # Executar migrações
    run_command("heroku run python manage.py migrate", "Executando migrações")
    
    # Coletar arquivos estáticos
    run_command("heroku run python manage.py collectstatic --noinput", "Coletando arquivos estáticos")
    
    return True

def create_superuser():
    """Cria superusuário"""
    print_step(8, "CRIANDO USUÁRIO ADMINISTRADOR")
    
    print("👤 Vamos criar um usuário administrador para seu site")
    print("🔄 Execute o comando abaixo e siga as instruções:")
    print("heroku run python manage.py createsuperuser")
    
    create_now = input("\n❓ Criar agora? (s/n): ").lower()
    if create_now == 's':
        os.system("heroku run python manage.py createsuperuser")
    
    return True

def final_steps(app_name):
    """Passos finais"""
    print_step(9, "FINALIZANDO")
    
    print("🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
    print(f"🌐 Seu site está disponível em: https://{app_name}.herokuapp.com")
    print()
    print("📋 COMANDOS ÚTEIS:")
    print("• Ver logs: heroku logs --tail")
    print("• Abrir site: heroku open")
    print("• Status: heroku ps")
    print("• Reiniciar: heroku restart")
    print()
    
    open_site = input("🌐 Abrir seu site agora? (s/n): ").lower()
    if open_site == 's':
        run_command("heroku open", "Abrindo site no navegador")

def main():
    """Função principal"""
    print("🔥 DEPLOY HEROKU - DO ZERO AO AR!")
    print("=" * 60)
    print()
    
    try:
        # Verificar pré-requisitos
        if not check_prerequisites():
            return
        
        # Preparar projeto
        if not prepare_project():
            return
        
        # Criar app
        app_name = create_heroku_app()
        if not app_name:
            return
        
        # Adicionar addons
        if not add_addons():
            return
        
        # Configurar ambiente
        if not configure_environment():
            return
        
        # Deploy
        if not deploy_code():
            return
        
        # Configurar banco
        if not setup_database():
            return
        
        # Criar superuser
        if not create_superuser():
            return
        
        # Finalizar
        final_steps(app_name)
        
    except KeyboardInterrupt:
        print("\n⏹️ Deploy cancelado pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()