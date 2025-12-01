# Chat IA Assistente (Sophie) - Configuration Guide

This document describes the configuration options for the Chat IA Assistente system.

## Overview

The chat system configuration is defined in `home_services/settings.py` under the `CHAT_CONFIG` dictionary. All settings can be overridden using environment variables for flexibility across different environments (development, staging, production).

## Required Configuration

### OpenAI API Key

The only **required** configuration is the OpenAI API key:

```bash
# In your .env file
OPENAI_API_KEY=your_openai_api_key_here
```

Without this key, the chat system will fall back to predefined responses only.

## Optional Configuration

All other settings have sensible defaults and can be customized via environment variables:

### OpenAI Settings

```bash
# OpenAI model to use (default: gpt-4)
OPENAI_MODEL=gpt-4

# Temperature for response creativity (default: 0.7, range: 0.0-1.0)
OPENAI_TEMPERATURE=0.7

# Maximum tokens in AI response (default: 500)
OPENAI_MAX_TOKENS=500
```

### Session Management

```bash
# Maximum messages to keep in chat history (default: 50)
CHAT_MAX_HISTORY=50

# Session timeout in hours (default: 24)
CHAT_SESSION_TIMEOUT=24

# Cleanup interval for old sessions in hours (default: 6)
CHAT_CLEANUP_INTERVAL=6
```

### Rate Limiting (Requirement 8.3)

```bash
# Messages per minute per user (default: 10)
CHAT_RATE_LIMIT=10
```

**Default behavior:**
- 10 messages per minute per user
- 60-second sliding window
- 3 message burst allowance

### Caching (Requirement 8.2)

```bash
# Cache TTL in seconds (default: 3600 = 1 hour)
CHAT_CACHE_TTL=3600

# Enable response caching (default: true)
CHAT_CACHE_ENABLED=true
```

**Cache behavior:**
- Responses are cached using a hash of the message content
- Cache key prefix: `chat_response`
- Uses Redis when available, falls back to in-memory cache

### Performance (Requirement 8.4)

```bash
# Maximum concurrent chat sessions (default: 100)
CHAT_MAX_SESSIONS=100

# Response timeout in seconds (default: 30)
CHAT_TIMEOUT=30

# Connection timeout in seconds (default: 10)
CHAT_CONN_TIMEOUT=10

# Maximum retry attempts for failed requests (default: 3)
CHAT_MAX_RETRIES=3
```

### Features

```bash
# Enable chat analytics tracking (default: true)
CHAT_ANALYTICS=true

# Enable fallback responses when AI unavailable (default: true)
CHAT_FALLBACK=true

# Enable typing indicator (default: true)
CHAT_TYPING_INDICATOR=true
```

### Security

```bash
# Maximum message length in characters (default: 2000)
CHAT_MAX_MSG_LENGTH=2000

# Minimum message length in characters (default: 1)
CHAT_MIN_MSG_LENGTH=1
```

**Security features (always enabled):**
- Input sanitization
- Session validation
- Message type validation (text, system only)

### Logging

```bash
# Log level for chat operations (default: INFO)
CHAT_LOG_LEVEL=INFO

# Log all messages (default: true)
CHAT_LOG_MESSAGES=true

# Log AI responses (default: true)
CHAT_LOG_AI=true
```

## Redis Configuration

For production deployments, Redis is recommended for both WebSocket channel layers and response caching:

```bash
# Enable Redis (default: false for development)
USE_REDIS=true

# Redis connection settings
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0

# Optional: Channel layer settings
CHANNEL_CAPACITY=1500
CHANNEL_EXPIRY=10
CHANNEL_GROUP_EXPIRY=86400
```

## Configuration Access

In your code, access configuration via Django settings:

```python
from django.conf import settings

# Access chat configuration
api_key = settings.CHAT_CONFIG['OPENAI_API_KEY']
rate_limit = settings.CHAT_CONFIG['RATE_LIMIT_MESSAGES_PER_MINUTE']
cache_ttl = settings.CHAT_CONFIG['CACHE_TTL_SECONDS']

# Access cache configuration
cache_backend = settings.CHAT_CACHE_CONFIG['BACKEND']
```

## Environment-Specific Configuration

### Development

```bash
# Minimal configuration for development
OPENAI_API_KEY=your_key_here
USE_REDIS=false
CHAT_ANALYTICS=false
CHAT_LOG_LEVEL=DEBUG
```

### Production

```bash
# Recommended production configuration
OPENAI_API_KEY=your_production_key_here
USE_REDIS=true
REDIS_HOST=your_redis_host
CHAT_CACHE_ENABLED=true
CHAT_ANALYTICS=true
CHAT_MAX_SESSIONS=500
CHAT_LOG_LEVEL=INFO
```

## Monitoring

Key metrics to monitor (when `CHAT_ANALYTICS=true`):

- Active sessions count
- Average response time
- Cache hit rate
- Rate limit violations
- API error rate
- Message throughput

## Troubleshooting

### Chat not responding

1. Check OpenAI API key is set: `echo $OPENAI_API_KEY`
2. Verify Redis is running (if `USE_REDIS=true`): `redis-cli ping`
3. Check logs: `tail -f django.log`

### Slow responses

1. Verify cache is enabled: `CHAT_CACHE_ENABLED=true`
2. Check Redis connection if using Redis
3. Consider reducing `OPENAI_MAX_TOKENS`
4. Monitor concurrent sessions vs `CHAT_MAX_SESSIONS`

### Rate limiting issues

1. Adjust `CHAT_RATE_LIMIT` if needed
2. Check if burst allowance is sufficient
3. Review rate limit logs in analytics

## Requirements Mapping

This configuration satisfies the following requirements:

- **Requirement 8.2**: Caching configuration with TTL and Redis support
- **Requirement 8.3**: Rate limiting with configurable limits per minute
- **Requirement 8.4**: Performance settings including timeouts and concurrent session limits

## See Also

- [Chat System README](README.md)
- [Setup Guide](SETUP_COMPLETE.md)
- [Design Document](../../.kiro/specs/chat-ia-assistente/design.md)
