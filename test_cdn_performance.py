"""
Test script for CDN performance and cache effectiveness.

This script tests the CDN integration and validates that:
- Cache headers are properly set
- ETags are generated and validated
- Loading time reduction meets the 70% requirement

Requirements:
- 9.2: Validate cache headers (30 days for static files)
- 9.5: Validate reduction of loading time > 70%

Usage:
    python test_cdn_performance.py
"""

import requests
import time
import statistics
from typing import Dict, List
import sys


class CDNPerformanceTester:
    """Test CDN performance and cache effectiveness."""
    
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url.rstrip('/')
        self.results = {
            'cache_headers': [],
            'etag_tests': [],
            'performance': [],
        }
    
    def test_static_cache_headers(self):
        """
        Test that static files have proper cache headers.
        
        Requirement 9.2: Cache-Control for static files (30 days)
        """
        print("\n" + "="*60)
        print("Testing Static File Cache Headers")
        print("="*60)
        
        # Test various static file types
        static_files = [
            '/static/css/style.css',
            '/static/js/main.js',
            '/static/images/logo.png',
        ]
        
        for file_path in static_files:
            url = f"{self.base_url}{file_path}"
            
            try:
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    cache_control = response.headers.get('Cache-Control', '')
                    etag = response.headers.get('ETag', '')
                    
                    print(f"\n{file_path}:")
                    print(f"  Status: {response.status_code}")
                    print(f"  Cache-Control: {cache_control}")
                    print(f"  ETag: {etag}")
                    
                    # Validate cache duration (30 days = 2592000 seconds)
                    if 'max-age=2592000' in cache_control:
                        print("  ✓ Cache duration is correct (30 days)")
                        self.results['cache_headers'].append({
                            'file': file_path,
                            'status': 'pass',
                            'cache_control': cache_control
                        })
                    else:
                        print("  ✗ Cache duration is incorrect")
                        self.results['cache_headers'].append({
                            'file': file_path,
                            'status': 'fail',
                            'cache_control': cache_control
                        })
                else:
                    print(f"\n{file_path}: Not found (404)")
                    
            except requests.exceptions.RequestException as e:
                print(f"\n{file_path}: Error - {e}")
    
    def test_media_cache_headers(self):
        """
        Test that media files have proper cache headers.
        
        Requirement 9.2: Cache-Control for media files (30 days)
        """
        print("\n" + "="*60)
        print("Testing Media File Cache Headers")
        print("="*60)
        
        # Test media files (if any exist)
        media_files = [
            '/media/avatars/default.png',
        ]
        
        for file_path in media_files:
            url = f"{self.base_url}{file_path}"
            
            try:
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    cache_control = response.headers.get('Cache-Control', '')
                    etag = response.headers.get('ETag', '')
                    
                    print(f"\n{file_path}:")
                    print(f"  Status: {response.status_code}")
                    print(f"  Cache-Control: {cache_control}")
                    print(f"  ETag: {etag}")
                    
                    # Validate cache duration
                    if 'max-age=2592000' in cache_control:
                        print("  ✓ Cache duration is correct (30 days)")
                    else:
                        print("  ✗ Cache duration is incorrect")
                else:
                    print(f"\n{file_path}: Not found (404)")
                    
            except requests.exceptions.RequestException as e:
                print(f"\n{file_path}: Error - {e}")
    
    def test_etag_validation(self):
        """
        Test ETag generation and validation.
        
        Requirement 9.5: Configure ETags for validation
        """
        print("\n" + "="*60)
        print("Testing ETag Validation")
        print("="*60)
        
        test_url = f"{self.base_url}/static/css/style.css"
        
        try:
            # First request - get ETag
            print("\nFirst request (no cache):")
            response1 = requests.get(test_url, timeout=5)
            
            if response1.status_code == 200:
                etag = response1.headers.get('ETag')
                print(f"  Status: {response1.status_code}")
                print(f"  ETag: {etag}")
                print(f"  Content-Length: {len(response1.content)} bytes")
                
                if etag:
                    # Second request - with If-None-Match
                    print("\nSecond request (with If-None-Match):")
                    headers = {'If-None-Match': etag}
                    response2 = requests.get(test_url, headers=headers, timeout=5)
                    
                    print(f"  Status: {response2.status_code}")
                    
                    if response2.status_code == 304:
                        print("  ✓ ETag validation working (304 Not Modified)")
                        self.results['etag_tests'].append({
                            'url': test_url,
                            'status': 'pass'
                        })
                    else:
                        print("  ✗ ETag validation not working")
                        self.results['etag_tests'].append({
                            'url': test_url,
                            'status': 'fail'
                        })
                else:
                    print("  ✗ No ETag header found")
            else:
                print(f"  Error: Status {response1.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"  Error: {e}")
    
    def test_loading_performance(self, iterations=10):
        """
        Test loading performance with and without cache.
        
        Requirement 9.5: Validate reduction of loading time > 70%
        """
        print("\n" + "="*60)
        print("Testing Loading Performance")
        print("="*60)
        
        test_urls = [
            f"{self.base_url}/",
            f"{self.base_url}/static/css/style.css",
        ]
        
        for url in test_urls:
            print(f"\nTesting: {url}")
            
            # Measure without cache (first load)
            print(f"  Running {iterations} iterations (cold cache)...")
            cold_times = []
            
            for i in range(iterations):
                try:
                    # Add cache-busting parameter
                    test_url = f"{url}?nocache={time.time()}"
                    start = time.time()
                    response = requests.get(test_url, timeout=10)
                    elapsed = (time.time() - start) * 1000  # Convert to ms
                    
                    if response.status_code == 200:
                        cold_times.append(elapsed)
                except requests.exceptions.RequestException as e:
                    print(f"    Error on iteration {i+1}: {e}")
            
            if cold_times:
                avg_cold = statistics.mean(cold_times)
                print(f"  Average cold load time: {avg_cold:.2f}ms")
                
                # Measure with cache (subsequent loads)
                print(f"  Running {iterations} iterations (warm cache)...")
                warm_times = []
                
                for i in range(iterations):
                    try:
                        start = time.time()
                        response = requests.get(url, timeout=10)
                        elapsed = (time.time() - start) * 1000
                        
                        if response.status_code == 200:
                            warm_times.append(elapsed)
                    except requests.exceptions.RequestException as e:
                        print(f"    Error on iteration {i+1}: {e}")
                
                if warm_times:
                    avg_warm = statistics.mean(warm_times)
                    print(f"  Average warm load time: {avg_warm:.2f}ms")
                    
                    # Calculate improvement
                    if avg_cold > 0:
                        improvement = ((avg_cold - avg_warm) / avg_cold) * 100
                        print(f"  Performance improvement: {improvement:.1f}%")
                        
                        self.results['performance'].append({
                            'url': url,
                            'cold_time': avg_cold,
                            'warm_time': avg_warm,
                            'improvement': improvement
                        })
                        
                        # Check if meets 70% requirement
                        if improvement >= 70:
                            print(f"  ✓ Meets 70% improvement requirement")
                        else:
                            print(f"  ⚠ Does not meet 70% improvement requirement")
    
    def print_summary(self):
        """Print a summary of all test results."""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        # Cache headers summary
        print("\nCache Headers Tests:")
        passed = sum(1 for r in self.results['cache_headers'] if r['status'] == 'pass')
        total = len(self.results['cache_headers'])
        print(f"  Passed: {passed}/{total}")
        
        # ETag tests summary
        print("\nETag Validation Tests:")
        passed = sum(1 for r in self.results['etag_tests'] if r['status'] == 'pass')
        total = len(self.results['etag_tests'])
        print(f"  Passed: {passed}/{total}")
        
        # Performance tests summary
        print("\nPerformance Tests:")
        if self.results['performance']:
            avg_improvement = statistics.mean([r['improvement'] for r in self.results['performance']])
            print(f"  Average improvement: {avg_improvement:.1f}%")
            
            meets_requirement = avg_improvement >= 70
            if meets_requirement:
                print(f"  ✓ Meets 70% improvement requirement")
            else:
                print(f"  ✗ Does not meet 70% improvement requirement")
        else:
            print("  No performance data collected")
        
        print("\n" + "="*60)
    
    def run_all_tests(self):
        """Run all CDN performance tests."""
        print("Starting CDN Performance Tests")
        print(f"Base URL: {self.base_url}")
        
        self.test_static_cache_headers()
        self.test_media_cache_headers()
        self.test_etag_validation()
        self.test_loading_performance()
        
        self.print_summary()


def main():
    """Main entry point for the test script."""
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8000'
    
    tester = CDNPerformanceTester(base_url)
    tester.run_all_tests()


if __name__ == '__main__':
    main()
