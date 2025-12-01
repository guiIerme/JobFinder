"""
Test script for mobile-optimized API endpoints.

This script tests the mobile API endpoints to ensure they work correctly
with field selection, compact mode, and device detection.
"""
import requests
import json

BASE_URL = 'http://localhost:8000/api/v1/mobile'

# Test headers for different devices
MOBILE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
}

TABLET_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
}

DESKTOP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def test_mobile_services():
    """Test mobile services endpoint"""
    print("\n=== Testing Mobile Services Endpoint ===")
    
    # Test 1: Basic request
    print("\n1. Basic request:")
    response = requests.get(f'{BASE_URL}/services/', headers=MOBILE_HEADERS)
    print(f"Status: {response.status_code}")
    print(f"Device Type Header: {response.headers.get('X-Device-Type')}")
    print(f"Lazy Load Header: {response.headers.get('X-Image-Lazy-Load')}")
    if response.status_code == 200:
        data = response.json()
        print(f"Results count: {data.get('count', 0)}")
        if data.get('results'):
            print(f"First result fields: {list(data['results'][0].keys())}")
    
    # Test 2: Compact mode
    print("\n2. Compact mode (?compact=true):")
    response = requests.get(f'{BASE_URL}/services/?compact=true', headers=MOBILE_HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('results'):
            print(f"Compact fields: {list(data['results'][0].keys())}")
    
    # Test 3: Field selection
    print("\n3. Field selection (?fields=id,name,estimated_price):")
    response = requests.get(
        f'{BASE_URL}/services/?fields=id,name,estimated_price',
        headers=MOBILE_HEADERS
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('results'):
            print(f"Selected fields: {list(data['results'][0].keys())}")


def test_mobile_professionals():
    """Test mobile professionals endpoint"""
    print("\n=== Testing Mobile Professionals Endpoint ===")
    
    # Test 1: Basic request
    print("\n1. Basic request:")
    response = requests.get(f'{BASE_URL}/professionals/', headers=TABLET_HEADERS)
    print(f"Status: {response.status_code}")
    print(f"Device Type Header: {response.headers.get('X-Device-Type')}")
    if response.status_code == 200:
        data = response.json()
        print(f"Results count: {data.get('count', 0)}")
        if data.get('results'):
            print(f"First result fields: {list(data['results'][0].keys())}")
    
    # Test 2: Compact mode
    print("\n2. Compact mode (?compact=true):")
    response = requests.get(f'{BASE_URL}/professionals/?compact=true', headers=TABLET_HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('results'):
            print(f"Compact fields: {list(data['results'][0].keys())}")


def test_device_detection():
    """Test device detection across different user agents"""
    print("\n=== Testing Device Detection ===")
    
    devices = [
        ('Mobile', MOBILE_HEADERS),
        ('Tablet', TABLET_HEADERS),
        ('Desktop', DESKTOP_HEADERS),
    ]
    
    for device_name, headers in devices:
        print(f"\n{device_name} device:")
        response = requests.get(f'{BASE_URL}/services/', headers=headers)
        print(f"  Status: {response.status_code}")
        print(f"  Detected as: {response.headers.get('X-Device-Type')}")
        print(f"  Lazy load: {response.headers.get('X-Image-Lazy-Load', 'not recommended')}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Mobile API Endpoint Tests")
    print("=" * 60)
    print("\nMake sure the Django development server is running on localhost:8000")
    print("Run: python manage.py runserver")
    
    try:
        # Test if server is running
        response = requests.get('http://localhost:8000/api/v1/health/', timeout=2)
        if response.status_code != 200:
            print("\n❌ Server is not responding correctly")
            return
    except requests.exceptions.RequestException:
        print("\n❌ Cannot connect to server. Make sure it's running on localhost:8000")
        return
    
    print("\n✓ Server is running\n")
    
    # Run tests
    test_mobile_services()
    test_mobile_professionals()
    test_device_detection()
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == '__main__':
    main()
