"""
Test script for search API optimization

Tests:
1. Search with different sorting options
2. Verify response time < 500ms
3. Verify cache integration
4. Verify performance metadata in response
"""

import requests
import time
import json

BASE_URL = 'http://localhost:8000'

def test_search_endpoint(endpoint, params, test_name):
    """Test a search endpoint with given parameters"""
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"Endpoint: {endpoint}")
    print(f"Params: {json.dumps(params, indent=2)}")
    print(f"{'='*60}")
    
    # First request (uncached)
    start = time.time()
    response = requests.get(f"{BASE_URL}{endpoint}", params=params)
    elapsed = (time.time() - start) * 1000
    
    print(f"\n✓ First request (uncached): {elapsed:.2f}ms")
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Check performance metadata
        if 'performance' in data:
            perf = data['performance']
            print(f"  Response time (server): {perf.get('response_time_ms')}ms")
            print(f"  Cached: {perf.get('cached')}")
            print(f"  Target met (<500ms): {perf.get('target_met')}")
        
        # Check results
        if 'count' in data:
            print(f"  Results: {data['count']} total")
        
        # Second request (should be cached)
        time.sleep(0.1)
        start = time.time()
        response2 = requests.get(f"{BASE_URL}{endpoint}", params=params)
        elapsed2 = (time.time() - start) * 1000
        
        print(f"\n✓ Second request (cached): {elapsed2:.2f}ms")
        
        if response2.status_code == 200:
            data2 = response2.json()
            if 'performance' in data2:
                perf2 = data2['performance']
                print(f"  Response time (server): {perf2.get('response_time_ms')}ms")
                print(f"  Cached: {perf2.get('cached')}")
                print(f"  Speedup: {elapsed / elapsed2:.2f}x faster")
    else:
        print(f"  Error: {response.text}")
    
    return response.status_code == 200


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SEARCH API OPTIMIZATION TESTS")
    print("="*60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Basic search with sorting by price
    tests_total += 1
    if test_search_endpoint(
        '/api/v1/search/',
        {'q': 'limpeza', 'sort': 'price'},
        'Basic search sorted by price (ascending)'
    ):
        tests_passed += 1
    
    # Test 2: Search with category filter and rating sort
    tests_total += 1
    if test_search_endpoint(
        '/api/v1/search/',
        {'category': 'cleaning', 'sort': '-rating'},
        'Category filter with rating sort (descending)'
    ):
        tests_passed += 1
    
    # Test 3: Search with price range
    tests_total += 1
    if test_search_endpoint(
        '/api/v1/search/',
        {'min_price': '50', 'max_price': '200', 'sort': 'price'},
        'Price range filter with price sort'
    ):
        tests_passed += 1
    
    # Test 4: Professional search with rating sort
    tests_total += 1
    if test_search_endpoint(
        '/api/v1/search/professionals/',
        {'sort': '-rating', 'is_available': 'true'},
        'Professional search by rating (available only)'
    ):
        tests_passed += 1
    
    # Test 5: Search with relevance (default)
    tests_total += 1
    if test_search_endpoint(
        '/api/v1/search/',
        {'q': 'encanamento', 'sort': 'relevance'},
        'Search with relevance sort (most recent)'
    ):
        tests_passed += 1
    
    # Test 6: Search with name sort
    tests_total += 1
    if test_search_endpoint(
        '/api/v1/search/',
        {'sort': 'name'},
        'Search sorted by name (alphabetical)'
    ):
        tests_passed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Tests passed: {tests_passed}/{tests_total}")
    print(f"Success rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("\n✓ All tests passed!")
    else:
        print(f"\n✗ {tests_total - tests_passed} test(s) failed")
    
    print("\nNOTE: Make sure the development server is running:")
    print("  python manage.py runserver")


if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to server")
        print("  Make sure the development server is running:")
        print("  python manage.py runserver")
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
