import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from services.models import Service, Sponsor, UserProfile, CustomService

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        # Create sample services
        services_data = [
            {
                'name': 'Reparo de Encanamento',
                'description': 'Reparos em encanamentos, vazamentos, torneiras, ralos e canos.',
                'category': 'plumbing',
                'base_price': 150.00,
            },
            {
                'name': 'Montagem de Móveis',
                'description': 'Montagem de móveis como armários, estantes, camas e mesas.',
                'category': 'assembly',
                'base_price': 120.00,
            },
            {
                'name': 'Instalação Elétrica',
                'description': 'Instalação de pontos elétricos, troca de tomadas e disjuntores.',
                'category': 'electrical',
                'base_price': 200.00,
            },
            {
                'name': 'Pintura Residencial',
                'description': 'Pintura de paredes internas e externas, textura e acabamento.',
                'category': 'painting',
                'base_price': 300.00,
            },
            {
                'name': 'Limpeza Pós-Obra',
                'description': 'Limpeza completa após reformas e obras, remoção de entulho.',
                'category': 'cleaning',
                'base_price': 250.00,
            },
            {
                'name': 'Conserto de Eletrodomésticos',
                'description': 'Conserto de geladeiras, máquinas de lavar, micro-ondas e fogões.',
                'category': 'repair',
                'base_price': 180.00,
            }
        ]

        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            if created:
                self.stdout.write(f'Created service: {service.name}')
            else:
                self.stdout.write(f'Service already exists: {service.name}')

        # Create sample sponsors
        sponsors_data = [
            {
                'name': 'Construtora Alfa',
                'description': 'Especializada em reformas e construções residenciais.',
                'website': 'https://construtoraalfa.com.br',
                'is_active': True
            },
            {
                'name': 'Elétrica Beta',
                'description': 'Instalações e manutenções elétricas de alta qualidade.',
                'website': 'https://eletricabeta.com.br',
                'is_active': True
            },
            {
                'name': 'Hidráulica Gamma',
                'description': 'Soluções completas para sistemas hidráulicos.',
                'website': 'https://hidraulicagamma.com.br',
                'is_active': True
            }
        ]

        for sponsor_data in sponsors_data:
            sponsor, created = Sponsor.objects.get_or_create(
                name=sponsor_data['name'],
                defaults=sponsor_data
            )
            if created:
                self.stdout.write(f'Created sponsor: {sponsor.name}')
            else:
                self.stdout.write(f'Sponsor already exists: {sponsor.name}')

        # Create sample professionals
        professionals_data = [
            {'username': 'joao_eletricista', 'email': 'joao@eletricista.com', 'password': 'password123', 'first_name': 'João', 'last_name': 'Silva'},
            {'username': 'maria_encanadora', 'email': 'maria@encanadora.com', 'password': 'password123', 'first_name': 'Maria', 'last_name': 'Santos'},
            {'username': 'pedro_pintor', 'email': 'pedro@pintor.com', 'password': 'password123', 'first_name': 'Pedro', 'last_name': 'Oliveira'},
            {'username': 'ana_limpeza', 'email': 'ana@limpeza.com', 'password': 'password123', 'first_name': 'Ana', 'last_name': 'Costa'},
            {'username': 'carlos_montador', 'email': 'carlos@montador.com', 'password': 'password123', 'first_name': 'Carlos', 'last_name': 'Pereira'},
            {'username': 'lucia_jardineira', 'email': 'lucia@jardineira.com', 'password': 'password123', 'first_name': 'Lúcia', 'last_name': 'Rodrigues'},
            {'username': 'roberto_dedetizador', 'email': 'roberto@dedetizador.com', 'password': 'password123', 'first_name': 'Roberto', 'last_name': 'Almeida'},
            {'username': 'fernanda_babysitter', 'email': 'fernanda@babysitter.com', 'password': 'password123', 'first_name': 'Fernanda', 'last_name': 'Gomes'},
        ]

        for prof_data in professionals_data:
            user, created = User.objects.get_or_create(
                username=prof_data['username'],
                defaults={
                    'email': prof_data['email'],
                    'first_name': prof_data.get('first_name', ''),
                    'last_name': prof_data.get('last_name', '')
                }
            )
            if created:
                user.set_password(prof_data['password'])
                user.save()
                # Create user profile
                UserProfile.objects.create(
                    user=user,
                    user_type='professional',
                    phone=f'+55119{random.randint(10000000, 99999999)}',
                    city=random.choice(['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília', 'Curitiba']),
                    state=random.choice(['SP', 'RJ', 'MG', 'DF', 'PR']),
                    rating=round(random.uniform(3.5, 5.0), 2),
                    review_count=random.randint(10, 100)
                )
                self.stdout.write(f'Created professional: {user.username}')
            else:
                self.stdout.write(f'Professional already exists: {user.username}')

        # Create custom services for professionals
        custom_services_data = [
            # Electrical services
            {'name': 'Instalação de Ar Condicionado', 'description': 'Instalação completa de aparelhos de ar condicionado split, incluindo fiação e drenagem.', 'category': 'electrical', 'estimated_price': 450.00},
            {'name': 'Troca de Disjuntor', 'description': 'Substituição de disjuntores defeituosos e instalação de novos disjuntores.', 'category': 'electrical', 'estimated_price': 120.00},
            {'name': 'Instalação de Chuveiro Elétrico', 'description': 'Instalação de chuveiros elétricos com fiação adequada e segurança.', 'category': 'electrical', 'estimated_price': 200.00},
            
            # Plumbing services
            {'name': 'Desentupimento de Esgoto', 'description': 'Desentupimento de tubulações de esgoto residenciais e comerciais.', 'category': 'plumbing', 'estimated_price': 180.00},
            {'name': 'Instalação de Box', 'description': 'Instalação de boxes de vidro temperado para banheiros.', 'category': 'plumbing', 'estimated_price': 350.00},
            {'name': 'Reparo de Vazamento', 'description': 'Localização e reparo de vazamentos em tubulações de água.', 'category': 'plumbing', 'estimated_price': 220.00},
            
            # Painting services
            {'name': 'Pintura de Fachada', 'description': 'Pintura de fachadas com preparação de superfície e acabamento duradouro.', 'category': 'painting', 'estimated_price': 800.00},
            {'name': 'Textura 3D', 'description': 'Aplicação de texturas 3D em paredes para efeito decorativo.', 'category': 'painting', 'estimated_price': 500.00},
            {'name': 'Pintura de Galpão', 'description': 'Pintura industrial de galpões e estruturas metálicas.', 'category': 'painting', 'estimated_price': 1200.00},
            
            # Cleaning services
            {'name': 'Limpeza de Caixa d\'Água', 'description': 'Limpeza e desinfecção completa de caixas d\'água residenciais.', 'category': 'cleaning', 'estimated_price': 300.00},
            {'name': 'Limpeza Pós-Incêndio', 'description': 'Limpeza especializada após sinistros com remoção de fuligem e odores.', 'category': 'cleaning', 'estimated_price': 1500.00},
            {'name': 'Higienização de Estofados', 'description': 'Higienização de sofás, cadeiras e colchões com equipamentos profissionais.', 'category': 'cleaning', 'estimated_price': 250.00},
            
            # Assembly services
            {'name': 'Montagem de Home Theater', 'description': 'Montagem e configuração completa de sistemas de home theater.', 'category': 'assembly', 'estimated_price': 400.00},
            {'name': 'Instalação de Persiana', 'description': 'Instalação de persianas e cortinas automatizadas.', 'category': 'assembly', 'estimated_price': 180.00},
            {'name': 'Montagem de Cozinha Planejada', 'description': 'Montagem de móveis de cozinha planejada com ajustes finos.', 'category': 'assembly', 'estimated_price': 600.00},
            
            # Repair services
            {'name': 'Conserto de Máquina de Lavar', 'description': 'Diagnóstico e reparo de máquinas de lavar roupas e louças.', 'category': 'repair', 'estimated_price': 180.00},
            {'name': 'Reparo de Portão Automático', 'description': 'Manutenção e reparo de portões automatizados e seus mecanismos.', 'category': 'repair', 'estimated_price': 300.00},
            {'name': 'Conserto de Computador', 'description': 'Manutenção e reparo de computadores desktop e notebooks.', 'category': 'repair', 'estimated_price': 150.00},
            
            # Other services
            {'name': 'Jardinagem Residencial', 'description': 'Manutenção de jardins, podas e tratamento de plantas.', 'category': 'other', 'estimated_price': 200.00},
            {'name': 'Dedetização Completa', 'description': 'Dedetização de residências e comércios contra insetos e roedores.', 'category': 'other', 'estimated_price': 400.00},
            {'name': 'Babysitter Profissional', 'description': 'Cuidado com crianças com experiência em primeiros socorros.', 'category': 'other', 'estimated_price': 80.00},
        ]

        # Get all professional users
        professionals = User.objects.filter(userprofile__user_type='professional')
        
        # Create custom services for each professional
        for professional in professionals:
            # Each professional gets 3-5 random services
            num_services = random.randint(3, 5)
            selected_services = random.sample(custom_services_data, min(num_services, len(custom_services_data)))
            
            for service_data in selected_services:
                # Randomize price slightly
                service_data['estimated_price'] = round(float(service_data['estimated_price']) * random.uniform(0.8, 1.3), 2)
                
                # Create custom service
                custom_service = CustomService.objects.create(
                    name=service_data['name'],
                    description=service_data['description'],
                    category=service_data['category'],
                    estimated_price=service_data['estimated_price'],
                    provider=professional
                )
                self.stdout.write(f'Created custom service: {custom_service.name} for {professional.username}')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data')
        )