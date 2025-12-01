# WebSocket Security Configuration

## Overview

This document describes the comprehensive security configuration for the Chat IA Assistente (Sophie) WebSocket connections. The security implementation addresses **Requirement 8.3** from the design document.

## Security Components

### 1. CORS Configuration (Requirement 8.3)

WebSocket connections are protected by strict CORS (Cross-Origin Resource Sharing) policies to prevent unauthorized access from malicious websites.

#### Configuration Location
- **File**: `home_services/settings.py`
- **Settings**: `ALLOWED_WEBSOCKET_ORIGINS`, `WEBSOCKET_CORS_ALLOWED_HEADERS`

#### Allowed Origins
```python
ALLOWED_WEBSOCKET_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    # Add production domains when deploying
]
```

#### Allowed Headers
The following headers are permitted in WebSocket upgrade requests:
- `authorization` - For authentication tokens
- `content-type` - Content type specification
- `x-csrftoken` - CSRF protection
- `x-requested-with` - AJAX request identification
- `sec-websocket-*` - WebSocket protocol headers
- `origin` - Origin header for CORS
- `host` - Host header

#### Implementation
- **Middleware**: `WebSocketSecurityMiddleware` in `services/chat/security.py`
- **Method**: `check_origin()` validates origin against allowed list
- **Enforcement**: Connections from unauthorized origins are rejected with code 4003

### 2. Message Size Limits (Requirement 8.3)

Message size limits prevent Denial of Service (DoS) attacks via large payloads.

#### Configuration
```python
WEBSOCKET_SECURITY = {
    'MAX_MESSAGE_SIZE': 2000,           # Characters in message content
    'MAX_FRAME_SIZE': 65536,            # Bytes in WebSocket frame (64KB)
    'MAX_FEEDBACK_LENGTH': 1000,        # Characters in feedback text
    'MAX_CONTEXT_SIZE_BYTES': 10000,    # Bytes in context data (10KB)
    'ENFORCE_MESSAGE_SIZE': True,       # Enable enforcement
}
```

#### Limits Enforced

| Type | Limit | Purpose |
|------|-------|---------|
| Message Content | 2000 characters | Prevent spam and abuse |
| WebSocket Frame | 64KB (65536 bytes) | Prevent memory exhaustion |
| Feedback Text | 1000 characters | Reasonable feedback length |
| Context Data | 10KB (10000 bytes) | Prevent DoS via large context |

#### Implementation
- **Validator**: `ChatSecurityValidator.validate_message_content()`
- **Middleware**: `WebSocketSecurityMiddleware` wraps `receive()` to check frame size
- **Consumer**: `ChatConsumer.handle_chat_message()` validates before processing

### 3. Input Validation Rules (Requirement 8.3)

Comprehensive input validation prevents injection attacks (XSS, SQL injection, etc.).

#### Validation Rules

##### Message Content Validation
```python
ChatSecurityValidator.validate_message_content(content)
```
- **Type Check**: Must be string
- **Length Check**: 1-2000 characters
- **Pattern Check**: Blocks dangerous patterns:
  - `<script>` tags
  - `javascript:` protocol
  - Event handlers (`onclick`, `onload`, etc.)
  - `<iframe>`, `<object>`, `<embed>` tags

##### Session ID Validation
```python
ChatSecurityValidator.validate_session_id(session_id)
```
- **Format**: Must be valid UUID (RFC 4122)
- **Pattern**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

##### Rating Validation
```python
ChatSecurityValidator.validate_rating(rating)
```
- **Type**: Must be integer
- **Range**: 1-5 (inclusive)

##### Feedback Validation
```python
ChatSecurityValidator.validate_feedback(feedback)
```
- **Type**: Must be string
- **Length**: 0-1000 characters
- **Pattern Check**: Blocks dangerous patterns

##### Context Data Validation
```python
ChatSecurityValidator.validate_context_data(context)
```
- **Type**: Must be dictionary
- **Size**: Maximum 10KB when serialized to JSON
- **Keys**: Must be alphanumeric strings with `_`, `-`, `.`
- **Structure**: Validated recursively up to 5 levels deep

##### JSON Message Validation
```python
ChatSecurityValidator.validate_json_message(text_data)
```
- **Format**: Must be valid JSON
- **Type**: Must be object (dictionary)
- **Required Fields**: Must contain `type` field

#### Dangerous Patterns Blocked

The following patterns are detected and blocked:

```python
DANGEROUS_PATTERNS = [
    r'<script[^>]*>.*?</script>',  # Script tags
    r'javascript:',                 # JavaScript protocol
    r'on\w+\s*=',                  # Event handlers
    r'<iframe[^>]*>',              # Iframes
    r'<object[^>]*>',              # Object tags
    r'<embed[^>]*>',               # Embed tags
]
```

### 4. Input Sanitization

All user inputs are sanitized to prevent XSS attacks.

#### Sanitization Methods

##### HTML Escaping
```python
ChatSecurityValidator.sanitize_message_content(content)
```
- Converts HTML special characters to entities
- Example: `<script>` → `&lt;script&gt;`

##### Context Data Sanitization
```python
ChatSecurityValidator.sanitize_context_data(context)
```
- Recursively sanitizes nested structures
- HTML escapes string values
- Preserves safe types (int, float, bool)
- Maximum recursion depth: 5 levels

### 5. Connection Limits

Prevent abuse by limiting concurrent connections.

#### Configuration
```python
WEBSOCKET_SECURITY = {
    'MAX_CONNECTIONS_PER_USER': 5,   # Per authenticated user
    'MAX_CONNECTIONS_PER_IP': 10,    # Per IP address
    'TRACK_CONNECTIONS': True,       # Enable tracking
}
```

#### Implementation
- **Tracker**: `ConnectionTracker` class in `services/chat/security.py`
- **Storage**: Redis cache (1 hour TTL)
- **Enforcement**: Connections exceeding limits are rejected with code 4008

### 6. Rate Limiting

Prevent spam by limiting message frequency.

#### Configuration
```python
CHAT_CONFIG = {
    'RATE_LIMIT_MESSAGES_PER_MINUTE': 10,
    'RATE_LIMIT_WINDOW_SECONDS': 60,
    'RATE_LIMIT_BURST_ALLOWANCE': 3,
}
```

#### Implementation
- **Method**: `ChatConsumer.check_rate_limit()`
- **Storage**: Redis cache with sliding window
- **Response**: Rate limit error with retry_after time

### 7. Timeout Settings

Prevent resource exhaustion from idle connections.

#### Configuration
```python
WEBSOCKET_SECURITY = {
    'CONNECTION_TIMEOUT': 300,    # 5 minutes
    'PING_INTERVAL': 30,          # 30 seconds
    'PING_TIMEOUT': 10,           # 10 seconds
    'IDLE_TIMEOUT': 600,          # 10 minutes
}
```

## Security Flow

### Connection Establishment

```
1. Client initiates WebSocket connection
   ↓
2. WebSocketSecurityMiddleware intercepts
   ↓
3. Origin validation (check_origin)
   ├─ Valid → Continue
   └─ Invalid → Reject (code 4003)
   ↓
4. Connection limit check
   ├─ Within limit → Continue
   └─ Exceeded → Reject (code 4008)
   ↓
5. Increment connection counter
   ↓
6. AuthMiddlewareStack authenticates user
   ↓
7. ChatConsumer.connect() accepts connection
   ↓
8. Send welcome message
```

### Message Processing

```
1. Client sends message
   ↓
2. WebSocketSecurityMiddleware checks frame size
   ├─ Within limit → Continue
   └─ Exceeded → Disconnect (code 4009)
   ↓
3. ChatConsumer.receive() parses JSON
   ↓
4. Rate limit check
   ├─ Within limit → Continue
   └─ Exceeded → Send rate_limit_error
   ↓
5. Validate message content
   ├─ Valid → Continue
   └─ Invalid → Send error message
   ↓
6. Sanitize input
   ↓
7. Process message
   ↓
8. Send response
```

### Disconnection

```
1. Connection closes
   ↓
2. ChatConsumer.disconnect() called
   ↓
3. Save analytics
   ↓
4. Leave channel group
   ↓
5. WebSocketSecurityMiddleware finally block
   ↓
6. Decrement connection counter
```

## Error Codes

Custom WebSocket close codes for security events:

| Code | Meaning | Trigger |
|------|---------|---------|
| 4003 | Unauthorized Origin | Origin not in allowed list |
| 4008 | Connection Limit Exceeded | Too many concurrent connections |
| 4009 | Message Too Large | Frame size exceeds limit |

## Logging

Security events are logged for monitoring and debugging.

### Log Levels

- **INFO**: Normal security events (connection accepted)
- **WARNING**: Validation failures, rate limits, rejected connections
- **ERROR**: Unexpected security errors

### Logged Events

```python
WEBSOCKET_SECURITY = {
    'LOG_SECURITY_EVENTS': True,           # Connection accepted/rejected
    'LOG_REJECTED_CONNECTIONS': True,      # Unauthorized origins, limits
    'LOG_VALIDATION_FAILURES': True,       # Invalid inputs
    'LOG_RATE_LIMIT_VIOLATIONS': True,     # Rate limit exceeded
    'LOG_SUSPICIOUS_ACTIVITY': True,       # Dangerous patterns detected
}
```

### Example Log Entries

```
WARNING: Rejected WebSocket connection from unauthorized origin
  origin: http://malicious-site.com
  path: /ws/chat/

WARNING: Dangerous pattern detected in message
  pattern: <script[^>]*>.*?</script>
  content_preview: <script>alert('xss')</script>

WARNING: Rate limit exceeded
  user_id: 123
  current_count: 11
  limit: 10
```

## Testing Security

### Manual Testing

#### Test CORS Protection
```bash
# Should be rejected
wscat -c ws://localhost:8000/ws/chat/ --origin http://malicious-site.com

# Should be accepted
wscat -c ws://localhost:8000/ws/chat/ --origin http://localhost:8000
```

#### Test Message Size Limits
```javascript
// Should be rejected (>2000 characters)
ws.send(JSON.stringify({
    type: 'message',
    content: 'A'.repeat(2001)
}));
```

#### Test Rate Limiting
```javascript
// Send 11 messages rapidly (should reject 11th)
for (let i = 0; i < 11; i++) {
    ws.send(JSON.stringify({
        type: 'message',
        content: `Message ${i}`
    }));
}
```

#### Test XSS Protection
```javascript
// Should be sanitized
ws.send(JSON.stringify({
    type: 'message',
    content: '<script>alert("xss")</script>'
}));
```

### Automated Testing

Security tests are located in:
- `services/chat/test_security.py`
- `services/chat/test_security_config.py`

Run tests:
```bash
python manage.py test services.chat.test_security
python manage.py test services.chat.test_security_config
```

## Production Deployment

### Checklist

- [ ] Update `ALLOWED_WEBSOCKET_ORIGINS` with production domains
- [ ] Set `WEBSOCKET_SECURITY['ALLOW_WILDCARD_ORIGIN']` to `False`
- [ ] Enable Redis for connection tracking and rate limiting
- [ ] Configure monitoring for security log events
- [ ] Set up alerts for:
  - High rate of rejected connections
  - Dangerous pattern detections
  - Rate limit violations
- [ ] Review and adjust limits based on usage patterns
- [ ] Enable HTTPS/WSS in production
- [ ] Configure firewall rules for WebSocket ports

### Environment Variables

```bash
# Redis (required for production)
USE_REDIS=true
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# WebSocket Security
WEBSOCKET_ENFORCE_ORIGIN=true
WEBSOCKET_MAX_CONNECTIONS_PER_USER=5
WEBSOCKET_MAX_CONNECTIONS_PER_IP=10

# Rate Limiting
CHAT_RATE_LIMIT=10
CHAT_RATE_LIMIT_WINDOW=60
```

## Security Best Practices

1. **Always validate input** - Never trust client data
2. **Sanitize output** - Escape HTML to prevent XSS
3. **Use HTTPS/WSS** - Encrypt connections in production
4. **Monitor logs** - Watch for suspicious activity
5. **Rate limit aggressively** - Prevent abuse
6. **Limit connection lifetime** - Close idle connections
7. **Validate origins strictly** - No wildcards in production
8. **Keep dependencies updated** - Security patches
9. **Test security regularly** - Automated security tests
10. **Document security decisions** - Maintain this document

## References

- **Design Document**: `.kiro/specs/chat-ia-assistente/design.md`
- **Requirements**: Requirement 8.3 (Security)
- **Implementation**: 
  - `services/chat/security.py` - Security validators and middleware
  - `services/chat/consumers.py` - Consumer with security checks
  - `home_services/settings.py` - Security configuration
  - `home_services/asgi.py` - ASGI application with security layers

## Support

For security concerns or questions:
1. Review this documentation
2. Check security test files
3. Review Django Channels security documentation
4. Consult the development team

---

**Last Updated**: Task 13.3 Implementation
**Status**: Complete
**Requirements Validated**: 8.3 (Configure CORS, Set message size limits, Add input validation rules)
