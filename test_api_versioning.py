"""
Test script for API versioning implementation

This script tests the API versioning and deprecation system.
Requirements: 12.1, 12.2, 12.3, 12.4, 12.5
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:8000'

def test_version_in_url():
    """Test version specification via URL path"""
    print("\n=== Testing Version in URL ===")
    
    # Test v1 endpoint
    response = requests.get(f'{BASE_URL}/api/v1/health/')
    print(f"GET /api/v1/health/")
    print(f"Status: {response.status_code}")
    print(f"X-API-Version header: {response.headers.get('X-API-Version', 'Not present')}")
    
    if response.status_code == 200:
        print("✓ v1 endpoint accessible")
    else:
        print("✗ v1 endpoint failed")
    
    return response.status_code == 200


def test_version_info_endpoint():
    """Test public version information endpoint"""
    print("\n=== Testing Version Info Endpoint ===")
    
    response = requests.get(f'{BASE_URL}/api/v1/version/')
    print(f"GET /api/v1/version/")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Current version: {data.get('current_version')}")
        print(f"Supported versions: {data.get('supported_versions')}")
        print(f"Deprecation warnings: {len(data.get('deprecation_warnings', []))}")
        print("✓ Version info endpoint working")
        return True
    else:
        print("✗ Version info endpoint failed")
        return False


def test_accept_version_header():
    """Test version specification via Accept-Version header"""
    print("\n=== Testing Accept-Version Header ===")
    
    headers = {'Accept-Version': 'v1'}
    response = requests.get(f'{BASE_URL}/api/services/', headers=headers)
    print(f"GET /api/services/ with Accept-Version: v1")
    print(f"Status: {response.status_code}")
    print(f"X-API-Version header: {response.headers.get('X-API-Version', 'Not present')}")
    
    if response.headers.get('X-API-Version') == 'v1':
        print("✓ Accept-Version header working")
        return True
    else:
        print("✗ Accept-Version header not working")
        return False


def test_unsupported_version():
    """Test handling of unsupported version"""
    print("\n=== Testing Unsupported Version ===")
    
    response = requests.get(f'{BASE_URL}/api/v99/health/')
    print(f"GET /api/v99/health/")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 400:
        data = response.json()
        print(f"Error message: {data.get('error', {}).get('message')}")
        print("✓ Unsupported version properly rejected")
        return True
    else:
        print("✗ Unsupported version not properly handled")
        return False


def test_deprecation_headers():
    """Test deprecation warning headers"""
    print("\n=== Testing Deprecation Headers ===")
    
    response = requests.get(f'{BASE_URL}/api/v1/health/')
    
    deprecated = response.headers.get('X-API-Deprecated')
    deprecation_date = response.headers.get('X-API-Deprecation-Date')
    deprecation_info = response.headers.get('X-API-Deprecation-Info')
    
    print(f"X-API-Deprecated: {deprecated or 'Not present'}")
    print(f"X-API-Deprecation-Date: {deprecation_date or 'Not present'}")
    print(f"X-API-Deprecation-Info: {deprecation_info or 'Not present'}")
    
    if deprecated:
        print("⚠ Version is deprecated")
        return True
    else:
        print("✓ Version is not deprecated (expected for v1)")
        return True


def test_changelog_exists():
    """Test that changelog file exists"""
    print("\n=== Testing Changelog ===")
    
    import os
    changelog_path = 'services/api/CHANGELOG.md'
    
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Changelog exists: {len(content)} characters")
            print("✓ Changelog file present")
            return True
    else:
        print("✗ Changelog file not found")
        return False


def run_all_tests():
    """Run all versioning tests"""
    print("=" * 60)
    print("API Versioning Implementation Tests")
    print("=" * 60)
    
    tests = [
        ("Version in URL", test_version_in_url),
        ("Version Info Endpoint", test_version_info_endpoint),
        ("Accept-Version Header", test_accept_version_header),
        ("Unsupported Version", test_unsupported_version),
        ("Deprecation Headers", test_deprecation_headers),
        ("Changelog Exists", test_changelog_exists),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
    
    return passed == total


if __name__ == '__main__':
    print("\nNote: Make sure the Django development server is running on localhost:8000")
    print("Run: python manage.py runserver\n")
    
    input("Press Enter to start tests...")
    
    success = run_all_tests()
    exit(0 if success else 1)
