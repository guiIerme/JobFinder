"""
Test script for Batch Processing API

This script tests the batch processing API endpoints to ensure they work correctly.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

from django.contrib.auth.models import User
from services.models import BatchOperation, Order, UserProfile, CustomService
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
import json


def test_batch_processing_api():
    """Test the batch processing API"""
    print("=" * 80)
    print("Testing Batch Processing API")
    print("=" * 80)
    
    # Create test user
    print("\n1. Creating test user...")
    user, created = User.objects.get_or_create(
        username='batch_test_user',
        defaults={
            'email': 'batch@test.com',
            'is_staff': True
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"   ✓ Created user: {user.username}")
    else:
        print(f"   ✓ Using existing user: {user.username}")
    
    # Create user profile
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={'user_type': 'admin'}
    )
    
    # Create API client
    client = APIClient()
    client.force_authenticate(user=user)
    
    # Test 1: Batch size validation
    print("\n2. Testing batch size validation...")
    operations = [{'method': 'PATCH', 'resource_id': i, 'data': {}} for i in range(51)]
    response = client.post('/api/v1/batch/', {
        'operation_type': 'order_update',
        'operations': operations
    }, format='json')
    
    if response.status_code == 400:
        error = response.json().get('error', {})
        if error.get('code') == 'BATCH_SIZE_EXCEEDED':
            print(f"   ✓ Batch size validation working (max 50 operations)")
        else:
            print(f"   ✗ Unexpected error: {error}")
    else:
        print(f"   ✗ Expected 400, got {response.status_code}")
    
    # Test 2: Missing operation type
    print("\n3. Testing missing operation_type validation...")
    response = client.post('/api/v1/batch/', {
        'operations': [{'method': 'PATCH', 'resource_id': 1, 'data': {}}]
    }, format='json')
    
    if response.status_code == 400:
        error = response.json().get('error', {})
        if error.get('code') == 'MISSING_OPERATION_TYPE':
            print(f"   ✓ Missing operation_type validation working")
        else:
            print(f"   ✗ Unexpected error: {error}")
    else:
        print(f"   ✗ Expected 400, got {response.status_code}")
    
    # Test 3: Empty operations list
    print("\n4. Testing empty operations validation...")
    response = client.post('/api/v1/batch/', {
        'operation_type': 'order_update',
        'operations': []
    }, format='json')
    
    if response.status_code == 400:
        error = response.json().get('error', {})
        if error.get('code') == 'INVALID_OPERATIONS':
            print(f"   ✓ Empty operations validation working")
        else:
            print(f"   ✗ Unexpected error: {error}")
    else:
        print(f"   ✗ Expected 400, got {response.status_code}")
    
    # Test 4: Create test orders and perform batch update
    print("\n5. Creating test orders...")
    from services.models import Service
    from datetime import datetime, timedelta
    
    # Get or create a service
    service, _ = Service.objects.get_or_create(
        name='Test Service',
        defaults={
            'description': 'Test service for batch operations',
            'category': 'cleaning',
            'base_price': 100.00
        }
    )
    
    # Create test orders
    orders = []
    for i in range(3):
        order, created = Order.objects.get_or_create(
            customer=user,
            service=service,
            defaults={
                'status': 'pending',
                'scheduled_date': datetime.now() + timedelta(days=i+1),
                'address': f'Test Address {i+1}',
                'total_price': 100.00
            }
        )
        orders.append(order)
        if created:
            print(f"   ✓ Created order {order.id}")
        else:
            print(f"   ✓ Using existing order {order.id}")
    
    # Test 5: Batch update orders
    print("\n6. Testing batch order updates...")
    batch_operations = [
        {
            'method': 'PATCH',
            'resource_id': orders[0].id,
            'data': {'status': 'confirmed', 'notes': 'Batch updated'}
        },
        {
            'method': 'PATCH',
            'resource_id': orders[1].id,
            'data': {'status': 'in_progress'}
        },
        {
            'method': 'PATCH',
            'resource_id': 99999,  # Non-existent order
            'data': {'status': 'completed'}
        }
    ]
    
    response = client.post('/api/v1/batch/', {
        'operation_type': 'order_update',
        'operations': batch_operations
    }, format='json')
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ Batch operation created: ID {result['batch_id']}")
        print(f"   ✓ Total operations: {result['total_operations']}")
        print(f"   ✓ Completed: {result['summary']['completed']}")
        print(f"   ✓ Failed: {result['summary']['failed']}")
        print(f"   ✓ Success rate: {result['summary']['success_rate']}%")
        
        # Check individual results
        for res in result['results']:
            status_icon = "✓" if res['success'] else "✗"
            print(f"   {status_icon} Operation {res['index']}: {'Success' if res['success'] else 'Failed'}")
            if not res['success']:
                print(f"      Error: {res.get('error', {}).get('message', 'Unknown error')}")
    else:
        print(f"   ✗ Batch operation failed: {response.status_code}")
        print(f"      Response: {response.json()}")
    
    # Test 6: Check batch status
    if response.status_code == 200:
        batch_id = response.json()['batch_id']
        print(f"\n7. Testing batch status endpoint...")
        response = client.get(f'/api/v1/batch/{batch_id}/')
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Batch status retrieved successfully")
            print(f"   ✓ Status: {result['status']}")
            print(f"   ✓ Progress: {result['progress']}%")
        else:
            print(f"   ✗ Failed to get batch status: {response.status_code}")
    
    # Test 7: Check batch history
    print(f"\n8. Testing batch history endpoint...")
    response = client.get('/api/v1/batch/history/')
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ Batch history retrieved successfully")
        print(f"   ✓ Total batches: {result['count']}")
        print(f"   ✓ Results returned: {len(result['results'])}")
    else:
        print(f"   ✗ Failed to get batch history: {response.status_code}")
    
    # Test 8: Check BatchOperation model methods
    print(f"\n9. Testing BatchOperation model methods...")
    batch = BatchOperation.objects.filter(user=user).first()
    if batch:
        print(f"   ✓ Progress percentage: {batch.progress_percentage}%")
        print(f"   ✓ Success rate: {batch.success_rate}%")
        print(f"   ✓ Is complete: {batch.is_complete}")
        print(f"   ✓ Duration: {batch.duration_seconds} seconds")
        
        # Test user stats
        stats = BatchOperation.get_user_stats(user, days=30)
        print(f"   ✓ User stats - Total batches: {stats['total_batches']}")
        print(f"   ✓ User stats - Success rate: {stats['success_rate']}%")
    else:
        print(f"   ✗ No batch operations found")
    
    print("\n" + "=" * 80)
    print("Batch Processing API Tests Complete!")
    print("=" * 80)


if __name__ == '__main__':
    test_batch_processing_api()
