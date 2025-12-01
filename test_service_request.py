import requests
import json

# Test the service request submission
url = 'http://127.0.0.1:8000/submit-service-request/'

# Sample data for the service request
data = {
    'title': 'Test Service Request',
    'description': 'This is a test service request',
    'category': 'repair',
    'scheduled_date': '2025-10-25T10:00',
    'address': '123 Test Street, Test City',
    'notes': 'Please call before arriving'
}

# Send the request
response = requests.post(url, json=data)

# Print the response
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")