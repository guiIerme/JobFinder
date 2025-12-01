import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from services.models import CustomService, UserProfile

class Command(BaseCommand):
    help = 'Create sample custom services for testing'

    def handle(self, *args, **options):
        # Create sample providers if they don't exist
        providers = []
        for i in range(3):
            username = f'provider{i+1}'
            try:
                provider = User.objects.get(username=username)
            except User.DoesNotExist:
                provider = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='password123'
                )
                # Create user profile if needed
                try:
                    UserProfile.objects.create(
                        user=provider,
                        user_type='professional'
                    )
                except:
                    pass
            providers.append(provider)

        # Create sample custom services
        services_data = [
            {
                'name': 'Reparo de Encanamento',
                'description': 'Reparos em encanamentos residenciais, vazamentos, torneiras, ralos e tubulações.',
                'category': 'plumbing',
                'estimated_price': 150.00,
            },
            {
                'name': 'Instalação Elétrica',
                'description': 'Instalação e manutenção de sistemas elétricos residenciais, troca de tomadas, disjuntores e iluminação.',
                'category': 'electrical',
                'estimated_price': 200.00,
            },
            {
                'name': 'Pintura Residencial',
                'description': 'Pintura de paredes internas e externas, texturização e acabamento profissional.',
                'category': 'painting',
                'estimated_price': 300.00,
            },
            {
                'name': 'Montagem de Móveis',
                'description': 'Montagem de móveis pré-fabricados, estantes, armários e equipamentos.',
                'category': 'assembly',
                'estimated_price': 120.00,
            },
            {
                'name': 'Limpeza Pós-Obras',
                'description': 'Limpeza profunda após reformas e construções, remoção de entulho e sujeiras difíceis.',
                'category': 'cleaning',
                'estimated_price': 250.00,
            },
            {
                'name': 'Reparos Gerais',
                'description': 'Serviços variados de manutenção predial, substituição de peças e reparos em geral.',
                'category': 'repair',
                'estimated_price': 180.00,
            }
        ]

        # Create services
        created_count = 0
        for service_data in services_data:
            # Randomly assign to one of the providers
            provider = random.choice(providers)
            
            # Check if service already exists
            if not CustomService.objects.filter(
                name=service_data['name'],
                provider=provider
            ).exists():
                CustomService.objects.create(
                    name=service_data['name'],
                    description=service_data['description'],
                    category=service_data['category'],
                    estimated_price=service_data['estimated_price'],
                    provider=provider,
                    is_active=True
                )
                self.stdout.write(
                    f'Successfully created service "{service_data["name"]}" for provider {provider.username}'
                )
                created_count += 1
            else:
                self.stdout.write(
                    f'Service "{service_data["name"]}" for provider {provider.username} already exists'
                )

        self.stdout.write(
            f'Successfully created/verified {created_count} sample services'
        )