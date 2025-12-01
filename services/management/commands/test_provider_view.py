"""
Comando para testar se o prestador vê as solicitações
"""
from django.core.management.base import BaseCommand
from services.models import ServiceRequestModal, UserProfile
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Testa visualização de solicitações por prestador'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username do prestador')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"\n=== TESTANDO PRESTADOR: {username} ===\n")
            
            # Verificar se é prestador
            try:
                profile = user.userprofile
                self.stdout.write(f"Tipo de usuário: {profile.user_type}")
                
                if profile.user_type != 'professional':
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠ ATENÇÃO: Este usuário NÃO é um prestador! Tipo: {profile.user_type}"
                        )
                    )
            except:
                self.stdout.write(self.style.ERROR("❌ Usuário não tem perfil"))
            
            # Buscar solicitações para este prestador
            solicitacoes = ServiceRequestModal.objects.filter(provider=user).order_by('-created_at')
            
            self.stdout.write(f"\n=== SOLICITAÇÕES PARA {username} ===")
            self.stdout.write(f"Total: {solicitacoes.count()}\n")
            
            if solicitacoes.exists():
                for sol in solicitacoes:
                    self.stdout.write(f"\nID: {sol.id}")
                    self.stdout.write(f"Serviço: {sol.service_name}")
                    self.stdout.write(f"Cliente: {sol.contact_name} ({sol.user.username})")
                    self.stdout.write(f"Status: {sol.status}")
                    self.stdout.write(f"Data: {sol.preferred_date}")
                    self.stdout.write(f"Criado em: {sol.created_at}")
                    self.stdout.write("-" * 50)
                
                # Contar por status
                pending = solicitacoes.filter(status='pending').count()
                scheduled = solicitacoes.filter(status='scheduled').count()
                completed = solicitacoes.filter(status='completed').count()
                
                self.stdout.write(f"\n=== POR STATUS ===")
                self.stdout.write(f"Pendentes: {pending}")
                self.stdout.write(f"Agendadas: {scheduled}")
                self.stdout.write(f"Concluídas: {completed}")
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "\n⚠ Nenhuma solicitação encontrada para este prestador"
                    )
                )
                
                # Verificar se há solicitações sem provider
                sem_provider = ServiceRequestModal.objects.filter(provider__isnull=True).count()
                if sem_provider > 0:
                    self.stdout.write(
                        self.style.ERROR(
                            f"\n❌ Existem {sem_provider} solicitações SEM PROVIDER no sistema!"
                        )
                    )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Usuário '{username}' não encontrado"
                )
            )
