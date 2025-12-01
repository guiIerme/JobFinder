"""
API Integration Tests

This module contains integration tests for the API optimization features:
- Search API with cache and pagination (Requirements: 1.1-1.5, 2.1-2.5, 3.1-3.5)
- Rate limiting under load (Requirements: 4.1-4.5)
- Batch operations with transactions (Requirements: 7.1-7.5)
- WebSocket with multiple connections (Requirements: 8.1-8.5)

These tests verify that all components work together correctly.
"""

from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth.models import User
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from services.models import (
    UserProfile, CustomService, ServiceRequestModal,
    RateLimitRecord, BatchOperation
)
from services.cache_manager import CacheManager
import json
import time
from datetime import datetime, timedelta


class SearchCachePaginationIntegrationTest(TestCase):
    """
    Test complete search flow with cache and pagination integration
    Requirements: 1.1-1.5, 2.1-2.5, 3.1-3.5
    """
    
    def setUp(self):
        """Set up test data"""
        cache.clear()
        self.client = APIClient()
        
        # Create test users and professionals
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create professionals with services
        for i in range(25):
            user = User.objects.create_user(
                username=f'professional{i}',
                email=f'pro{i}@example.com',
                password='testpass123'
            )
            profile = UserProfile.objects.create(
                user=user,
                user_type='professional',
                phone=f'1199999{i:04d}',
                bio=f'Professional {i} bio',
                latitude=-23.5505 + (i * 0.01),
                longitude=-46.6333 + (i * 0.01)
            )
            
            # Create custom services
            CustomService.objects.create(
                professional=profile,
                name=f'Service {i}',
                description=f'Description for service {i}',
                price=50.00 + (i * 10),
                category='cleaning' if i % 2 == 0 else 'plumbing'
            )
    
    def test_search_with_pagination_and_cache(self):
        """Test search returns paginated results and uses cache"""
        # First request - should hit database
        response1 = self.client.get('/api/v1/search/', {
            'q': 'service',
            'page': 1,
            'page_size': 10
        })
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        data1 = response1.json()
        
        # Verify pagination metadata
        self.assertIn('count', data1)
        self.assertIn('next', data1)
        self.assertIn('previous', data1)
        self.assertIn('results', data1)
        self.assertEqual(len(data1['results']), 10)
        
        # Second identical request - should hit cache
        start_time = time.time()
        response2 = self.client.get('/api/v1/search/', {
            'q': 'service',
            'page': 1,
            'page_size': 10
        })
        cache_time = time.time() - start_time
        
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        data2 = response2.json()
        
        # Results should be identical
        self.assertEqual(data1, data2)
        
        # Cache should be faster (< 50ms)
        self.assertLess(cache_time, 0.05)
    
    def test_search_with_filters_and_sorting(self):
        """Test search with multiple filters and sorting"""
        response = self.client.get('/api/v1/search/', {
            'q': 'service',
            'category': 'cleaning',
            'min_price': 50,
            'max_price': 150,
            'sort': 'price'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify results are filtered and sorted
        results = data['results']
        for result in results:
            self.assertEqual(result['category'], 'cleaning')
            self.assertGreaterEqual(result['price'], 50)
            self.assertLessEqual(result['price'], 150)
        
        # Verify sorting
        prices = [r['price'] for r in results]
        self.assertEqual(prices, sorted(prices))
    
    def test_cache_invalidation_on_update(self):
        """Test cache is invalidated when data is updated"""
        # First request to populate cache
        response1 = self.client.get('/api/v1/search/', {'q': 'service'})
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Update a service
        service = CustomService.objects.first()
        service.name = 'Updated Service Name'
        service.save()
        
        # Second request should get fresh data
        response2 = self.client.get('/api/v1/search/', {'q': 'Updated'})
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        data = response2.json()
        
        # Should find the updated service
        self.assertGreater(data['count'], 0)


class RateLimitingIntegrationTest(TestCase):
    """
    Test rate limiting under load
    Requirements: 4.1-4.5
    """
    
    def setUp(self):
        """Set up test client"""
        self.client = APIClient()
        cache.clear()
        RateLimitRecord.objects.all().delete()
    
    def test_anonymous_rate_limit(self):
        """Test anonymous users are rate limited to 100/hour"""
        # Make requests up to the limit
        for i in range(100):
            response = self.client.get('/api/v1/search/')
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
        
        # Next request should be rate limited
        response = self.client.get('/api/v1/search/')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Verify rate limit headers
        self.assertIn('X-RateLimit-Limit', response)
        self.assertIn('X-RateLimit-Remaining', response)
        self.assertIn('X-RateLimit-Reset', response)
    
    def test_authenticated_rate_limit(self):
        """Test authenticated users have higher rate limit"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        # Authenticated users should have 1000/hour limit
        # Test a sample of requests
        for i in range(50):
            response = self.client.get('/api/v1/search/')
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
    
    def test_rate_limit_headers(self):
        """Test rate limit headers are present"""
        response = self.client.get('/api/v1/search/')
        
        # Verify headers exist
        self.assertIn('X-RateLimit-Limit', response)
        self.assertIn('X-RateLimit-Remaining', response)
        self.assertIn('X-RateLimit-Reset', response)
        
        # Verify header values
        limit = int(response['X-RateLimit-Limit'])
        remaining = int(response['X-RateLimit-Remaining'])
        
        self.assertGreater(limit, 0)
        self.assertGreaterEqual(remaining, 0)
        self.assertLess(remaining, limit)


class BatchOperationsIntegrationTest(TransactionTestCase):
    """
    Test batch operations with transactions
    Requirements: 7.1-7.5
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create admin user
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.force_authenticate(user=self.admin)
        
        # Create test orders
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            user_type='client',
            phone='11999999999'
        )
        
        self.professional = User.objects.create_user(
            username='professional',
            password='testpass123'
        )
        self.pro_profile = UserProfile.objects.create(
            user=self.professional,
            user_type='professional',
            phone='11988888888'
        )
        
        # Create orders
        self.orders = []
        for i in range(10):
            order = ServiceRequestModal.objects.create(
                user=self.user,
                professional=self.pro_profile,
                service_type='cleaning',
                description=f'Test order {i}',
                status='pending'
            )
            self.orders.append(order)
    
    def test_batch_order_status_update(self):
        """Test batch update of order statuses"""
        order_ids = [order.id for order in self.orders[:5]]
        
        response = self.client.post('/api/v1/batch/', {
            'operations': [
                {
                    'method': 'PATCH',
                    'url': f'/api/v1/orders/{order_id}/',
                    'body': {'status': 'confirmed'}
                }
                for order_id in order_ids
            ]
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify all operations succeeded
        self.assertEqual(len(data['results']), 5)
        for result in data['results']:
            self.assertEqual(result['status'], 200)
        
        # Verify database was updated
        for order_id in order_ids:
            order = ServiceRequestModal.objects.get(id=order_id)
            self.assertEqual(order.status, 'confirmed')
    
    def test_batch_partial_failure(self):
        """Test batch continues processing even with failures"""
        operations = [
            {
                'method': 'PATCH',
                'url': f'/api/v1/orders/{self.orders[0].id}/',
                'body': {'status': 'confirmed'}
            },
            {
                'method': 'PATCH',
                'url': '/api/v1/orders/99999/',  # Non-existent order
                'body': {'status': 'confirmed'}
            },
            {
                'method': 'PATCH',
                'url': f'/api/v1/orders/{self.orders[2].id}/',
                'body': {'status': 'confirmed'}
            }
        ]
        
        response = self.client.post('/api/v1/batch/', {
            'operations': operations
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify results
        self.assertEqual(len(data['results']), 3)
        self.assertEqual(data['results'][0]['status'], 200)  # Success
        self.assertEqual(data['results'][1]['status'], 404)  # Failure
        self.assertEqual(data['results'][2]['status'], 200)  # Success
    
    def test_batch_size_limit(self):
        """Test batch operations are limited to 50"""
        operations = [
            {
                'method': 'GET',
                'url': f'/api/v1/orders/{i}/',
                'body': {}
            }
            for i in range(51)
        ]
        
        response = self.client.post('/api/v1/batch/', {
            'operations': operations
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('error', data)


class WebSocketIntegrationTest(TransactionTestCase):
    """
    Test WebSocket with multiple connections
    Requirements: 8.1-8.5
    
    Note: This is a basic test structure. Full WebSocket testing
    requires additional setup with channels testing utilities.
    """
    
    def setUp(self):
        """Set up test users"""
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )
    
    def test_websocket_connection_requires_auth(self):
        """Test WebSocket connections require authentication"""
        # This is a placeholder for WebSocket testing
        # Full implementation requires channels testing utilities
        pass
    
    def test_websocket_notification_delivery(self):
        """Test notifications are delivered via WebSocket"""
        # This is a placeholder for WebSocket testing
        # Full implementation requires channels testing utilities
        pass
    
    def test_websocket_multiple_connections(self):
        """Test system supports multiple simultaneous connections"""
        # This is a placeholder for WebSocket testing
        # Full implementation requires channels testing utilities
        pass


class EndToEndAPIFlowTest(TestCase):
    """
    End-to-end test of complete API flow
    Tests the integration of all components together
    """
    
    def setUp(self):
        """Set up complete test environment"""
        cache.clear()
        self.client = APIClient()
        
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create professional with service
        self.professional = User.objects.create_user(
            username='professional',
            password='testpass123'
        )
        self.pro_profile = UserProfile.objects.create(
            user=self.professional,
            user_type='professional',
            phone='11988888888',
            latitude=-23.5505,
            longitude=-46.6333
        )
        
        self.service = CustomService.objects.create(
            professional=self.pro_profile,
            name='Test Service',
            description='Test description',
            price=100.00,
            category='cleaning'
        )
    
    def test_complete_api_flow(self):
        """Test complete flow: search -> view -> request -> track"""
        # Step 1: Search for services
        search_response = self.client.get('/api/v1/search/', {
            'q': 'test',
            'category': 'cleaning'
        })
        self.assertEqual(search_response.status_code, status.HTTP_200_OK)
        search_data = search_response.json()
        self.assertGreater(search_data['count'], 0)
        
        # Step 2: Get service details
        service_id = search_data['results'][0]['id']
        detail_response = self.client.get(f'/api/v1/services/{service_id}/')
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        
        # Step 3: Create service request
        request_response = self.client.post('/api/v1/orders/', {
            'professional': self.pro_profile.id,
            'service_type': 'cleaning',
            'description': 'Test request',
            'status': 'pending'
        }, format='json')
        self.assertEqual(request_response.status_code, status.HTTP_201_CREATED)
        
        # Step 4: Track order
        order_id = request_response.json()['id']
        track_response = self.client.get(f'/api/v1/orders/{order_id}/')
        self.assertEqual(track_response.status_code, status.HTTP_200_OK)
        
        # Verify all steps completed successfully
        self.assertTrue(True)
