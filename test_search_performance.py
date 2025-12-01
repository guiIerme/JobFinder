"""
Performance test for Advanced Search API
Validates that response times are under 500ms
"""
import os
import django
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

from django.test import RequestFactory
from services.api.search_views import AdvancedSearchView, ProfessionalSearchView

def measure_response_time(view, request):
    """Measure response time for a request"""
    start_time = time.time()
    response = view(request)
    end_time = time.time()
    return (end_time - start_time) * 1000  # Convert to milliseconds

def test_performance():
    """Test response times for various search scenarios"""
    print("=" * 60)
    print("Search API Performance Test")
    print("Target: < 500ms for 95% of requests")
    print("=" * 60)
    
    factory = RequestFactory()
    search_view = AdvancedSearchView.as_view()
    professional_view = ProfessionalSearchView.as_view()
    
    test_cases = [
        ("Basic search", factory.get('/api/v1/search/'), search_view),
        ("Text search", factory.get('/api/v1/search/?q=encanamento'), search_view),
        ("Category filter", factory.get('/api/v1/search/?category=plumbing'), search_view),
        ("Price range", factory.get('/api/v1/search/?min_price=50&max_price=200'), search_view),
        ("Rating filter", factory.get('/api/v1/search/?min_rating=4.0'), search_view),
        ("Price sorting", factory.get('/api/v1/search/?sort=price'), search_view),
        ("Rating sorting", factory.get('/api/v1/search/?sort=-rating'), search_view),
        ("Combined filters", factory.get('/api/v1/search/?q=limpeza&category=cleaning&min_price=30&max_price=150&sort=price'), search_view),
        ("Geographic search", factory.get('/api/v1/search/?lat=-23.5505&lng=-46.6333&radius=10'), search_view),
        ("Distance sorting", factory.get('/api/v1/search/?lat=-23.5505&lng=-46.6333&radius=50&sort=distance'), search_view),
        ("Professional search", factory.get('/api/v1/search/professionals/'), professional_view),
        ("Professional with filters", factory.get('/api/v1/search/professionals/?min_rating=4.0&is_available=true'), professional_view),
        ("Professional geographic", factory.get('/api/v1/search/professionals/?lat=-23.5505&lng=-46.6333&radius=20'), professional_view),
    ]
    
    results = []
    
    print("\nRunning performance tests...\n")
    
    for test_name, request, view in test_cases:
        # Run test 5 times to get average
        times = []
        for _ in range(5):
            response_time = measure_response_time(view, request)
            times.append(response_time)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        status = "✓ PASS" if avg_time < 500 else "✗ FAIL"
        
        print(f"{status} | {test_name:30s} | Avg: {avg_time:6.2f}ms | Min: {min_time:6.2f}ms | Max: {max_time:6.2f}ms")
        
        results.append({
            'name': test_name,
            'avg': avg_time,
            'min': min_time,
            'max': max_time,
            'passed': avg_time < 500
        })
    
    # Calculate statistics
    all_times = [r['avg'] for r in results]
    avg_overall = sum(all_times) / len(all_times)
    passed_count = sum(1 for r in results if r['passed'])
    pass_rate = (passed_count / len(results)) * 100
    
    print("\n" + "=" * 60)
    print("Performance Summary")
    print("=" * 60)
    print(f"Total tests: {len(results)}")
    print(f"Passed: {passed_count} ({pass_rate:.1f}%)")
    print(f"Failed: {len(results) - passed_count}")
    print(f"Average response time: {avg_overall:.2f}ms")
    print(f"Fastest: {min(all_times):.2f}ms")
    print(f"Slowest: {max(all_times):.2f}ms")
    
    if pass_rate >= 95:
        print(f"\n✓ SUCCESS: {pass_rate:.1f}% of requests under 500ms (target: 95%)")
    else:
        print(f"\n✗ WARNING: Only {pass_rate:.1f}% of requests under 500ms (target: 95%)")
    
    print("=" * 60)
    
    return pass_rate >= 95

if __name__ == '__main__':
    success = test_performance()
    exit(0 if success else 1)
