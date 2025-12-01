#!/usr/bin/env python
"""
Test script to verify Redis configuration for Chat IA Assistente.

This script checks:
1. Django settings load correctly
2. Channel layers configuration
3. Cache configuration
4. Redis connection (if USE_REDIS=true)
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

from django.conf import settings
from django.core.cache import caches
from channels.layers import get_channel_layer

def test_settings():
    """Test that settings are loaded correctly."""
    print("=" * 70)
    print("TESTING DJANGO SETTINGS")
    print("=" * 70)
    
    print(f"\n✓ Settings loaded successfully")
    print(f"  USE_REDIS: {settings.USE_REDIS}")
    print(f"  REDIS_HOST: {settings.REDIS_HOST}")
    print(f"  REDIS_PORT: {settings.REDIS_PORT}")
    print(f"  REDIS_DB: {settings.REDIS_DB}")
    
    return True

def test_channel_layers():
    """Test Channel Layers configuration."""
    print("\n" + "=" * 70)
    print("TESTING CHANNEL LAYERS CONFIGURATION")
    print("=" * 70)
    
    channel_layer = get_channel_layer()
    backend = settings.CHANNEL_LAYERS['default']['BACKEND']
    
    print(f"\n✓ Channel layer configured")
    print(f"  Backend: {backend}")
    
    if settings.USE_REDIS:
        config = settings.CHANNEL_LAYERS['default']['CONFIG']
        print(f"  Hosts: {config['hosts']}")
        print(f"  Capacity: {config['capacity']}")
        print(f"  Expiry: {config['expiry']} seconds")
        print(f"  Group Expiry: {config['group_expiry']} seconds")
        print(f"  Max Connections: {config['connection_pool_kwargs']['max_connections']}")
    else:
        print("  Using InMemoryChannelLayer (development mode)")
    
    return True

def test_cache_configuration():
    """Test cache configuration."""
    print("\n" + "=" * 70)
    print("TESTING CACHE CONFIGURATION")
    print("=" * 70)
    
    cache_names = list(settings.CACHES.keys())
    print(f"\n✓ Caches configured: {cache_names}")
    
    for cache_name in cache_names:
        cache_config = settings.CACHES[cache_name]
        print(f"\n  Cache: '{cache_name}'")
        print(f"    Backend: {cache_config['BACKEND']}")
        
        if settings.USE_REDIS and 'redis' in cache_config['BACKEND'].lower():
            print(f"    Location: {cache_config['LOCATION']}")
            print(f"    Key Prefix: {cache_config.get('KEY_PREFIX', 'N/A')}")
            print(f"    Timeout: {cache_config.get('TIMEOUT', 'N/A')} seconds")
        else:
            print(f"    Location: {cache_config.get('LOCATION', 'N/A')}")
            print(f"    Using in-memory cache (development mode)")
    
    return True

def test_redis_connection():
    """Test actual Redis connection if USE_REDIS is true."""
    if not settings.USE_REDIS:
        print("\n" + "=" * 70)
        print("SKIPPING REDIS CONNECTION TEST")
        print("=" * 70)
        print("\n  USE_REDIS is False - using in-memory backends")
        print("  Set USE_REDIS=true in .env to test Redis connection")
        return True
    
    print("\n" + "=" * 70)
    print("TESTING REDIS CONNECTION")
    print("=" * 70)
    
    try:
        import redis
        
        # Test Redis connection
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            socket_connect_timeout=5
        )
        
        # Ping Redis
        if r.ping():
            print("\n✓ Redis server is reachable")
            
            # Test set/get
            test_key = 'chat_config_test'
            test_value = 'test_value'
            r.set(test_key, test_value, ex=10)
            retrieved = r.get(test_key)
            
            if retrieved and retrieved.decode() == test_value:
                print("✓ Redis read/write operations work")
                r.delete(test_key)
            else:
                print("✗ Redis read/write test failed")
                return False
            
            # Get Redis info
            info = r.info()
            print(f"\n  Redis Version: {info['redis_version']}")
            print(f"  Connected Clients: {info['connected_clients']}")
            print(f"  Used Memory: {info['used_memory_human']}")
            print(f"  Total Keys: {r.dbsize()}")
            
            return True
        else:
            print("\n✗ Redis server did not respond to PING")
            return False
            
    except redis.ConnectionError as e:
        print(f"\n✗ Could not connect to Redis: {e}")
        print("\n  Make sure Redis server is running:")
        print("    - Ubuntu/Debian: sudo systemctl start redis-server")
        print("    - macOS: brew services start redis")
        print("    - Windows: Start Redis service")
        return False
    except ImportError:
        print("\n✗ redis package not installed")
        print("  Install with: pip install redis")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False

def test_chat_config():
    """Test chat-specific configuration."""
    print("\n" + "=" * 70)
    print("TESTING CHAT CONFIGURATION")
    print("=" * 70)
    
    chat_config = settings.CHAT_CONFIG
    
    print("\n✓ Chat configuration loaded")
    print(f"  OpenAI Model: {chat_config['OPENAI_MODEL']}")
    print(f"  Max History Messages: {chat_config['MAX_HISTORY_MESSAGES']}")
    print(f"  Session Timeout: {chat_config['SESSION_TIMEOUT_HOURS']} hours")
    print(f"  Rate Limit: {chat_config['RATE_LIMIT_MESSAGES_PER_MINUTE']} messages/minute")
    print(f"  Cache TTL: {chat_config['CACHE_TTL_SECONDS']} seconds")
    print(f"  Cache Enabled: {chat_config['CACHE_ENABLED']}")
    print(f"  Max Concurrent Sessions: {chat_config['MAX_CONCURRENT_SESSIONS']}")
    print(f"  Response Timeout: {chat_config['RESPONSE_TIMEOUT_SECONDS']} seconds")
    
    return True

def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("REDIS CONFIGURATION TEST FOR CHAT IA ASSISTENTE (SOPHIE)")
    print("=" * 70)
    
    tests = [
        ("Settings", test_settings),
        ("Channel Layers", test_channel_layers),
        ("Cache Configuration", test_cache_configuration),
        ("Chat Configuration", test_chat_config),
        ("Redis Connection", test_redis_connection),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        print("\nYour Redis configuration is ready for Chat IA Assistente.")
    else:
        print("\n✗ Some tests failed.")
        print("\nPlease review the errors above and fix the configuration.")
    
    print("\n" + "=" * 70)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
