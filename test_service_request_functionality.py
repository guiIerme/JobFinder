import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

from django.contrib.auth.models import User
from services.models import Service, CustomService, Order, UserProfile

# Create a test user if one doesn't exist
try:
    user = User.objects.get(username='testuser')
except User.DoesNotExist:
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    UserProfile.objects.create(user=user, user_type='customer')

# Create a test custom service if one doesn't exist
try:
    custom_service = CustomService.objects.get(name='Test Custom Service')
except CustomService.DoesNotExist:
    # Create a provider user first
    try:
        provider = User.objects.get(username='testprovider')
    except User.DoesNotExist:
        provider = User.objects.create_user(
            username='testprovider',
            email='provider@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=provider, user_type='professional')
    
    custom_service = CustomService.objects.create(
        name='Test Custom Service',
        description='This is a test custom service for verification',
        category='repair',
        estimated_price=150.00,
        provider=provider
    )

print(f"Test user: {user.username}")
print(f"Test custom service: {custom_service.name}")
print(f"Service price: R$ {custom_service.estimated_price}")
print("Service request functionality is ready for testing!")