import json
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from services.models import Service, CustomService, UserProfile, Order, Sponsor
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Import sample data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing data before importing',
        )

    def handle(self, *args, **options):
        if options['clear_existing']:
            self.stdout.write('Clearing existing data...')
            self.clear_existing_data()

        self.stdout.write('Importing sample data...')
        
        # Create sample users
        self.create_sample_users()
        
        # Create sample services
        self.create_sample_services()
        
        # Create sample sponsors
        self.create_sample_sponsors()
        
        # Create sample custom services
        self.create_sample_custom_services()
        
        # Create sample orders
        self.create_sample_orders()
        
        self.stdout.write(
            'Successfully imported sample data'
        )

    def clear_existing_data(self):
        """Clear all existing data"""
        Order.objects.all().delete()
        CustomService.objects.all().delete()
        Service.objects.all().delete()
        Sponsor.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

    def create_sample_users(self):
        """Create sample users with different roles"""
        # Create sample customers
        customers_data = [
            {'username': 'cliente1', 'email': 'cliente1@example.com', 'password': 'password123'},
            {'username': 'cliente2', 'email': 'cliente2@example.com', 'password': 'password123'},
            {'username': 'cliente3', 'email': 'cliente3@example.com', 'password': 'password123'},
        ]
        
        for customer_data in customers_data:
            user, created = User.objects.get_or_create(
                username=customer_data['username'],
                defaults={
                    'email': customer_data['email'],
                    'first_name': customer_data['username'].replace('cliente', 'Cliente '),
                    'last_name': 'Silva'
                }
            )
            if created:
                user.set_password(customer_data['password'])
                user.save()
                UserProfile.objects.create(
                    user=user,
                    user_type='customer',
                    phone=f'+55119{random.randint(10000000, 99999999)}',
                    city='São Paulo',
                    state='SP'
                )
                self.stdout.write(f'Created customer: {user.username}')
        
        # Create sample professionals
        professionals_data = [
            {'username': 'profissional1', 'email': 'prof1@example.com', 'password': 'password123'},
            {'username': 'profissional2', 'email': 'prof2@example.com', 'password': 'password123'},
            {'username': 'profissional3', 'email': 'prof3@example.com', 'password': 'password123'},
        ]
        
        for prof_data in professionals_data:
            user, created = User.objects.get_or_create(
                username=prof_data['username'],
                defaults={
                    'email': prof_data['email'],
                    'first_name': prof_data['username'].replace('profissional', 'Profissional '),
                    'last_name': 'Santos'
                }
            )
            if created:
                user.set_password(prof_data['password'])
                user.save()
                UserProfile.objects.create(
                    user=user,
                    user_type='professional',
                    phone=f'+55119{random.randint(10000000, 99999999)}',
                    city='São Paulo',
                    state='SP',
                    rating=random.uniform(3.5, 5.0),
                    review_count=random.randint(10, 100)
                )
                self.stdout.write(f'Created professional: {user.username}')
        
        # Create sample admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            UserProfile.objects.create(
                user=admin_user,
                user_type='admin'
            )
            self.stdout.write('Created admin user')

    def create_sample_services(self):
        """Create sample standard services"""
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

    def create_sample_sponsors(self):
        """Create sample sponsors"""
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

    def create_sample_custom_services(self):
        """Create sample custom services offered by professionals"""
        professionals = list(User.objects.filter(userprofile__user_type='professional'))
        if not professionals:
            self.stdout.write('No professionals found, skipping custom services creation')
            return
            
        service_types = [
            ('Elétrica Residencial', 'Instalação e manutenção de sistemas elétricos residenciais', 'electrical'),
            ('Encanamento Predial', 'Reparos e instalações hidráulicas em prédios', 'plumbing'),
            ('Pintura Comercial', 'Pintura de escritórios e espaços comerciais', 'painting'),
            ('Montagem de Estandes', 'Montagem de estandes para eventos e feiras', 'assembly'),
            ('Limpeza Industrial', 'Limpeza especializada para indústrias', 'cleaning'),
            ('Reparo de Máquinas', 'Manutenção e reparo de equipamentos industriais', 'repair'),
        ]
        
        for i, professional in enumerate(professionals):
            # Each professional offers 2-3 custom services
            num_services = random.randint(2, 3)
            for j in range(num_services):
                if i * num_services + j < len(service_types):
                    service_type = service_types[i * num_services + j]
                    custom_service = CustomService.objects.create(
                        name=service_type[0],
                        description=service_type[1],
                        category=service_type[2],
                        estimated_price=random.uniform(200.00, 800.00),
                        estimated_duration=timedelta(hours=random.randint(2, 8)),
                        provider=professional
                    )
                    self.stdout.write(f'Created custom service: {custom_service.name} by {professional.username}')

    def create_sample_orders(self):
        """Create sample orders"""
        customers = list(User.objects.filter(userprofile__user_type='customer'))
        professionals = list(User.objects.filter(userprofile__user_type='professional'))
        services = list(Service.objects.all())
        custom_services = list(CustomService.objects.all())
        
        if not customers or not professionals or not services:
            self.stdout.write('Missing required data for orders, skipping order creation')
            return
            
        # Create 15 sample orders
        for i in range(15):
            customer = random.choice(customers)
            professional = random.choice(professionals)
            
            # Randomly choose between standard service and custom service
            if random.choice([True, False]) and custom_services:
                service = None
                custom_service = random.choice(custom_services)
                total_price = custom_service.estimated_price
            else:
                service = random.choice(services)
                custom_service = None
                total_price = service.base_price
            
            # Generate random scheduled date (within next 30 days or past 30 days)
            if random.choice([True, False]):
                # Future date
                scheduled_date = datetime.now() + timedelta(days=random.randint(1, 30))
            else:
                # Past date
                scheduled_date = datetime.now() - timedelta(days=random.randint(1, 30))
            
            # Random status
            status_choices = ['pending', 'confirmed', 'in_progress', 'completed', 'cancelled']
            status = random.choice(status_choices)
            
            # Create order
            order = Order.objects.create(
                customer=customer,
                service=service,
                professional=professional,
                status=status,
                scheduled_date=scheduled_date,
                address=f'Rua Teste {random.randint(1, 1000)}, São Paulo, SP',
                notes=f'Pedido de teste #{i+1}',
                total_price=total_price
            )
            
            self.stdout.write(f'Created order #{order.id} for {customer.username}')