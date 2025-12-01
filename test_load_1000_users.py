"""
Load Test with 1000 Concurrent Users

This script simulates 1000 concurrent users to test system scalability.
Uses threading to simulate concurrent requests.

Requirements:
- Test with 1000 concurrent users
- Validate response times remain acceptable under load

Usage:
    python test_load_1000_users.py
"""

import os
import django
import time
import statistics
import threading
from queue import Queue
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

from django.test import RequestFactory
from services.api.search_views import AdvancedSearchView, ProfessionalSearchView


class LoadTester:
    """Load testing with concurrent users."""
    
    def __init__(self, num_users=1000, requests_per_user=5):
        self.num_users = num_users
        self.requests_per_user = requests_per_user
        self.factory = RequestFactory()
        self.results_queue = Queue()
        self.errors_queue = Queue()
    
    def simulate_user(self, user_id):
        """Simulate a single user making requests."""
        search_view = AdvancedSearchView.as_view()
        professional_view = ProfessionalSearchView.as_view()
        
        # Different request patterns for variety
        test_requests = [
            (self.factory.get('/api/v1/search/'), search_view),
            (self.factory.get('/api/v1/search/?q=encanamento'), search_view),
            (self.factory.get('/api/v1/search/?category=plumbing'), search_view),
            (self.factory.get('/api/v1/search/?min_price=50&max_price=200'), search_view),
            (self.factory.get('/api/v1/search/professionals/'), professional_view),
        ]
        
        user_times = []
        user_errors = 0
        
        for i in range(self.requests_per_user):
            request, view = test_requests[i % len(test_requests)]
            
            start_time = time.time()
            try:
                response = view(request)
                elapsed = (time.time() - start_time) * 1000  # ms
                user_times.append(elapsed)
            except Exception as e:
                elapsed = (time.time() - start_time) * 1000
                user_errors += 1
                self.errors_queue.put({
                    'user_id': user_id,
                    'error': str(e),
                    'time': elapsed
                })
        
        # Store results
        self.results_queue.put({
            'user_id': user_id,
            'times': user_times,
            'errors': user_errors
        })
    
    def run_load_test(self):
        """Execute load test with concurrent users."""
        print("="*70)
        print("LOAD TEST: 1000 CONCURRENT USERS")
        print("="*70)
        print(f"Number of users: {self.num_users}")
        print(f"Requests per user: {self.requests_per_user}")
        print(f"Total requests: {self.num_users * self.requests_per_user}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        print("\nStarting load test...")
        start_time = time.time()
        
        # Create and start threads
        threads = []
        batch_size = 100  # Process in batches to avoid overwhelming the system
        
        for batch_start in range(0, self.num_users, batch_size):
            batch_end = min(batch_start + batch_size, self.num_users)
            batch_threads = []
            
            print(f"Starting users {batch_start+1} to {batch_end}...")
            
            for user_id in range(batch_start, batch_end):
                thread = threading.Thread(target=self.simulate_user, args=(user_id,))
                thread.start()
                batch_threads.append(thread)
            
            # Wait for batch to complete before starting next batch
            for thread in batch_threads:
                thread.join()
            
            threads.extend(batch_threads)
        
        total_time = time.time() - start_time
        
        print(f"\nLoad test completed in {total_time:.2f} seconds")
        
        # Collect and analyze results
        self.analyze_results(total_time)
    
    def analyze_results(self, total_time):
        """Analyze and display test results."""
        print("\n" + "="*70)
        print("LOAD TEST RESULTS")
        print("="*70)
        
        # Collect all results
        all_times = []
        total_errors = 0
        successful_users = 0
        
        while not self.results_queue.empty():
            result = self.results_queue.get()
            all_times.extend(result['times'])
            total_errors += result['errors']
            if result['errors'] == 0:
                successful_users += 1
        
        # Collect errors
        errors = []
        while not self.errors_queue.empty():
            errors.append(self.errors_queue.get())
        
        if not all_times:
            print("\n✗ FAILED: No successful requests")
            return False
        
        # Calculate statistics
        total_requests = len(all_times)
        successful_requests = total_requests - total_errors
        avg_time = statistics.mean(all_times)
        median_time = statistics.median(all_times)
        min_time = min(all_times)
        max_time = max(all_times)
        
        # Calculate percentiles
        sorted_times = sorted(all_times)
        p50_time = sorted_times[len(sorted_times) // 2]
        p95_time = sorted_times[int(len(sorted_times) * 0.95)]
        p99_time = sorted_times[int(len(sorted_times) * 0.99)]
        
        # Calculate throughput
        throughput = total_requests / total_time
        
        # Calculate percentage under 500ms
        under_500 = sum(1 for t in all_times if t < 500)
        percentage_under_500 = (under_500 / total_requests) * 100
        
        # Calculate percentage under 1000ms
        under_1000 = sum(1 for t in all_times if t < 1000)
        percentage_under_1000 = (under_1000 / total_requests) * 100
        
        # Display results
        print(f"\nTest Duration: {total_time:.2f} seconds")
        print(f"Throughput: {throughput:.2f} requests/second")
        
        print(f"\nRequest Statistics:")
        print(f"  Total requests: {total_requests}")
        print(f"  Successful: {successful_requests} ({(successful_requests/total_requests)*100:.1f}%)")
        print(f"  Failed: {total_errors} ({(total_errors/total_requests)*100:.1f}%)")
        
        print(f"\nUser Statistics:")
        print(f"  Total users: {self.num_users}")
        print(f"  Users with no errors: {successful_users} ({(successful_users/self.num_users)*100:.1f}%)")
        
        print(f"\nResponse Time Statistics:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Median (P50): {median_time:.2f}ms")
        print(f"  P95: {p95_time:.2f}ms")
        print(f"  P99: {p99_time:.2f}ms")
        print(f"  Min: {min_time:.2f}ms")
        print(f"  Max: {max_time:.2f}ms")
        
        print(f"\nPerformance Targets:")
        print(f"  Requests < 500ms: {under_500}/{total_requests} ({percentage_under_500:.1f}%)")
        print(f"  Requests < 1000ms: {under_1000}/{total_requests} ({percentage_under_1000:.1f}%)")
        
        # Show error samples if any
        if errors:
            print(f"\nError Samples (showing first 10):")
            for error in errors[:10]:
                print(f"  User {error['user_id']}: {error['error'][:100]}")
        
        print("\n" + "="*70)
        print("PERFORMANCE EVALUATION")
        print("="*70)
        
        # Evaluate against requirements
        passed_tests = []
        failed_tests = []
        
        # Test 1: 95% under 500ms
        if percentage_under_500 >= 95:
            passed_tests.append(f"✓ Response time: {percentage_under_500:.1f}% under 500ms (target: ≥95%)")
        else:
            failed_tests.append(f"✗ Response time: {percentage_under_500:.1f}% under 500ms (target: ≥95%)")
        
        # Test 2: P95 under 500ms
        if p95_time < 500:
            passed_tests.append(f"✓ P95 response time: {p95_time:.2f}ms (target: <500ms)")
        else:
            failed_tests.append(f"✗ P95 response time: {p95_time:.2f}ms (target: <500ms)")
        
        # Test 3: Error rate under 5%
        error_rate = (total_errors / total_requests) * 100
        if error_rate < 5:
            passed_tests.append(f"✓ Error rate: {error_rate:.1f}% (target: <5%)")
        else:
            failed_tests.append(f"✗ Error rate: {error_rate:.1f}% (target: <5%)")
        
        # Test 4: Throughput reasonable (at least 50 req/s)
        if throughput >= 50:
            passed_tests.append(f"✓ Throughput: {throughput:.2f} req/s (target: ≥50 req/s)")
        else:
            failed_tests.append(f"✗ Throughput: {throughput:.2f} req/s (target: ≥50 req/s)")
        
        # Display results
        if passed_tests:
            print("\nPassed Tests:")
            for test in passed_tests:
                print(f"  {test}")
        
        if failed_tests:
            print("\nFailed Tests:")
            for test in failed_tests:
                print(f"  {test}")
        
        print("\n" + "="*70)
        
        all_passed = len(failed_tests) == 0
        
        if all_passed:
            print("✓ LOAD TEST PASSED: System handles 1000 concurrent users successfully")
        else:
            print("✗ LOAD TEST FAILED: System needs optimization for 1000 concurrent users")
        
        print("="*70)
        
        return all_passed


def main():
    """Main entry point for load testing."""
    print("\nInitializing load test with 1000 concurrent users...")
    print("This may take several minutes to complete.\n")
    
    # Run with 1000 users, 5 requests each = 5000 total requests
    tester = LoadTester(num_users=1000, requests_per_user=5)
    success = tester.run_load_test()
    
    exit(0 if success else 1)


if __name__ == '__main__':
    main()
