# Mobile-Optimized API Documentation

## Overview

The mobile-optimized API endpoints provide streamlined, bandwidth-efficient access to services, professionals, and orders data. These endpoints are specifically designed for mobile applications with features like:

- **Compact responses** with reduced field sets
- **Dynamic field selection** to request only needed data
- **Automatic image optimization** based on device type
- **Device detection** via User-Agent headers
- **Lazy loading hints** for mobile devices

## Base URL

```
/api/v1/mobile/
```

## Endpoints

### 1. Mobile Services

**Endpoint:** `GET /api/v1/mobile/services/`

**Description:** Retrieve a list of services with mobile-optimized responses.

**Default Fields:**
- `id` - Service ID
- `name` - Service name
- `category` - Category code
- `category_display` - Human-readable category
- `estimated_price` - Price estimate
- `provider` - Provider user ID
- `provider_name` - Provider's name
- `is_active` - Active status

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `category` | string | Filter by category | `?category=plumbing` |
| `is_active` | boolean | Filter by active status | `?is_active=true` |
| `provider` | integer | Filter by provider ID | `?provider=5` |
| `ordering` | string | Sort results | `?ordering=-created_at` |
| `fields` | string | Select specific fields | `?fields=id,name,estimated_price` |
| `compact` | boolean | Use minimal field set | `?compact=true` |
| `page` | integer | Page number | `?page=2` |
| `page_size` | integer | Items per page (10-100) | `?page_size=20` |

**Compact Mode Fields:**
- `id`
- `name`
- `estimated_price`

**Example Requests:**

```bash
# Basic request
GET /api/v1/mobile/services/

# Compact mode (minimal data)
GET /api/v1/mobile/services/?compact=true

# Select specific fields
GET /api/v1/mobile/services/?fields=id,name,estimated_price,category_display

# Filter and sort
GET /api/v1/mobile/services/?category=cleaning&ordering=-estimated_price
```

**Example Response:**

```json
{
  "count": 45,
  "next": "http://localhost:8000/api/v1/mobile/services/?page=2",
  "previous": null,
  "total_pages": 3,
  "current_page": 1,
  "results": [
    {
      "id": 1,
      "name": "House Cleaning",
      "category": "cleaning",
      "category_display": "Limpeza",
      "estimated_price": "150.00",
      "provider": 5,
      "provider_name": "John Doe",
      "is_active": true
    }
  ]
}
```

---

### 2. Mobile Professionals

**Endpoint:** `GET /api/v1/mobile/professionals/`

**Description:** Retrieve a list of professionals with mobile-optimized responses.

**Default Fields:**
- `id` - Profile ID
- `username` - Username
- `full_name` - Full name
- `phone` - Phone number
- `city` - City
- `state` - State
- `rating` - Average rating
- `review_count` - Number of reviews
- `is_verified` - Verification status
- `is_available` - Availability status
- `avatar` - Optimized avatar URL

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `city` | string | Filter by city | `?city=São Paulo` |
| `state` | string | Filter by state | `?state=SP` |
| `is_available` | boolean | Filter by availability | `?is_available=true` |
| `is_verified` | boolean | Filter by verification | `?is_verified=true` |
| `ordering` | string | Sort results | `?ordering=-rating` |
| `fields` | string | Select specific fields | `?fields=id,full_name,rating` |
| `compact` | boolean | Use minimal field set | `?compact=true` |
| `page` | integer | Page number | `?page=2` |
| `page_size` | integer | Items per page (10-100) | `?page_size=20` |

**Compact Mode Fields:**
- `id`
- `full_name`
- `rating`
- `city`

**Image Optimization:**

Avatar images are automatically optimized based on the device type detected from the User-Agent header:

- **Mobile:** 150x150px
- **Tablet:** 200x200px
- **Desktop:** 300x300px

The optimized URL includes query parameters that can be used by CDN or image proxy services:
```
/media/avatars/user.jpg?w=150&h=150&fit=cover
```

**Example Requests:**

```bash
# Basic request
GET /api/v1/mobile/professionals/

# Compact mode
GET /api/v1/mobile/professionals/?compact=true

# Filter by location and availability
GET /api/v1/mobile/professionals/?city=Rio&is_available=true

# Select specific fields
GET /api/v1/mobile/professionals/?fields=id,full_name,rating,phone
```

**Example Response:**

```json
{
  "count": 28,
  "next": null,
  "previous": null,
  "total_pages": 1,
  "current_page": 1,
  "results": [
    {
      "id": 5,
      "username": "johndoe",
      "full_name": "John Doe",
      "phone": "+55 11 98765-4321",
      "city": "São Paulo",
      "state": "SP",
      "rating": "4.85",
      "review_count": 42,
      "is_verified": true,
      "is_available": true,
      "avatar": "/media/avatars/johndoe.jpg?w=150&h=150&fit=cover"
    }
  ]
}
```

---

### 3. Mobile Orders

**Endpoint:** `GET /api/v1/mobile/orders/`

**Description:** Retrieve user's orders with mobile-optimized responses.

**Authentication:** Required (users see only their own orders)

**Default Fields:**
- `id` - Order ID
- `service_name` - Service name
- `estimated_price` - Price estimate
- `provider` - Provider user ID
- `provider_name` - Provider's name
- `status` - Status code
- `status_display` - Human-readable status
- `preferred_date` - Preferred service date
- `created_at` - Creation timestamp

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `status` | string | Filter by status | `?status=pending` |
| `ordering` | string | Sort results | `?ordering=-created_at` |
| `fields` | string | Select specific fields | `?fields=id,service_name,status` |
| `compact` | boolean | Use minimal field set | `?compact=true` |
| `page` | integer | Page number | `?page=2` |
| `page_size` | integer | Items per page (10-100) | `?page_size=20` |

**Compact Mode Fields:**
- `id`
- `service_name`
- `status`
- `created_at`

**Status Values:**
- `pending` - Pendente
- `contacted` - Contatado
- `scheduled` - Agendado
- `completed` - Concluído
- `cancelled` - Cancelado

**Example Requests:**

```bash
# Basic request (requires authentication)
GET /api/v1/mobile/orders/
Authorization: Token <your-token>

# Compact mode
GET /api/v1/mobile/orders/?compact=true
Authorization: Token <your-token>

# Filter by status
GET /api/v1/mobile/orders/?status=pending
Authorization: Token <your-token>

# Select specific fields
GET /api/v1/mobile/orders/?fields=id,service_name,status,created_at
Authorization: Token <your-token>
```

**Example Response:**

```json
{
  "count": 12,
  "next": null,
  "previous": null,
  "total_pages": 1,
  "current_page": 1,
  "results": [
    {
      "id": 23,
      "service_name": "House Cleaning",
      "estimated_price": "150.00",
      "provider": 5,
      "provider_name": "John Doe",
      "status": "scheduled",
      "status_display": "Agendado",
      "preferred_date": "2025-11-20",
      "created_at": "2025-11-17T10:30:00Z"
    }
  ]
}
```

---

## Response Headers

All mobile API responses include the following headers:

| Header | Description | Example |
|--------|-------------|---------|
| `X-Device-Type` | Detected device type | `mobile`, `tablet`, or `desktop` |
| `X-Image-Lazy-Load` | Lazy loading recommendation | `recommended` (for mobile/tablet) |
| `X-Optimization-Hint` | Optimization suggestion | `Use ?compact=true for minimal payload` |

---

## Device Detection

The API automatically detects device type from the `User-Agent` header:

**Mobile Devices:**
- iPhone, Android phones
- Windows Phone, BlackBerry
- Opera Mini, Mobile browsers

**Tablet Devices:**
- iPad, Android tablets
- Kindle, PlayBook

**Desktop:**
- All other devices

---

## Field Selection

### Using `?fields=` Parameter

Request only the fields you need to minimize data transfer:

```bash
# Request only ID and name
GET /api/v1/mobile/services/?fields=id,name

# Request multiple specific fields
GET /api/v1/mobile/professionals/?fields=id,full_name,rating,city,phone
```

**Benefits:**
- Reduced payload size
- Faster response times
- Lower bandwidth usage
- Optimized database queries

### Using `?compact=true` Parameter

Get a predefined minimal set of fields:

```bash
# Compact services (id, name, estimated_price)
GET /api/v1/mobile/services/?compact=true

# Compact professionals (id, full_name, rating, city)
GET /api/v1/mobile/professionals/?compact=true

# Compact orders (id, service_name, status, created_at)
GET /api/v1/mobile/orders/?compact=true
```

**Benefits:**
- Smallest possible payload
- Minified JSON response
- Optimal for slow connections
- Reduced battery usage

---

## Image Optimization

### Automatic Optimization

Images (like avatars) are automatically optimized based on device type:

```json
{
  "avatar": "/media/avatars/user.jpg?w=150&h=150&fit=cover"
}
```

### Size Configurations

| Device | Avatar | Thumbnail | Medium | Large |
|--------|--------|-----------|--------|-------|
| Mobile | 150x150 | 300x300 | 600x600 | 1024x1024 |
| Tablet | 200x200 | 400x400 | 800x800 | 1280x1280 |
| Desktop | 300x300 | 600x600 | 1200x1200 | 1920x1920 |

### Lazy Loading

For mobile and tablet devices, the API recommends lazy loading via the `X-Image-Lazy-Load` header:

```http
X-Image-Lazy-Load: recommended
```

Implement lazy loading in your mobile app to:
- Load images only when needed
- Reduce initial page load time
- Save bandwidth and battery

---

## Performance Tips

### 1. Use Compact Mode for Lists

When displaying lists of items, use compact mode:

```bash
GET /api/v1/mobile/services/?compact=true
```

### 2. Select Only Needed Fields

Request only the fields you'll display:

```bash
GET /api/v1/mobile/professionals/?fields=id,full_name,rating,avatar
```

### 3. Implement Pagination

Use appropriate page sizes for your UI:

```bash
# Mobile: smaller pages for faster loading
GET /api/v1/mobile/services/?page_size=10

# Tablet: medium pages
GET /api/v1/mobile/services/?page_size=20
```

### 4. Cache Responses

Cache API responses in your mobile app to:
- Reduce network requests
- Improve offline experience
- Save battery life

### 5. Implement Lazy Loading

Load images and additional data only when needed:
- Use intersection observers
- Load on scroll
- Defer non-critical data

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Invalid field name in fields parameter",
    "details": {
      "invalid_fields": ["invalid_field_name"]
    }
  }
}
```

**Common Error Codes:**
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

---

## Rate Limiting

Mobile endpoints follow the same rate limiting as standard API endpoints:

- **Anonymous users:** 100 requests/hour
- **Authenticated users:** 1000 requests/hour

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1700236800
```

---

## Examples

### Complete Mobile App Integration

```javascript
// Mobile app service class
class MobileAPIService {
  constructor(baseURL, authToken) {
    this.baseURL = baseURL;
    this.authToken = authToken;
    this.deviceType = this.detectDevice();
  }
  
  detectDevice() {
    const ua = navigator.userAgent;
    if (/iPad|Android.*Tablet/.test(ua)) return 'tablet';
    if (/iPhone|Android|Mobile/.test(ua)) return 'mobile';
    return 'desktop';
  }
  
  async getServices(options = {}) {
    const params = new URLSearchParams({
      compact: 'true',  // Use compact mode for mobile
      page_size: this.deviceType === 'mobile' ? '10' : '20',
      ...options
    });
    
    const response = await fetch(
      `${this.baseURL}/mobile/services/?${params}`,
      {
        headers: {
          'Authorization': `Token ${this.authToken}`
        }
      }
    );
    
    return response.json();
  }
  
  async getProfessionals(filters = {}) {
    const params = new URLSearchParams({
      fields: 'id,full_name,rating,city,avatar',  // Only needed fields
      ...filters
    });
    
    const response = await fetch(
      `${this.baseURL}/mobile/professionals/?${params}`,
      {
        headers: {
          'Authorization': `Token ${this.authToken}`
        }
      }
    );
    
    return response.json();
  }
  
  async getMyOrders(status = null) {
    const params = new URLSearchParams({
      compact: 'true',
      ordering: '-created_at'
    });
    
    if (status) {
      params.append('status', status);
    }
    
    const response = await fetch(
      `${this.baseURL}/mobile/orders/?${params}`,
      {
        headers: {
          'Authorization': `Token ${this.authToken}`
        }
      }
    );
    
    return response.json();
  }
}

// Usage
const api = new MobileAPIService('http://localhost:8000/api/v1', 'your-token');

// Get services in compact mode
const services = await api.getServices({ category: 'cleaning' });

// Get professionals with specific fields
const professionals = await api.getProfessionals({ 
  city: 'São Paulo',
  is_available: 'true'
});

// Get user's orders
const orders = await api.getMyOrders('pending');
```

---

## Testing

Use the provided test script to verify the mobile API:

```bash
python test_mobile_api.py
```

This will test:
- Basic endpoint functionality
- Compact mode
- Field selection
- Device detection
- Response headers

---

## Support

For issues or questions about the mobile API:
1. Check this documentation
2. Review the test script examples
3. Check API response headers for hints
4. Contact the development team

---

## Changelog

### Version 1.0 (2025-11-17)
- Initial release of mobile-optimized endpoints
- Support for dynamic field selection
- Automatic image optimization
- Device detection and optimization hints
- Compact mode for minimal payloads
