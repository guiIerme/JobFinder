#!/usr/bin/env python
"""
Script para testar se o template de registro está correto
Execute: python test_template_register.py
"""

import os
import sys

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')

import django
django.setup()

from django.template.loader import get_template
from django.template import Context

def test_register_template():
    print("=" * 60)
    print("TESTE DO TEMPLATE DE REGISTRO")
    print("=" * 60)
    
    try:
        # Carrega o template
        template = get_template('services/register.html')
        print("✅ Template carregado com sucesso!")
        
        # Renderiza o template
        html = template.render({})
        
        # Verifica se os termos estão presentes
        checks = [
            ("Termos e Privacidade", "Título da seção de termos"),
            ("Termos de Serviço", "Link para termos"),
            ("Política de Privacidade", "Link para política"),
            ("Li e concordo", "Texto do checkbox"),
            ("alert alert-info", "Caixa de alerta azul"),
            ("form-check", "Checkbox de termos"),
        ]
        
        print("\n" + "=" * 60)
        print("VERIFICAÇÕES:")
        print("=" * 60)
        
        all_passed = True
        for text, description in checks:
            if text in html:
                print(f"✅ {description}: ENCONTRADO")
            else:
                print(f"❌ {description}: NÃO ENCONTRADO")
                all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("✅ TODOS OS TESTES PASSARAM!")
            print("\nO template está correto. Se não aparecer no navegador:")
            print("1. Reinicie o servidor Django (Ctrl+C e python manage.py runserver)")
            print("2. Limpe o cache do navegador (Ctrl+Shift+Delete)")
            print("3. Faça um hard refresh (Ctrl+F5)")
        else:
            print("❌ ALGUNS TESTES FALHARAM!")
            print("\nO template pode estar com problemas.")
        print("=" * 60)
        
        # Mostra um trecho do HTML gerado
        print("\n" + "=" * 60)
        print("TRECHO DO HTML GERADO (primeiros 500 caracteres):")
        print("=" * 60)
        
        # Procura pela seção de termos
        if "Termos e Privacidade" in html:
            start = html.find("Termos e Privacidade") - 100
            end = start + 600
            print(html[start:end])
        else:
            print(html[:500])
        
    except Exception as e:
        print(f"❌ ERRO ao carregar template: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_register_template()
