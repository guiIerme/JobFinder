# Admin Bulk Operations API Documentation

## Overview

This document describes the Admin Bulk Operations API endpoints that allow administrators to efficiently manage orders, professionals, and other resources in batch operations. The API supports synchronous bulk operations, data export in multiple formats, and asynchronous processing for long-running tasks.

**Requirements Implemented:**
- 11.1: Bulk operations for orders and professionals
- 11.2: Admin permissions and validation
- 11.3: Data export in CSV and JSON formats
- 11.4: Asynchronous processing for long operations
- 11.5: Progress tracking and completion notifications

## Authentication

All endpoints require admin authentication. Include authentication credentials in your requests:

- **Session-based**: Login via `/login/` endpoint
- **Token-based**: Include `Authorization: Bearer <token>` header (if JWT is configured)

## Base URL

```
/api/v1/admin/
```

---

## 1. Bulk Operations

### 1.1 Bulk Order Status Update

Update the status of multiple orders in a single request.

**Endpoint:** `POST /api/v1/admin/bulk/orders/update-status/`

**Permissions:** Admin only

**Request Body:**
```json
{
  "order_ids": [1, 2, 3, 4, 5],
  "status": "completed",
  "notes": "Bulk completion by admin"
}
```

**Parameters:**
- `order_ids` (array, required): List of order IDs to update
- `status` (string, required): New status value. Valid values:
  - `pending`
  - `confirmed`
  - `in_progress`
  - `completed`
  - `cancelled`
- `notes` (string, optional): Additional notes to append to orders

**Response (200 OK):**
```json
{
  "success": true,
  "updated_count": 5,
  "failed_count": 0,
  "total_count": 5,
  "results": [
    {
      "order_id": 1,
      "success": true,
      "status": "completed",
      "customer": "john_doe"
    },
    {
      "order_id": 2,
      "success": false,
      "error": "Order not found"
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request`: Invalid parameters
- `403 Forbidden`: Not an admin user

---

### 1.2 Bulk Professional Approval

Approve, verify, or update the status of multiple professionals.

**Endpoint:** `POST /api/v1/admin/bulk/professionals/approve/`

**Permissions:** Admin only

**Request Body:**
```json
{
  "user_ids": [2, 3, 4, 5],
  "is_verified": true,
  "is_premium": false,
  "is_available": true
}
```

**Parameters:**
- `user_ids` (array, required): List of user IDs (professionals) to update
- `is_verified` (boolean, optional): Set verification status
- `is_premium` (boolean, optional): Set premium status
- `is_available` (boolean, optional): Set availability status

**Note:** At least one of the boolean fields must be provided.

**Response (200 OK):**
```json
{
  "success": true,
  "updated_count": 4,
  "failed_count": 0,
  "total_count": 4,
  "results": [
    {
      "user_id": 2,
      "username": "john_plumber",
      "success": true,
      "is_verified": true,
      "is_premium": false,
      "is_available": true
    }
  ]
}
```

---

### 1.3 Bulk Service Update

Activate or deactivate multiple services.

**Endpoint:** `POST /api/v1/admin/bulk/services/update/`

**Permissions:** Admin only

**Request Body:**
```json
{
  "service_ids": [1, 2, 3, 4, 5],
  "is_active": true
}
```

**Parameters:**
- `service_ids` (array, required): List of service IDs to update
- `is_active` (boolean, required): Set active status

**Response (200 OK):**
```json
{
  "success": true,
  "updated_count": 5,
  "failed_count": 0,
  "total_count": 5,
  "results": [
    {
      "service_id": 1,
      "name": "Plumbing Service",
      "provider": "john_plumber",
      "success": true,
      "is_active": true
    }
  ]
}
```

---

## 2. Data Export

### 2.1 Export Orders

Export order data in CSV or JSON format with pagination support.

**Endpoint:** `GET /api/v1/admin/export/orders/`

**Permissions:** Admin only

**Query Parameters:**
- `format` (string, optional): Export format. Values: `json` (default), `csv`
- `status` (string, optional): Filter by order status
- `start_date` (string, optional): Filter from date (YYYY-MM-DD)
- `end_date` (string, optional): Filter until date (YYYY-MM-DD)
- `limit` (integer, optional): Max records (default: 1000, max: 10000)
- `offset` (integer, optional): Pagination offset (default: 0)

**JSON Response (200 OK):**
```json
{
  "count": 150,
  "limit": 10,
  "offset": 0,
  "has_more": true,
  "next_offset": 10,
  "results": [
    {
      "id": 1,
      "customer": {
        "id": 5,
        "username": "john_doe",
        "email": "john@example.com"
      },
      "service": {
        "id": 3,
        "name": "Plumbing Repair"
      },
      "professional": {
        "id": 2,
        "username": "jane_plumber"
      },
      "status": "completed",
      "status_display": "Concluído",
      "scheduled_date": "2025-11-20T14:00:00Z",
      "total_price": "150.00",
      "address": "123 Main St",
      "notes": "Fixed kitchen sink",
      "created_at": "2025-11-17T10:30:00Z",
      "updated_at": "2025-11-18T15:45:00Z"
    }
  ]
}
```

**CSV Response (200 OK):**
- Content-Type: `text/csv`
- Content-Disposition: `attachment; filename="orders_export_20251117_103000.csv"`
- Headers: `X-Total-Count`, `X-Offset`, `X-Limit`

CSV Format:
```csv
ID,Customer,Customer Email,Service,Professional,Status,Scheduled Date,Total Price,Address,Created At,Updated At
1,john_doe,john@example.com,Plumbing Repair,jane_plumber,Concluído,2025-11-20 14:00,150.00,123 Main St,2025-11-17 10:30:00,2025-11-18 15:45:00
```

---

### 2.2 Export Users

Export user data in CSV or JSON format.

**Endpoint:** `GET /api/v1/admin/export/users/`

**Permissions:** Admin only

**Query Parameters:**
- `format` (string, optional): Export format. Values: `json` (default), `csv`
- `user_type` (string, optional): Filter by type. Values: `customer`, `professional`, `admin`
- `is_active` (boolean, optional): Filter by active status
- `is_verified` (boolean, optional): Filter verified professionals
- `limit` (integer, optional): Max records (default: 1000, max: 10000)
- `offset` (integer, optional): Pagination offset (default: 0)

**JSON Response (200 OK):**
```json
{
  "count": 50,
  "limit": 10,
  "offset": 0,
  "has_more": true,
  "next_offset": 10,
  "results": [
    {
      "id": 2,
      "username": "jane_plumber",
      "email": "jane@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "is_active": true,
      "date_joined": "2025-01-15T08:00:00Z",
      "profile": {
        "user_type": "professional",
        "phone": "+1234567890",
        "city": "São Paulo",
        "state": "SP",
        "is_verified": true,
        "is_premium": false,
        "is_available": true,
        "rating": "4.75",
        "review_count": 24
      }
    }
  ]
}
```

---

### 2.3 Export Services

Export service data in CSV or JSON format.

**Endpoint:** `GET /api/v1/admin/export/services/`

**Permissions:** Admin only

**Query Parameters:**
- `format` (string, optional): Export format. Values: `json` (default), `csv`
- `is_active` (boolean, optional): Filter by active status
- `category` (string, optional): Filter by category
- `limit` (integer, optional): Max records (default: 1000, max: 10000)
- `offset` (integer, optional): Pagination offset (default: 0)

**JSON Response (200 OK):**
```json
{
  "count": 75,
  "limit": 10,
  "offset": 0,
  "has_more": true,
  "next_offset": 10,
  "results": [
    {
      "id": 1,
      "name": "Emergency Plumbing",
      "description": "24/7 emergency plumbing services",
      "category": "plumbing",
      "category_display": "Encanamento",
      "provider": {
        "id": 2,
        "username": "jane_plumber",
        "email": "jane@example.com"
      },
      "estimated_price": "200.00",
      "is_active": true,
      "created_at": "2025-01-20T10:00:00Z",
      "updated_at": "2025-11-15T14:30:00Z"
    }
  ]
}
```

---

## 3. Asynchronous Processing

For large batch operations that may take significant time, use the async API to submit operations and poll for status.

### 3.1 Submit Async Batch Operation

Submit a batch operation for asynchronous processing.

**Endpoint:** `POST /api/v1/admin/async/submit/`

**Permissions:** Admin only

**Request Body:**
```json
{
  "operation_type": "order_update",
  "operations": [
    {
      "resource_id": 1,
      "data": {"status": "completed"}
    },
    {
      "resource_id": 2,
      "data": {"status": "completed"}
    }
  ],
  "notify_on_completion": true
}
```

**Parameters:**
- `operation_type` (string, required): Type of operation. Values:
  - `order_update`
  - `professional_approval`
  - `service_update`
  - `user_update`
- `operations` (array, required): List of operations (max 1000)
- `notify_on_completion` (boolean, optional): Send notification when complete (default: true)

**Response (202 Accepted):**
```json
{
  "batch_id": 123,
  "status": "pending",
  "message": "Batch operation submitted for processing",
  "poll_url": "/api/v1/admin/async/status/123/",
  "total_operations": 2,
  "estimated_duration_seconds": 1
}
```

---

### 3.2 Check Async Batch Status

Poll for the status and progress of an async batch operation.

**Endpoint:** `GET /api/v1/admin/async/status/{batch_id}/`

**Permissions:** Admin or batch owner

**Response (200 OK) - Processing:**
```json
{
  "batch_id": 123,
  "operation_type": "Atualização de Pedidos",
  "status": "processing",
  "status_display": "Processando",
  "progress": {
    "total": 100,
    "completed": 45,
    "failed": 2,
    "percentage": 47.0,
    "success_rate": 95.74
  },
  "created_at": "2025-11-17T10:30:00Z",
  "started_at": "2025-11-17T10:30:05Z",
  "completed_at": null,
  "duration_seconds": 5.2,
  "estimated_completion": "2025-11-17T10:30:15Z"
}
```

**Response (200 OK) - Completed:**
```json
{
  "batch_id": 123,
  "operation_type": "Atualização de Pedidos",
  "status": "completed",
  "status_display": "Concluído",
  "progress": {
    "total": 100,
    "completed": 98,
    "failed": 2,
    "percentage": 100.0,
    "success_rate": 98.0
  },
  "created_at": "2025-11-17T10:30:00Z",
  "started_at": "2025-11-17T10:30:05Z",
  "completed_at": "2025-11-17T10:30:15Z",
  "duration_seconds": 10.5,
  "results": {
    "0": {"id": 1, "status": "completed"},
    "1": {"id": 2, "status": "completed"}
  },
  "errors": {
    "5": {"code": "VALIDATION_ERROR", "message": "Order not found"}
  }
}
```

---

### 3.3 Cancel Async Batch Operation

Cancel a pending or processing async batch operation.

**Endpoint:** `POST /api/v1/admin/async/cancel/{batch_id}/`

**Permissions:** Admin or batch owner

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Batch operation canceled",
  "batch_id": 123,
  "completed_operations": 45,
  "canceled_operations": 55
}
```

**Note:** Already completed operations cannot be rolled back.

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": {
    "code": "INVALID_PARAMETERS",
    "message": "Invalid request parameters",
    "details": {
      "field": "order_ids",
      "issue": "must be a non-empty list"
    }
  }
}
```

### 403 Forbidden
```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "Admin permissions required"
  }
}
```

### 404 Not Found
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Batch operation 123 not found"
  }
}
```

### 500 Internal Server Error
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred"
  }
}
```

---

## Usage Examples

### Example 1: Bulk Approve Professionals

```bash
curl -X POST http://localhost:8000/api/v1/admin/bulk/professionals/approve/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "user_ids": [2, 3, 4, 5, 6],
    "is_verified": true,
    "is_premium": false
  }'
```

### Example 2: Export Orders as CSV

```bash
curl -X GET "http://localhost:8000/api/v1/admin/export/orders/?format=csv&status=completed&limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o orders_export.csv
```

### Example 3: Async Batch with Status Polling

```python
import requests
import time

# Submit batch
response = requests.post(
    'http://localhost:8000/api/v1/admin/async/submit/',
    json={
        'operation_type': 'order_update',
        'operations': [
            {'resource_id': i, 'data': {'status': 'completed'}}
            for i in range(1, 101)
        ],
        'notify_on_completion': True
    },
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

batch_id = response.json()['batch_id']
print(f"Batch {batch_id} submitted")

# Poll for status
while True:
    status_response = requests.get(
        f'http://localhost:8000/api/v1/admin/async/status/{batch_id}/',
        headers={'Authorization': 'Bearer YOUR_TOKEN'}
    )
    
    status_data = status_response.json()
    progress = status_data['progress']
    
    print(f"Progress: {progress['percentage']}% ({progress['completed']}/{progress['total']})")
    
    if status_data['status'] in ['completed', 'failed', 'partial']:
        print(f"Batch completed with {progress['success_rate']}% success rate")
        break
    
    time.sleep(2)
```

---

## Best Practices

1. **Batch Size**: Keep batch sizes reasonable (< 100 for sync, < 1000 for async)
2. **Error Handling**: Always check individual operation results for failures
3. **Pagination**: Use pagination for large exports to avoid timeouts
4. **Async for Large Operations**: Use async API for operations with > 50 items
5. **Status Polling**: Poll async status every 2-5 seconds, not more frequently
6. **CSV for Reports**: Use CSV format for data analysis and reporting
7. **JSON for Integration**: Use JSON format for programmatic integration

---

## Rate Limiting

Admin bulk operations are subject to rate limiting:
- **Sync Operations**: 100 requests per hour
- **Async Operations**: 50 requests per hour
- **Export Operations**: 20 requests per hour

Exceeded limits will return `429 Too Many Requests`.

---

## Support

For issues or questions about the Admin Bulk Operations API, contact the development team or refer to the main API documentation.

**Last Updated:** November 17, 2025
**API Version:** 1.0
