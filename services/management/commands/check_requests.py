"""
Comando Django para verificar solicitações recentes
"""
from django.core.management.base import BaseCommand
from services.models import ServiceRequestModal
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Verifica as últimas solicitações criadas'

    def handle(self, *args, **options):
        """Mostra as últimas 5 solicitações"""
        
        # Buscar últimas 5 solicitações
        recent_requests = ServiceRequestModal.objects.all().order_by('-created_at')[:5]
        
        self.stdout.write(f"\n=== ÚLTIMAS 5 SOLICITAÇÕES ===\n")
        
        for req in recent_requests:
            self.stdout.write(f"\nID: {req.id}")
            self.stdout.write(f"Serviço: {req.service_name}")
            self.stdout.write(f"Cliente: {req.user.username} (ID: {req.user.id})")
            
            if req.provider:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Prestador: {req.provider.username} (ID: {req.provider.id})"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Prestador: NENHUM ❌"
                    )
                )
            
            self.stdout.write(f"Status: {req.status}")
            self.stdout.write(f"Data: {req.preferred_date}")
            self.stdout.write(f"Criado em: {req.created_at}")
            
            if req.service:
                self.stdout.write(f"Serviço associado: {req.service.name} (Provider: {req.service.provider.username})")
            else:
                self.stdout.write(self.style.WARNING("Serviço associado: NENHUM"))
            
            self.stdout.write("-" * 50)
        
        # Estatísticas
        total = ServiceRequestModal.objects.count()
        with_provider = ServiceRequestModal.objects.filter(provider__isnull=False).count()
        without_provider = ServiceRequestModal.objects.filter(provider__isnull=True).count()
        
        self.stdout.write(f"\n=== ESTATÍSTICAS ===")
        self.stdout.write(f"Total de solicitações: {total}")
        self.stdout.write(self.style.SUCCESS(f"Com provider: {with_provider}"))
        self.stdout.write(self.style.ERROR(f"Sem provider: {without_provider}"))
