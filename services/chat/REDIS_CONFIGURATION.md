# Redis Configuration for Chat IA Assistente (Sophie)

## Overview

Redis is used as the backend for Django Channels and chat response caching. This document explains the Redis configuration and how to set it up.

## Requirements

- **Requirement 8.1**: Support 100+ concurrent chat sessions
- **Requirement 8.2**: Cache frequent responses to reduce API calls
- **Requirement 8.3**: Implement rate limiting to prevent abuse

## Redis Usage

Redis is used for three main purposes in the chat system:

### 1. Channel Layer (WebSocket Support)
- **Database**: Redis DB 0 (default)
- **Purpose**: Real-time message passing between WebSocket connections
- **Configuration**: `CHANNEL_LAYERS` in settings.py
- **Key Settings**:
  - `capacity`: 1500 messages per channel
  - `expiry`: 10 seconds for message expiry
  - `group_expiry`: 86400 seconds (24 hours) for channel groups

### 2. Chat Response Caching
- **Database**: Redis DB 2
- **Purpose**: Cache AI responses to reduce OpenAI API calls
- **Configuration**: `CACHES['chat']` in settings.py
- **Key Settings**:
  - `TIMEOUT`: 3600 seconds (1 hour)
  - `max_connections`: 30 connections in pool

### 3. General Application Cache
- **Database**: Redis DB 1
- **Purpose**: General application caching (services, user data, etc.)
- **Configuration**: `CACHES['default']` in settings.py

## Installation

### Install Redis Server

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS
```bash
brew install redis
brew services start redis
```

#### Windows
Download and install from: https://github.com/microsoftarchive/redis/releases

### Install Python Dependencies

The required Python packages are already in `requirements.txt`:
```
channels-redis>=4.0.0
redis>=4.5.0
django-redis>=5.2.0
```

Install with:
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Set these in your `.env` file:

```bash
# Enable Redis
USE_REDIS=true

# Redis connection
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0

# Optional: Channel layer tuning
CHANNEL_CAPACITY=1500
CHANNEL_EXPIRY=10
CHANNEL_GROUP_EXPIRY=86400
```

### Development vs Production

#### Development (without Redis)
Set `USE_REDIS=false` in `.env`. The system will use:
- `InMemoryChannelLayer` for WebSocket support
- `LocMemCache` for caching

**Note**: In-memory backends are NOT suitable for production and do NOT support multiple server instances.

#### Production (with Redis)
Set `USE_REDIS=true` in `.env`. The system will use:
- `RedisChannelLayer` for WebSocket support
- `RedisCache` for caching

## Testing Redis Connection

### Test Redis Server
```bash
redis-cli ping
# Should return: PONG
```

### Test from Python
```python
import redis

# Test connection
r = redis.Redis(host='127.0.0.1', port=6379, db=0)
r.ping()  # Should return True

# Test set/get
r.set('test_key', 'test_value')
print(r.get('test_key'))  # Should return b'test_value'
```

### Test Django Channels
```bash
python manage.py shell
```

```python
from channels.layers import get_channel_layer
import asyncio

channel_layer = get_channel_layer()

# Test send/receive
async def test_channels():
    await channel_layer.send('test_channel', {'type': 'test.message', 'text': 'Hello'})
    message = await channel_layer.receive('test_channel')
    print(message)

asyncio.run(test_channels())
```

## Performance Tuning

### Channel Layer Settings

- **capacity**: Maximum messages per channel before blocking
  - Default: 1500
  - Increase for high-traffic scenarios
  - Decrease to save memory

- **expiry**: How long messages stay in channel
  - Default: 10 seconds
  - Increase if messages are being dropped
  - Decrease to save memory

- **group_expiry**: How long channel groups persist
  - Default: 86400 seconds (24 hours)
  - Matches chat session timeout
  - Increase for longer session persistence

### Connection Pool Settings

- **max_connections**: Maximum Redis connections
  - Channel Layer: 100 connections
  - Chat Cache: 30 connections
  - Default Cache: 50 connections
  - Adjust based on concurrent user load

### Cache Settings

- **TIMEOUT**: How long cached responses persist
  - Chat responses: 3600 seconds (1 hour)
  - Adjust based on content freshness requirements

## Monitoring

### Redis Memory Usage
```bash
redis-cli info memory
```

### Active Connections
```bash
redis-cli client list
```

### Key Statistics
```bash
redis-cli info stats
```

### Monitor Real-time Commands
```bash
redis-cli monitor
```

## Troubleshooting

### Connection Refused
- Check if Redis server is running: `sudo systemctl status redis-server`
- Check Redis port: `netstat -an | grep 6379`
- Check firewall settings

### High Memory Usage
- Check key expiration settings
- Monitor cache hit rates
- Consider increasing Redis memory limit in `redis.conf`

### Slow Performance
- Check Redis latency: `redis-cli --latency`
- Monitor connection pool exhaustion
- Consider Redis persistence settings (RDB vs AOF)

### WebSocket Connection Issues
- Verify `CHANNEL_LAYERS` configuration
- Check Redis connection from Django shell
- Review Django Channels logs

## Security Considerations

1. **Network Security**
   - Bind Redis to localhost in development
   - Use firewall rules in production
   - Consider Redis AUTH password

2. **Encryption**
   - Channel messages are encrypted using Django SECRET_KEY
   - Consider TLS for Redis connections in production

3. **Resource Limits**
   - Set `maxmemory` in redis.conf
   - Configure eviction policy (e.g., `allkeys-lru`)

## Production Deployment

### Redis Configuration (`redis.conf`)
```conf
# Bind to localhost only (or specific IPs)
bind 127.0.0.1

# Set password (recommended)
requirepass your_strong_password_here

# Set memory limit
maxmemory 256mb
maxmemory-policy allkeys-lru

# Enable persistence (optional)
save 900 1
save 300 10
save 60 10000

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log
```

### Django Settings for Production
```python
# Use environment variables for sensitive data
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')

# Update connection string with password
REDIS_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}'
```

## References

- [Django Channels Documentation](https://channels.readthedocs.io/)
- [channels-redis Documentation](https://github.com/django/channels_redis)
- [Redis Documentation](https://redis.io/documentation)
- [django-redis Documentation](https://github.com/jazzband/django-redis)
