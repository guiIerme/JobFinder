"""
Script para corrigir solicitações existentes sem provider
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

from services.models import ServiceRequestModal

def fix_existing_requests():
    """Atualiza solicitações existentes para adicionar o provider"""
    
    # Buscar todas as solicitações sem provider
    requests_without_provider = ServiceRequestModal.objects.filter(provider__isnull=True)
    
    print(f"Encontradas {requests_without_provider.count()} solicitações sem provider")
    
    updated_count = 0
    error_count = 0
    
    for request in requests_without_provider:
        try:
            # Tentar obter o provider através do serviço
            if request.service and request.service.provider:
                request.provider = request.service.provider
                request.save()
                updated_count += 1
                print(f"✓ Solicitação #{request.id} atualizada: provider={request.provider.username}")
            else:
                error_count += 1
                print(f"✗ Solicitação #{request.id}: Não foi possível identificar o provider (service={request.service})")
        except Exception as e:
            error_count += 1
            print(f"✗ Erro ao atualizar solicitação #{request.id}: {str(e)}")
    
    print(f"\n=== RESUMO ===")
    print(f"Total de solicitações: {requests_without_provider.count()}")
    print(f"Atualizadas com sucesso: {updated_count}")
    print(f"Erros: {error_count}")
    
    # Verificar resultado
    remaining = ServiceRequestModal.objects.filter(provider__isnull=True).count()
    print(f"Solicitações ainda sem provider: {remaining}")

if __name__ == '__main__':
    fix_existing_requests()
