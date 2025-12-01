#!/usr/bin/env python
"""
Script para testar se as credenciais OAuth são válidas
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_credentials():
    print("\n🔍 Testando credenciais OAuth...\n")
    
    credentials = {
        'Google': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET', '')
        },
        'Facebook': {
            'client_id': os.environ.get('FACEBOOK_CLIENT_ID', ''),
            'secret': os.environ.get('FACEBOOK_CLIENT_SECRET', '')
        },
        'Microsoft': {
            'client_id': os.environ.get('MICROSOFT_CLIENT_ID', ''),
            'secret': os.environ.get('MICROSOFT_CLIENT_SECRET', '')
        }
    }
    
    # Credenciais de exemplo que NÃO funcionam
    example_values = [
        'your_google_client_id',
        'your_google_client_secret',
        'your_facebook_app_id',
        'your_facebook_app_secret',
        'your_microsoft_client_id',
        'your_microsoft_client_secret',
        '',
        'here'
    ]
    
    all_valid = True
    
    for provider, creds in credentials.items():
        print(f"{'='*50}")
        print(f"📱 {provider}")
        print(f"{'='*50}")
        
        client_id = creds['client_id']
        secret = creds['secret']
        
        # Check Client ID
        if not client_id or any(ex in client_id.lower() for ex in example_values):
            print(f"❌ Client ID: INVÁLIDO (usando valor de exemplo)")
            all_valid = False
        else:
            print(f"✅ Client ID: Parece válido ({len(client_id)} caracteres)")
        
        # Check Secret
        if not secret or any(ex in secret.lower() for ex in example_values):
            print(f"❌ Secret: INVÁLIDO (usando valor de exemplo)")
            all_valid = False
        else:
            print(f"✅ Secret: Parece válido ({len(secret)} caracteres)")
        
        print()
    
    print(f"{'='*50}")
    print("RESULTADO")
    print(f"{'='*50}")
    
    if all_valid:
        print("✅ Todas as credenciais parecem válidas!")
        print("\n📋 Próximos passos:")
        print("1. Execute: python manage.py setup_social_auth")
        print("2. Inicie o servidor: python manage.py runserver")
        print("3. Teste: http://localhost:8000/login/")
    else:
        print("❌ Algumas credenciais são inválidas ou estão usando valores de exemplo!")
        print("\n📝 O que fazer:")
        print("1. Abra o arquivo .env")
        print("2. Substitua os valores de exemplo por credenciais REAIS")
        print("3. Consulte: GUIA_RAPIDO_CREDENCIAIS.md")
        print("\n💡 Dica: Comece apenas com o Google!")
        print("   É o mais fácil de configurar.")
    
    print()

if __name__ == '__main__':
    test_credentials()
