# Admin Bulk API - Quick Start Guide

## 🚀 Quick Reference

### Authentication Required
All endpoints require admin authentication. Login first at `/login/`

---

## 📋 Bulk Operations

### Update Multiple Order Statuses
```bash
POST /api/v1/admin/bulk/orders/update-status/
{
  "order_ids": [1, 2, 3],
  "status": "completed"
}
```

### Approve Multiple Professionals
```bash
POST /api/v1/admin/bulk/professionals/approve/
{
  "user_ids": [2, 3, 4],
  "is_verified": true
}
```

### Activate/Deactivate Services
```bash
POST /api/v1/admin/bulk/services/update/
{
  "service_ids": [1, 2, 3],
  "is_active": true
}
```

---

## 📊 Data Export

### Export Orders (JSON)
```bash
GET /api/v1/admin/export/orders/?format=json&limit=100
```

### Export Orders (CSV)
```bash
GET /api/v1/admin/export/orders/?format=csv&status=completed
```

### Export Users
```bash
GET /api/v1/admin/export/users/?format=json&user_type=professional
```

### Export Services
```bash
GET /api/v1/admin/export/services/?format=csv&is_active=true
```

**Export Filters:**
- `format`: `json` or `csv`
- `limit`: Max records (default: 1000, max: 10000)
- `offset`: Pagination offset
- `status`: Filter by status
- `start_date`: From date (YYYY-MM-DD)
- `end_date`: Until date (YYYY-MM-DD)

---

## ⚡ Async Processing (for large batches)

### 1. Submit Batch
```bash
POST /api/v1/admin/async/submit/
{
  "operation_type": "order_update",
  "operations": [
    {"resource_id": 1, "data": {"status": "completed"}},
    {"resource_id": 2, "data": {"status": "completed"}}
  ],
  "notify_on_completion": true
}

Response: {"batch_id": 123, "status": "pending"}
```

### 2. Check Status
```bash
GET /api/v1/admin/async/status/123/

Response: {
  "status": "processing",
  "progress": {
    "percentage": 45.0,
    "completed": 45,
    "failed": 2,
    "total": 100
  }
}
```

### 3. Cancel (if needed)
```bash
POST /api/v1/admin/async/cancel/123/
```

---

## 💡 Common Use Cases

### Approve All Pending Professionals
```python
import requests

# Get all pending professionals (from your admin panel)
pending_ids = [2, 3, 4, 5, 6, 7, 8, 9, 10]

# Approve them all
response = requests.post(
    'http://localhost:8000/api/v1/admin/bulk/professionals/approve/',
    json={
        'user_ids': pending_ids,
        'is_verified': True
    }
)

print(f"Approved: {response.json()['updated_count']}")
```

### Export All Completed Orders This Month
```bash
curl "http://localhost:8000/api/v1/admin/export/orders/?format=csv&status=completed&start_date=2025-11-01" \
  -o november_orders.csv
```

### Bulk Update 100+ Orders Asynchronously
```python
import requests
import time

# Submit large batch
response = requests.post(
    'http://localhost:8000/api/v1/admin/async/submit/',
    json={
        'operation_type': 'order_update',
        'operations': [
            {'resource_id': i, 'data': {'status': 'completed'}}
            for i in range(1, 101)
        ]
    }
)

batch_id = response.json()['batch_id']

# Poll until complete
while True:
    status = requests.get(
        f'http://localhost:8000/api/v1/admin/async/status/{batch_id}/'
    ).json()
    
    print(f"Progress: {status['progress']['percentage']}%")
    
    if status['status'] in ['completed', 'failed']:
        break
    
    time.sleep(2)
```

---

## ⚠️ Important Notes

1. **Batch Limits:**
   - Sync operations: Up to 50 items
   - Async operations: Up to 1000 items
   - Exports: Up to 10,000 records per request

2. **Use Async for Large Batches:**
   - Use sync endpoints for < 50 items
   - Use async endpoints for 50+ items

3. **CSV vs JSON:**
   - Use CSV for reports and spreadsheets
   - Use JSON for programmatic integration

4. **Error Handling:**
   - Check individual results in response
   - Some operations may fail while others succeed

5. **Notifications:**
   - Async operations can send completion notifications
   - Check your notifications panel

---

## 🔗 Full Documentation

For complete API reference, see: `ADMIN_BULK_API_DOCUMENTATION.md`

For implementation details, see: `TASK_12_IMPLEMENTATION_SUMMARY.md`

---

## 🧪 Testing

Run the test suite:
```bash
python test_admin_bulk_api.py
```

---

**Need Help?** Check the full documentation or contact the development team.
