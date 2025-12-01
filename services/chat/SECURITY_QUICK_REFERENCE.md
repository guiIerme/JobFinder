# WebSocket Security Quick Reference

## Task 13.3 Implementation Summary

This document provides a quick reference for the security configurations implemented in Task 13.3.

## ✅ Requirements Validated

- **8.3.1** - Configure CORS for WebSocket connections ✓
- **8.3.2** - Set message size limits ✓
- **8.3.3** - Add input validation rules ✓

## Configuration Files

| File | Purpose |
|------|---------|
| `home_services/settings.py` | Main security configuration |
| `services/chat/security.py` | Security validators and middleware |
| `services/chat/consumers.py` | Consumer with security checks |
| `home_services/asgi.py` | ASGI application with security layers |

## Quick Configuration Reference

### CORS Settings
```python
# In settings.py
ALLOWED_WEBSOCKET_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
    # Add production domains
]

WEBSOCKET_CORS_ALLOWED_HEADERS = [
    'authorization', 'content-type', 'origin', ...
]
```

### Message Size Limits
```python
# In settings.py
WEBSOCKET_SECURITY = {
    'MAX_MESSAGE_SIZE': 2000,        # Characters
    'MAX_FRAME_SIZE': 65536,         # Bytes (64KB)
    'MAX_FEEDBACK_LENGTH': 1000,     # Characters
    'MAX_CONTEXT_SIZE_BYTES': 10000, # Bytes (10KB)
}
```

### Input Validation
```python
# In settings.py
WEBSOCKET_SECURITY = {
    'VALIDATE_JSON': True,
    'VALIDATE_MESSAGE_TYPE': True,
    'VALIDATE_CONTENT': True,
    'BLOCK_DANGEROUS_PATTERNS': True,
    'SANITIZE_INPUT': True,
}
```

## Security Validators

### Message Content
```python
from services.chat.security import ChatSecurityValidator

# Validate
is_valid, error = ChatSecurityValidator.validate_message_content(content)

# Sanitize
sanitized = ChatSecurityValidator.sanitize_message_content(content)
```

### Session ID
```python
is_valid, error = ChatSecurityValidator.validate_session_id(session_id)
```

### Rating
```python
is_valid, error, normalized = ChatSecurityValidator.validate_rating(rating)
```

### Context Data
```python
is_valid, error = ChatSecurityValidator.validate_context_data(context)
```

## Security Middleware

The `WebSocketSecurityMiddleware` is automatically applied in `asgi.py`:

```python
websocket_app = AllowedHostsOriginValidator(
    WebSocketSecurityMiddleware(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    )
)
```

## Connection Limits

```python
from services.chat.security import ConnectionTracker

# Check limits
is_allowed, reason = ConnectionTracker.check_connection_limit(
    user_id=user_id,
    ip_address=ip_address
)

# Track connections
ConnectionTracker.increment_connection(user_id, ip_address)
ConnectionTracker.decrement_connection(user_id, ip_address)
```

## Error Codes

| Code | Meaning |
|------|---------|
| 4003 | Unauthorized Origin |
| 4008 | Connection Limit Exceeded |
| 4009 | Message Too Large |

## Testing

Run security tests:
```bash
python manage.py test services.chat.test_security_config
```

All 24 tests should pass:
- ✓ CORS configuration
- ✓ Message size limits
- ✓ Input validation
- ✓ Connection limits
- ✓ Rate limiting
- ✓ Origin checking
- ✓ Pattern matching

## Common Tasks

### Add Production Domain
```python
# In settings.py
ALLOWED_WEBSOCKET_ORIGINS = [
    "http://localhost:8000",
    "https://yourdomain.com",      # Add this
    "wss://yourdomain.com",        # Add this
]
```

### Adjust Message Limits
```python
# In settings.py
WEBSOCKET_SECURITY = {
    'MAX_MESSAGE_SIZE': 3000,  # Increase from 2000
}
```

### Enable/Disable Validation
```python
# In settings.py
WEBSOCKET_SECURITY = {
    'VALIDATE_CONTENT': False,  # Disable (not recommended)
}
```

## Security Checklist for Production

- [ ] Update `ALLOWED_WEBSOCKET_ORIGINS` with production domains
- [ ] Set `ALLOW_WILDCARD_ORIGIN` to `False`
- [ ] Enable Redis for connection tracking
- [ ] Configure HTTPS/WSS
- [ ] Set up monitoring for security events
- [ ] Review and test all security configurations
- [ ] Enable security logging
- [ ] Configure alerts for suspicious activity

## Monitoring

Security events are logged with these prefixes:
- `WARNING: Rejected WebSocket connection` - Unauthorized origin
- `WARNING: Dangerous pattern detected` - XSS attempt
- `WARNING: Rate limit exceeded` - Spam attempt
- `WARNING: Message frame size exceeded` - DoS attempt

## Support

For detailed documentation, see:
- `services/chat/SECURITY_CONFIGURATION.md` - Complete documentation
- `services/chat/test_security_config.py` - Test examples
- `.kiro/specs/chat-ia-assistente/design.md` - Design requirements

---

**Task**: 13.3 Add security configurations
**Status**: ✅ Complete
**Requirements**: 8.3 (Configure CORS, Set message size limits, Add input validation rules)
**Tests**: 24/24 passing
