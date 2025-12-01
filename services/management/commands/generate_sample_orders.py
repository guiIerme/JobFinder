import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from services.models import Service, CustomService, Order, UserProfile
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Generate sample orders and reviews for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            type=int,
            default=10,
            help='Number of sample orders to generate (default: 10)',
        )

    def handle(self, *args, **options):
        # Get existing users, services, and professionals
        users = list(User.objects.filter(userprofile__user_type='customer'))
        professionals = list(User.objects.filter(userprofile__user_type='professional'))
        services = list(Service.objects.all())
        custom_services = list(CustomService.objects.all())
        
        if not users or not professionals or not services:
            self.stdout.write(
                'Need at least one customer, professional, and service to generate orders'
            )
            return

        # Generate sample orders
        for i in range(options['number']):
            # Randomly select customer, professional, and service
            customer = random.choice(users)
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
            
            # Generate random scheduled date (within next 30 days)
            scheduled_date = datetime.now() + timedelta(days=random.randint(1, 30))
            
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

        self.stdout.write(
            f'Successfully generated {options["number"]} sample orders'
        )