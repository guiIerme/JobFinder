#!/usr/bin/env python
"""
Script para testar se a página de termos está acessível
Execute: python test_terms_access.py
"""

import os
import sys

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')

import django
django.setup()

from django.test import Client
from django.urls import reverse

def test_terms_page():
    print("=" * 60)
    print("TESTE DE ACESSO À PÁGINA DE TERMOS")
    print("=" * 60)
    
    client = Client()
    
    # Testa a URL dos termos
    try:
        url = reverse('terms')
        print(f"\n✅ URL encontrada: {url}")
        
        # Faz uma requisição GET
        response = client.get(url)
        
        print(f"\n📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Página carregou com sucesso!")
            
            # Verifica o conteúdo
            content = response.content.decode('utf-8')
            
            checks = [
                ("Termos de Serviço", "Título da página"),
                ("Aceitação dos Termos", "Seção 1"),
                ("Descrição do Serviço", "Seção 2"),
                ("Cadastro e Conta", "Seção 3"),
                ("Job Finder", "Nome da plataforma"),
            ]
            
            print("\n" + "=" * 60)
            print("VERIFICAÇÕES DE CONTEÚDO:")
            print("=" * 60)
            
            all_found = True
            for text, description in checks:
                if text in content:
                    print(f"✅ {description}: ENCONTRADO")
                else:
                    print(f"❌ {description}: NÃO ENCONTRADO")
                    all_found = False
            
            if all_found:
                print("\n" + "=" * 60)
                print("✅ TODOS OS TESTES PASSARAM!")
                print("\nA página de termos está funcionando corretamente.")
                print(f"\nAcesse em: http://10.160.216.54:8000{url}")
                print("=" * 60)
            else:
                print("\n❌ Alguns conteúdos não foram encontrados!")
                
        elif response.status_code == 302:
            print(f"⚠️  Redirecionamento para: {response.url}")
            print("A página está redirecionando. Verifique o middleware.")
        elif response.status_code == 404:
            print("❌ Página não encontrada (404)")
        elif response.status_code == 500:
            print("❌ Erro no servidor (500)")
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_terms_page()
