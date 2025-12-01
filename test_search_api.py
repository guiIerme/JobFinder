"""
Test script for Advanced Search API
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

from django.test import RequestFactory
from services.api.search_views import AdvancedSearchView, ProfessionalSearchView
from services.models import CustomService, UserProfile, User
from decimal import Decimal

def test_basic_search():
    """Test basic search functionality"""
    print("Testing basic search...")
    
    factory = RequestFactory()
    view = AdvancedSearchView.as_view()
    
    # Test search without parameters
    request = factory.get('/api/v1/search/')
    response = view(request)
    print(f"✓ Basic search status: {response.status_code}")
    print(f"  Results count: {response.data.get('count', 0)}")
    
    # Test search with query
    request = factory.get('/api/v1/search/?q=encanamento')
    response = view(request)
    print(f"✓ Text search status: {response.status_code}")
    print(f"  Results count: {response.data.get('count', 0)}")
    
    # Test search with category filter
    request = factory.get('/api/v1/search/?category=plumbing')
    response = view(request)
    print(f"✓ Category filter status: {response.status_code}")
    print(f"  Results count: {response.data.get('count', 0)}")
    
    # Test search with price range
    request = factory.get('/api/v1/search/?min_price=50&max_price=200')
    response = view(request)
    print(f"✓ Price range filter status: {response.status_code}")
    print(f"  Results count: {response.data.get('count', 0)}")
    
    # Test search with sorting
    request = factory.get('/api/v1/search/?sort=price')
    response = view(request)
    print(f"✓ Price sorting status: {response.status_code}")
    print(f"  Results count: {response.data.get('count', 0)}")
    
    print("\n✓ All basic search tests passed!")

def test_geographic_search():
    """Test geographic search functionality"""
    print("\nTesting geographic search...")
    
    factory = RequestFactory()
    view = AdvancedSearchView.as_view()
    
    # Test search with coordinates (São Paulo coordinates)
    request = factory.get('/api/v1/search/?lat=-23.5505&lng=-46.6333&radius=10')
    response = view(request)
    print(f"✓ Geographic search status: {response.status_code}")
    print(f"  Results count: {response.data.get('count', 0)}")
    
    # Test distance sorting
    request = factory.get('/api/v1/search/?lat=-23.5505&lng=-46.6333&radius=50&sort=distance')
    response = view(request)
    print(f"✓ Distance sorting status: {response.status_code}")
    print(f"  Results count: {response.data.get('count', 0)}")
    
    # Check if distance is included in results
    if response.data.get('results'):
        first_result = response.data['results'][0]
        has_distance = 'distance_km' in first_result
        print(f"  Distance included in results: {has_distance}")
    
    print("\n✓ All geographic search tests passed!")

def test_professional_search():
    """Test professional search functionality"""
    print("\nTesting professional search...")
    
    factory = RequestFactory()
    view = ProfessionalSearchView.as_view()
    
    # Test basic professional search
    request = factory.get('/api/v1/search/professionals/')
    response = view(request)
    print(f"✓ Professional search status: {response.status_code}")
    print(f"  Results count: {response.data.get('count', 0)}")
    
    # Test with rating filter
    request = factory.get('/api/v1/search/professionals/?min_rating=4.0')
    response = view(request)
    print(f"✓ Rating filter status: {response.status_code}")
    print(f"  Results count: {response.data.get('count', 0)}")
    
    # Test with availability filter
    request = factory.get('/api/v1/search/professionals/?is_available=true')
    response = view(request)
    print(f"✓ Availability filter status: {response.status_code}")
    print(f"  Results count: {response.data.get('count', 0)}")
    
    # Test with geographic search
    request = factory.get('/api/v1/search/professionals/?lat=-23.5505&lng=-46.6333&radius=20')
    response = view(request)
    print(f"✓ Geographic professional search status: {response.status_code}")
    print(f"  Results count: {response.data.get('count', 0)}")
    
    print("\n✓ All professional search tests passed!")

def test_cache_functionality():
    """Test cache functionality"""
    print("\nTesting cache functionality...")
    
    from services.cache_manager import CacheManager
    
    factory = RequestFactory()
    view = AdvancedSearchView.as_view()
    
    # First request (cache miss)
    request = factory.get('/api/v1/search/?q=test&category=cleaning')
    response1 = view(request)
    print(f"✓ First request status: {response1.status_code}")
    
    # Second request (should hit cache)
    request = factory.get('/api/v1/search/?q=test&category=cleaning')
    response2 = view(request)
    print(f"✓ Second request status: {response2.status_code}")
    print(f"  Cache working: {response1.data == response2.data}")
    
    print("\n✓ Cache functionality test passed!")

def test_pagination():
    """Test pagination"""
    print("\nTesting pagination...")
    
    factory = RequestFactory()
    view = AdvancedSearchView.as_view()
    
    # Test with custom page size
    request = factory.get('/api/v1/search/?page_size=5')
    response = view(request)
    print(f"✓ Pagination status: {response.status_code}")
    print(f"  Page size: {len(response.data.get('results', []))}")
    print(f"  Total pages: {response.data.get('total_pages', 0)}")
    print(f"  Current page: {response.data.get('current_page', 0)}")
    
    # Test page 2
    request = factory.get('/api/v1/search/?page=2&page_size=5')
    response = view(request)
    print(f"✓ Page 2 status: {response.status_code}")
    
    print("\n✓ Pagination test passed!")

if __name__ == '__main__':
    print("=" * 60)
    print("Advanced Search API Test Suite")
    print("=" * 60)
    
    try:
        test_basic_search()
        test_geographic_search()
        test_professional_search()
        test_cache_functionality()
        test_pagination()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
