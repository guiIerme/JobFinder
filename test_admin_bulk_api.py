"""
Test script for Admin Bulk Operations API

This script tests the admin bulk operations, export, and async processing APIs.
Run with: python test_admin_bulk_api.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = 'http://localhost:8000'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'  # Change this to your admin password

class AdminBulkAPITester:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.token = None
    
    def login(self):
        """Login and get authentication token or session."""
        print(f"\n{'='*60}")
        print("LOGGING IN AS ADMIN")
        print(f"{'='*60}")
        
        # Try to login via Django's login endpoint
        login_url = f"{self.base_url}/login/"
        response = self.session.post(login_url, data={
            'username': self.username,
            'password': self.password
        })
        
        if response.status_code == 200:
            print("✓ Login successful")
            return True
        else:
            print(f"✗ Login failed: {response.status_code}")
            return False
    
    def test_bulk_order_update(self):
        """Test bulk order status update."""
        print(f"\n{'='*60}")
        print("TEST 1: Bulk Order Status Update")
        print(f"{'='*60}")
        
        url = f"{self.base_url}/api/v1/admin/bulk/orders/update-status/"
        data = {
            'order_ids': [1, 2, 3],
            'status': 'completed',
            'notes': 'Bulk completion test'
        }
        
        print(f"POST {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = self.session.post(url, json=data)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Success: {result['updated_count']} orders updated")
            print(f"  Failed: {result['failed_count']}")
            print(f"\nResults:")
            for r in result['results'][:3]:  # Show first 3
                print(f"  - Order {r['order_id']}: {r.get('status', 'N/A')} ({'✓' if r['success'] else '✗'})")
        else:
            print(f"✗ Failed: {response.text}")
    
    def test_bulk_professional_approval(self):
        """Test bulk professional approval."""
        print(f"\n{'='*60}")
        print("TEST 2: Bulk Professional Approval")
        print(f"{'='*60}")
        
        url = f"{self.base_url}/api/v1/admin/bulk/professionals/approve/"
        data = {
            'user_ids': [2, 3, 4],
            'is_verified': True,
            'is_premium': False
        }
        
        print(f"POST {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = self.session.post(url, json=data)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Success: {result['updated_count']} professionals updated")
            print(f"  Failed: {result['failed_count']}")
            print(f"\nResults:")
            for r in result['results'][:3]:
                print(f"  - User {r.get('username', 'N/A')}: Verified={r.get('is_verified', False)} ({'✓' if r['success'] else '✗'})")
        else:
            print(f"✗ Failed: {response.text}")
    
    def test_export_orders_json(self):
        """Test order export in JSON format."""
        print(f"\n{'='*60}")
        print("TEST 3: Export Orders (JSON)")
        print(f"{'='*60}")
        
        url = f"{self.base_url}/api/v1/admin/export/orders/"
        params = {
            'format': 'json',
            'limit': 10
        }
        
        print(f"GET {url}")
        print(f"Params: {params}")
        
        response = self.session.get(url, params=params)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Success: Retrieved {len(result['results'])} orders")
            print(f"  Total count: {result['count']}")
            print(f"  Has more: {result['has_more']}")
            if result['results']:
                print(f"\nFirst order:")
                order = result['results'][0]
                print(f"  ID: {order['id']}")
                print(f"  Customer: {order['customer']['username']}")
                print(f"  Status: {order['status_display']}")
        else:
            print(f"✗ Failed: {response.text}")
    
    def test_export_orders_csv(self):
        """Test order export in CSV format."""
        print(f"\n{'='*60}")
        print("TEST 4: Export Orders (CSV)")
        print(f"{'='*60}")
        
        url = f"{self.base_url}/api/v1/admin/export/orders/"
        params = {
            'format': 'csv',
            'limit': 10
        }
        
        print(f"GET {url}")
        print(f"Params: {params}")
        
        response = self.session.get(url, params=params)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✓ Success: CSV file downloaded")
            print(f"  Content-Type: {response.headers.get('Content-Type')}")
            print(f"  Content-Disposition: {response.headers.get('Content-Disposition')}")
            print(f"  Total Count: {response.headers.get('X-Total-Count')}")
            
            # Show first few lines
            lines = response.text.split('\n')[:5]
            print(f"\nFirst 5 lines:")
            for line in lines:
                print(f"  {line}")
        else:
            print(f"✗ Failed: {response.text}")
    
    def test_export_users(self):
        """Test user export."""
        print(f"\n{'='*60}")
        print("TEST 5: Export Users (JSON)")
        print(f"{'='*60}")
        
        url = f"{self.base_url}/api/v1/admin/export/users/"
        params = {
            'format': 'json',
            'limit': 10,
            'user_type': 'professional'
        }
        
        print(f"GET {url}")
        print(f"Params: {params}")
        
        response = self.session.get(url, params=params)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Success: Retrieved {len(result['results'])} users")
            print(f"  Total count: {result['count']}")
            if result['results']:
                print(f"\nFirst user:")
                user = result['results'][0]
                print(f"  Username: {user['username']}")
                print(f"  Email: {user['email']}")
                if user['profile']:
                    print(f"  Type: {user['profile']['user_type']}")
                    print(f"  Verified: {user['profile']['is_verified']}")
        else:
            print(f"✗ Failed: {response.text}")
    
    def test_async_bulk_operation(self):
        """Test async bulk operation submission and status polling."""
        print(f"\n{'='*60}")
        print("TEST 6: Async Bulk Operation")
        print(f"{'='*60}")
        
        # Submit async operation
        url = f"{self.base_url}/api/v1/admin/async/submit/"
        data = {
            'operation_type': 'order_update',
            'operations': [
                {'resource_id': 1, 'data': {'status': 'in_progress'}},
                {'resource_id': 2, 'data': {'status': 'in_progress'}},
                {'resource_id': 3, 'data': {'status': 'in_progress'}}
            ],
            'notify_on_completion': True
        }
        
        print(f"POST {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = self.session.post(url, json=data)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 202:
            result = response.json()
            batch_id = result['batch_id']
            print(f"✓ Batch submitted: ID={batch_id}")
            print(f"  Status: {result['status']}")
            print(f"  Total operations: {result['total_operations']}")
            print(f"  Estimated duration: {result['estimated_duration_seconds']}s")
            
            # Poll for status
            print(f"\nPolling for status...")
            status_url = f"{self.base_url}/api/v1/admin/async/status/{batch_id}/"
            
            for i in range(5):
                time.sleep(1)
                status_response = self.session.get(status_url)
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    progress = status_result['progress']
                    print(f"  [{i+1}] Status: {status_result['status']} - Progress: {progress['percentage']}% ({progress['completed']}/{progress['total']})")
                    
                    if status_result['status'] in ['completed', 'failed', 'partial']:
                        print(f"\n✓ Batch completed!")
                        print(f"  Success rate: {progress['success_rate']}%")
                        print(f"  Duration: {status_result['duration_seconds']}s")
                        break
                else:
                    print(f"  ✗ Status check failed: {status_response.status_code}")
                    break
        else:
            print(f"✗ Failed: {response.text}")
    
    def run_all_tests(self):
        """Run all tests."""
        print(f"\n{'#'*60}")
        print("ADMIN BULK OPERATIONS API TEST SUITE")
        print(f"{'#'*60}")
        print(f"Base URL: {self.base_url}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not self.login():
            print("\n✗ Cannot proceed without authentication")
            return
        
        # Run tests
        self.test_bulk_order_update()
        self.test_bulk_professional_approval()
        self.test_export_orders_json()
        self.test_export_orders_csv()
        self.test_export_users()
        self.test_async_bulk_operation()
        
        print(f"\n{'#'*60}")
        print("TEST SUITE COMPLETED")
        print(f"{'#'*60}\n")


if __name__ == '__main__':
    tester = AdminBulkAPITester(BASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD)
    tester.run_all_tests()
