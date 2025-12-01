"""
Comando Django para corrigir solicitações existentes sem provider
"""
from django.core.management.base import BaseCommand
from services.models import ServiceRequestModal


class Command(BaseCommand):
    help = 'Corrige solicitações existentes adicionando o campo provider'

    def handle(self, *args, **options):
        """Atualiza solicitações existentes para adicionar o provider"""
        
        # Buscar todas as solicitações sem provider
        requests_without_provider = ServiceRequestModal.objects.filter(provider__isnull=True)
        
        total = requests_without_provider.count()
        self.stdout.write(f"Encontradas {total} solicitações sem provider")
        
        updated_count = 0
        error_count = 0
        
        for request in requests_without_provider:
            try:
                # Tentar obter o provider através do serviço
                if request.service and request.service.provider:
                    request.provider = request.service.provider
                    request.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Solicitação #{request.id} atualizada: provider={request.provider.username}"
                        )
                    )
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"✗ Solicitação #{request.id}: Não foi possível identificar o provider (service={request.service})"
                        )
                    )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Erro ao atualizar solicitação #{request.id}: {str(e)}"
                    )
                )
        
        self.stdout.write("\n=== RESUMO ===")
        self.stdout.write(f"Total de solicitações: {total}")
        self.stdout.write(self.style.SUCCESS(f"Atualizadas com sucesso: {updated_count}"))
        self.stdout.write(self.style.ERROR(f"Erros: {error_count}"))
        
        # Verificar resultado
        remaining = ServiceRequestModal.objects.filter(provider__isnull=True).count()
        self.stdout.write(f"Solicitações ainda sem provider: {remaining}")
        
        if remaining == 0:
            self.stdout.write(self.style.SUCCESS("\n✓ Todas as solicitações foram corrigidas!"))
        else:
            self.stdout.write(self.style.WARNING(f"\n⚠ Ainda há {remaining} solicitações sem provider"))
