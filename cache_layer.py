"""Redis caching layer for performance optimization."""
import os
import json
import time
import hashlib
from typing import Any, Optional, Callable
from functools import wraps

# Try to import redis, fall back to in-memory cache
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# In-memory fallback cache
_MEMORY_CACHE = {}
_MEMORY_CACHE_EXPIRY = {}

REDIS_URL = os.getenv('REDIS_URL')  # e.g., redis://localhost:6379
CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
DEFAULT_TTL = int(os.getenv('CACHE_DEFAULT_TTL', '300'))  # 5 minutes


class CacheBackend:
    """Abstract cache backend supporting Redis or in-memory fallback."""
    
    def __init__(self):
        self.redis_client = None
        if REDIS_AVAILABLE and REDIS_URL:
            try:
                self.redis_client = redis.from_url(
                    REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                # Test connection
                self.redis_client.ping()
                print(f"✅ Redis connected: {REDIS_URL}")
            except Exception as e:
                print(f"⚠️  Redis connection failed, using in-memory cache: {e}")
                self.redis_client = None
        else:
            print("ℹ️  Redis not available, using in-memory cache")
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not CACHE_ENABLED:
            return None
        
        if self.redis_client:
            try:
                return self.redis_client.get(key)
            except Exception as e:
                print(f"⚠️  Redis GET error: {e}")
                return None
        else:
            # In-memory fallback
            if key in _MEMORY_CACHE_EXPIRY:
                if time.time() > _MEMORY_CACHE_EXPIRY[key]:
                    # Expired
                    del _MEMORY_CACHE[key]
                    del _MEMORY_CACHE_EXPIRY[key]
                    return None
            return _MEMORY_CACHE.get(key)
    
    def set(self, key: str, value: str, ttl: int = DEFAULT_TTL) -> bool:
        """Set value in cache with TTL."""
        if not CACHE_ENABLED:
            return False
        
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, value)
                return True
            except Exception as e:
                print(f"⚠️  Redis SET error: {e}")
                return False
        else:
            # In-memory fallback
            _MEMORY_CACHE[key] = value
            _MEMORY_CACHE_EXPIRY[key] = time.time() + ttl
            return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
                return True
            except Exception:
                return False
        else:
            _MEMORY_CACHE.pop(key, None)
            _MEMORY_CACHE_EXPIRY.pop(key, None)
            return True
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern (Redis only)."""
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            except Exception:
                return 0
        else:
            # Simple prefix match for in-memory
            count = 0
            pattern_prefix = pattern.replace('*', '')
            keys_to_delete = [k for k in _MEMORY_CACHE.keys() if k.startswith(pattern_prefix)]
            for key in keys_to_delete:
                _MEMORY_CACHE.pop(key, None)
                _MEMORY_CACHE_EXPIRY.pop(key, None)
                count += 1
            return count
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        if self.redis_client:
            try:
                info = self.redis_client.info('stats')
                return {
                    'backend': 'redis',
                    'connected': True,
                    'total_keys': self.redis_client.dbsize(),
                    'hits': info.get('keyspace_hits', 0),
                    'misses': info.get('keyspace_misses', 0),
                }
            except Exception:
                return {'backend': 'redis', 'connected': False}
        else:
            return {
                'backend': 'memory',
                'total_keys': len(_MEMORY_CACHE),
                'memory_size': len(str(_MEMORY_CACHE)),
            }


# Global cache instance
cache = CacheBackend()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: int = DEFAULT_TTL, key_prefix: str = ''):
    """Decorator to cache function results.
    
    Usage:
        @cached(ttl=300, key_prefix='analytics')
        def get_revenue_data(days=30):
            # expensive computation
            return data
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            func_key = f"{key_prefix}:{func.__name__}" if key_prefix else func.__name__
            arg_key = cache_key(*args, **kwargs)
            full_key = f"cache:{func_key}:{arg_key}"
            
            # Try to get from cache
            cached_value = cache.get(full_key)
            if cached_value is not None:
                try:
                    return json.loads(cached_value)
                except json.JSONDecodeError:
                    pass
            
            # Cache miss - compute value
            result = func(*args, **kwargs)
            
            # Store in cache
            try:
                cache.set(full_key, json.dumps(result, default=str), ttl=ttl)
            except Exception as e:
                print(f"⚠️  Cache SET failed for {full_key}: {e}")
            
            return result
        
        # Add cache control methods
        wrapper.clear_cache = lambda: cache.clear_pattern(f"cache:{key_prefix}:{func.__name__}:*")
        wrapper.cache_key_for = lambda *a, **kw: f"cache:{key_prefix}:{func.__name__}:{cache_key(*a, **kw)}"
        
        return wrapper
    return decorator


# Predefined cache strategies
def cache_ai_response(ttl: int = 3600):
    """Cache AI responses for 1 hour (saves API quota)."""
    return cached(ttl=ttl, key_prefix='ai')


def cache_analytics(ttl: int = 1800):
    """Cache analytics queries for 30 minutes."""
    return cached(ttl=ttl, key_prefix='analytics')


def cache_customer_data(ttl: int = 600):
    """Cache customer data for 10 minutes."""
    return cached(ttl=ttl, key_prefix='customer')


def invalidate_customer_cache(receipt: str):
    """Invalidate all caches for a specific customer."""
    cache.clear_pattern(f"cache:customer:*:{receipt}*")


def invalidate_all_analytics():
    """Clear all analytics caches (call after data changes)."""
    cache.clear_pattern("cache:analytics:*")
