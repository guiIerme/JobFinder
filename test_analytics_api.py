"""
Test script for Analytics API endpoints.

This script tests the analytics API endpoints to ensure they work correctly.
"""

import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

from django.contrib.auth.models import User
from services.models import APIMetric
from django.utils import timezone
from datetime import timedelta
import random


def create_test_data():
    """Create test API metrics data"""
    print("Creating test API metrics data...")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing test user: {user.username}")
    
    # Create sample metrics for the last 24 hours
    endpoints = [
        '/api/v1/services/',
        '/api/v1/professionals/',
        '/api/v1/search/',
        '/api/v1/orders/',
        '/api/v1/health/',
    ]
    
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    status_codes = [200, 201, 400, 404, 500]
    
    # Create 100 sample metrics
    metrics_created = 0
    for i in range(100):
        # Random timestamp within last 24 hours
        hours_ago = random.randint(0, 24)
        timestamp = timezone.now() - timedelta(hours=hours_ago)
        
        # Random endpoint and method
        endpoint = random.choice(endpoints)
        method = random.choice(methods)
        
        # Response time: mostly fast, some slow
        if random.random() < 0.9:  # 90% fast
            response_time = random.uniform(50, 500)
        else:  # 10% slow
            response_time = random.uniform(1000, 3000)
        
        # Status code: mostly success, some errors
        if random.random() < 0.85:  # 85% success
            status_code = random.choice([200, 201])
        else:  # 15% errors
            status_code = random.choice([400, 404, 500])
        
        # Create metric
        APIMetric.objects.create(
            endpoint=endpoint,
            method=method,
            response_time=round(response_time, 2),
            status_code=status_code,
            user=user if random.random() < 0.7 else None,  # 70% authenticated
            ip_address=f"192.168.1.{random.randint(1, 255)}",
            user_agent="Test User Agent"
        )
        metrics_created += 1
    
    print(f"Created {metrics_created} test API metrics")
    return metrics_created


def test_performance_stats():
    """Test performance statistics"""
    print("\n=== Testing Performance Statistics ===")
    
    stats = APIMetric.get_performance_stats(hours=24)
    
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Average Response Time: {stats['avg_response_time']}ms")
    print(f"P95 Response Time: {stats['p95_response_time']}ms")
    print(f"P99 Response Time: {stats['p99_response_time']}ms")
    print(f"Error Rate: {stats['error_rate']}%")
    print(f"Requests Per Minute: {stats['requests_per_minute']}")
    
    return stats['total_requests'] > 0


def test_slowest_endpoints():
    """Test slowest endpoints query"""
    print("\n=== Testing Slowest Endpoints ===")
    
    slowest = APIMetric.get_slowest_endpoints(limit=5, hours=24)
    
    for i, endpoint in enumerate(slowest, 1):
        print(f"{i}. {endpoint['method']} {endpoint['endpoint']}")
        print(f"   Avg: {endpoint['avg_response_time']:.2f}ms, Max: {endpoint['max_response_time']:.2f}ms")
        print(f"   Requests: {endpoint['request_count']}")
    
    return len(slowest) > 0


def test_error_stats():
    """Test error statistics"""
    print("\n=== Testing Error Statistics ===")
    
    errors = APIMetric.get_error_stats(hours=24)
    
    if errors:
        for i, error in enumerate(errors[:5], 1):
            print(f"{i}. {error['endpoint']} - Status {error['status_code']}")
            print(f"   Error Count: {error['error_count']}")
    else:
        print("No errors found (this is good!)")
    
    return True


def test_endpoint_stats():
    """Test endpoint statistics"""
    print("\n=== Testing Endpoint Statistics ===")
    
    stats = APIMetric.get_endpoint_stats(hours=24)
    
    for i, stat in enumerate(stats[:5], 1):
        print(f"{i}. {stat['method']} {stat['endpoint']}")
        print(f"   Total: {stat['total_requests']}, Errors: {stat['error_count']}")
        print(f"   Avg Time: {stat['avg_response_time']:.2f}ms")
        print(f"   Min: {stat['min_response_time']:.2f}ms, Max: {stat['max_response_time']:.2f}ms")
    
    return len(stats) > 0


def main():
    """Main test function"""
    print("=" * 60)
    print("Analytics API Test Suite")
    print("=" * 60)
    
    # Check if we have existing data
    existing_count = APIMetric.objects.count()
    print(f"\nExisting API metrics: {existing_count}")
    
    if existing_count < 10:
        print("\nNot enough test data. Creating sample data...")
        create_test_data()
    else:
        print("\nUsing existing data for tests...")
    
    # Run tests
    tests = [
        ("Performance Statistics", test_performance_stats),
        ("Slowest Endpoints", test_slowest_endpoints),
        ("Error Statistics", test_error_stats),
        ("Endpoint Statistics", test_endpoint_stats),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASS" if result else "FAIL"))
        except Exception as e:
            print(f"\nError in {test_name}: {e}")
            results.append((test_name, "ERROR"))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, result in results:
        status_symbol = "✓" if result == "PASS" else "✗"
        print(f"{status_symbol} {test_name}: {result}")
    
    # Overall result
    all_passed = all(result == "PASS" for _, result in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed. Please review the output above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
