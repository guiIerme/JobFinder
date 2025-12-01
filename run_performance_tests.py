"""
Master Performance Test Runner

Executes all performance tests and generates a comprehensive report.

Tests included:
1. Response time validation (< 500ms for 95% of requests)
2. Compression ratio testing (> 60%)
3. Cache hit rate measurement
4. Load testing with 1000 concurrent users

Requirements validated:
- 3.5: Response time < 500ms for 95% of requests
- 5.4: Compression ratio > 60%
- 6.5: Cache hit rate monitoring

Usage:
    python run_performance_tests.py
"""

import subprocess
import sys
import time
from datetime import datetime


class PerformanceTestRunner:
    """Master test runner for all performance tests."""
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def print_header(self):
        """Print test suite header."""
        print("\n" + "="*80)
        print(" "*20 + "PERFORMANCE TEST SUITE")
        print(" "*15 + "API Optimization - Task 14.4")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        print("\nThis suite will run the following tests:")
        print("  1. Comprehensive Performance Tests")
        print("     - Response time validation")
        print("     - Compression ratio testing")
        print("     - Cache hit rate measurement")
        print("     - Concurrent load testing (100 users)")
        print("\n  2. Load Test with 1000 Concurrent Users")
        print("     - Scalability testing")
        print("     - System stability under load")
        print("\n  3. Search API Performance Tests")
        print("     - Endpoint-specific performance")
        print("\n  4. CDN Performance Tests")
        print("     - Cache effectiveness")
        print("     - Loading time improvements")
        print("\n" + "="*80)
    
    def run_test(self, test_name, script_name):
        """Run a single test script."""
        print(f"\n{'='*80}")
        print(f"Running: {test_name}")
        print(f"Script: {script_name}")
        print(f"{'='*80}\n")
        
        start = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, script_name],
                capture_output=False,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            elapsed = time.time() - start
            success = result.returncode == 0
            
            self.results[test_name] = {
                'success': success,
                'elapsed': elapsed,
                'script': script_name
            }
            
            status = "✓ PASSED" if success else "✗ FAILED"
            print(f"\n{status} - {test_name} completed in {elapsed:.2f} seconds")
            
            return success
            
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start
            print(f"\n✗ TIMEOUT - {test_name} exceeded 10 minute limit")
            
            self.results[test_name] = {
                'success': False,
                'elapsed': elapsed,
                'script': script_name,
                'error': 'Timeout'
            }
            
            return False
            
        except Exception as e:
            elapsed = time.time() - start
            print(f"\n✗ ERROR - {test_name} failed with error: {e}")
            
            self.results[test_name] = {
                'success': False,
                'elapsed': elapsed,
                'script': script_name,
                'error': str(e)
            }
            
            return False
    
    def print_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "="*80)
        print(" "*25 + "TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r['success'])
        failed_tests = total_tests - passed_tests
        total_time = self.end_time - self.start_time
        
        print(f"\nTotal tests run: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Total execution time: {total_time:.2f} seconds ({total_time/60:.1f} minutes)")
        
        print("\n" + "-"*80)
        print("Individual Test Results:")
        print("-"*80)
        
        for test_name, result in self.results.items():
            status = "✓ PASS" if result['success'] else "✗ FAIL"
            elapsed = result['elapsed']
            
            print(f"\n{status} {test_name}")
            print(f"     Time: {elapsed:.2f}s")
            print(f"     Script: {result['script']}")
            
            if 'error' in result:
                print(f"     Error: {result['error']}")
        
        print("\n" + "="*80)
        print("REQUIREMENTS VALIDATION")
        print("="*80)
        
        # Map tests to requirements
        requirements = {
            'Requirement 3.5 (Response time < 500ms for 95%)': [
                'Comprehensive Performance Tests',
                'Load Test (1000 Users)',
                'Search API Performance'
            ],
            'Requirement 5.4 (Compression ratio > 60%)': [
                'Comprehensive Performance Tests'
            ],
            'Requirement 6.5 (Cache hit rate monitoring)': [
                'Comprehensive Performance Tests',
                'CDN Performance Tests'
            ],
            'Load Testing (1000 concurrent users)': [
                'Load Test (1000 Users)'
            ]
        }
        
        for req, tests in requirements.items():
            req_passed = all(
                self.results.get(test, {}).get('success', False)
                for test in tests
                if test in self.results
            )
            
            status = "✓" if req_passed else "✗"
            print(f"\n{status} {req}")
            
            for test in tests:
                if test in self.results:
                    test_status = "✓" if self.results[test]['success'] else "✗"
                    print(f"   {test_status} {test}")
        
        print("\n" + "="*80)
        
        if failed_tests == 0:
            print("✓ ALL PERFORMANCE TESTS PASSED")
            print("\nThe system meets all performance requirements:")
            print("  • Response times < 500ms for 95% of requests")
            print("  • Compression ratio > 60%")
            print("  • Cache hit rate is measurable and effective")
            print("  • System handles 1000 concurrent users")
        else:
            print("✗ SOME PERFORMANCE TESTS FAILED")
            print(f"\n{failed_tests} test(s) need attention.")
            print("Review the individual test results above for details.")
        
        print("\n" + "="*80)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        return failed_tests == 0
    
    def run_all_tests(self):
        """Run all performance tests."""
        self.print_header()
        
        input("\nPress Enter to start the performance test suite...")
        
        self.start_time = time.time()
        
        # Test 1: Comprehensive performance tests
        self.run_test(
            "Comprehensive Performance Tests",
            "test_comprehensive_performance.py"
        )
        
        # Test 2: Load test with 1000 users
        print("\n" + "="*80)
        print("IMPORTANT: The next test will simulate 1000 concurrent users.")
        print("This is a heavy load test and may take 5-10 minutes.")
        print("="*80)
        
        proceed = input("\nProceed with 1000 user load test? (y/n): ").lower()
        
        if proceed == 'y':
            self.run_test(
                "Load Test (1000 Users)",
                "test_load_1000_users.py"
            )
        else:
            print("\nSkipping 1000 user load test.")
            self.results["Load Test (1000 Users)"] = {
                'success': None,
                'elapsed': 0,
                'script': 'test_load_1000_users.py',
                'skipped': True
            }
        
        # Test 3: Search API performance
        self.run_test(
            "Search API Performance",
            "test_search_performance.py"
        )
        
        # Test 4: CDN performance
        self.run_test(
            "CDN Performance Tests",
            "test_cdn_performance.py"
        )
        
        self.end_time = time.time()
        
        # Print summary
        return self.print_summary()


def main():
    """Main entry point."""
    runner = PerformanceTestRunner()
    success = runner.run_all_tests()
    
    exit(0 if success else 1)


if __name__ == '__main__':
    main()
