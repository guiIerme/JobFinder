# Redis Quick Start Guide for Chat IA Assistente

## Quick Setup (Development)

### Option 1: Without Redis (In-Memory - Default)

No setup required! The system uses in-memory backends by default.

**Limitations**:
- Does not persist across server restarts
- Cannot handle multiple server instances
- Limited scalability
- Not suitable for production

### Option 2: With Redis (Recommended for Production)

#### Step 1: Install Redis

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Windows:**
Download from: https://github.com/microsoftarchive/redis/releases

#### Step 2: Verify Redis is Running

```bash
redis-cli ping
# Should return: PONG
```

#### Step 3: Enable Redis in Django

Edit your `.env` file:
```bash
USE_REDIS=true
```

#### Step 4: Test Configuration

```bash
python test_redis_config.py
```

You should see all tests pass with Redis connection successful.

## What Gets Configured

When `USE_REDIS=true`, the following are configured:

### 1. Channel Layers (WebSocket Support)
- **Purpose**: Real-time message passing for chat
- **Redis DB**: 0 (default)
- **Capacity**: 1500 messages per channel
- **Expiry**: 10 seconds
- **Group Expiry**: 24 hours

### 2. Chat Response Cache
- **Purpose**: Cache AI responses to reduce API calls
- **Redis DB**: 2
- **TTL**: 1 hour (3600 seconds)
- **Key Prefix**: `chat:`

### 3. General Application Cache
- **Purpose**: Cache services, user data, etc.
- **Redis DB**: 1
- **TTL**: 15 minutes (900 seconds)
- **Key Prefix**: `homeservices:`

## Environment Variables

All Redis settings can be customized via environment variables:

```bash
# Basic Redis connection
USE_REDIS=true
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0

# Channel layer tuning (optional)
CHANNEL_CAPACITY=1500
CHANNEL_EXPIRY=10
CHANNEL_GROUP_EXPIRY=86400
```

## Troubleshooting

### "Connection refused" error

**Problem**: Redis server is not running

**Solution**:
```bash
# Check if Redis is running
sudo systemctl status redis-server

# Start Redis
sudo systemctl start redis-server
```

### "No module named 'redis'" error

**Problem**: Redis Python package not installed

**Solution**:
```bash
pip install -r requirements.txt
```

### Chat not working in production

**Problem**: Using in-memory backends with multiple servers

**Solution**: Set `USE_REDIS=true` in production environment

## Performance Tips

1. **Monitor Redis Memory**: Use `redis-cli info memory`
2. **Check Connection Pool**: Ensure max_connections is adequate
3. **Cache Hit Rate**: Monitor cache effectiveness
4. **Key Expiration**: Verify keys are expiring properly

## Next Steps

After Redis is configured:

1. ✓ Redis is installed and running
2. ✓ `USE_REDIS=true` in `.env`
3. ✓ Run `python test_redis_config.py` - all tests pass
4. → Continue with chat implementation tasks
5. → Deploy to production with Redis

## Need Help?

- See `REDIS_CONFIGURATION.md` for detailed documentation
- Check Django Channels docs: https://channels.readthedocs.io/
- Redis documentation: https://redis.io/documentation
