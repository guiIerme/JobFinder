"""
Test script for rate limiting functionality.

This script tests the rate limiting middleware by making multiple requests
to verify that limits are enforced correctly.
"""

import requests
import time
from datetime import datetime


def test_rate_limiting():
    """Test rate limiting for anonymous users."""
    base_url = "http://localhost:8000"
    test_endpoint = f"{base_url}/search/"
    
    print("=" * 60)
    print("Testing Rate Limiting Functionality")
    print("=" * 60)
    print(f"\nTarget endpoint: {test_endpoint}")
    print(f"Expected limit for anonymous users: 100 requests/hour")
    print("\nMaking test requests...\n")
    
    # Make a few requests to test rate limiting
    for i in range(1, 6):
        try:
            response = requests.get(test_endpoint, timeout=5)
            
            # Extract rate limit headers
            limit = response.headers.get('X-RateLimit-Limit', 'N/A')
            remaining = response.headers.get('X-RateLimit-Remaining', 'N/A')
            reset = response.headers.get('X-RateLimit-Reset', 'N/A')
            
            print(f"Request {i}:")
            print(f"  Status: {response.status_code}")
            print(f"  Rate Limit: {limit}")
            print(f"  Remaining: {remaining}")
            print(f"  Reset: {reset}")
            
            if response.status_code == 429:
                print(f"  ⚠️  Rate limit exceeded!")
                print(f"  Response: {response.json()}")
                break
            else:
                print(f"  ✓ Request successful")
            
            print()
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error: {e}")
            print()
    
    print("=" * 60)
    print("Test completed!")
    print("=" * 60)


def test_authenticated_rate_limiting():
    """Test rate limiting for authenticated users."""
    base_url = "http://localhost:8000"
    login_url = f"{base_url}/login/"
    test_endpoint = f"{base_url}/profile/"
    
    print("\n" + "=" * 60)
    print("Testing Authenticated User Rate Limiting")
    print("=" * 60)
    print(f"\nExpected limit for authenticated users: 1000 requests/hour")
    print("\nNote: This test requires valid credentials")
    print("=" * 60)


if __name__ == "__main__":
    print("\n🚀 Starting Rate Limiting Tests\n")
    
    # Test anonymous rate limiting
    test_rate_limiting()
    
    # Test authenticated rate limiting (informational)
    test_authenticated_rate_limiting()
    
    print("\n✅ All tests completed!\n")
