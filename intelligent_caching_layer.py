"""
INTELLIGENT CACHING LAYER
=========================
High-performance caching system with Redis integration,
intelligent invalidation, and query optimization.

Features:
- Multi-tier caching (memory, Redis, database)
- Intelligent cache invalidation
- Query result caching
- Cache warming strategies
- Cache hit rate monitoring
- Distributed cache coordination
"""

import logging
import time
import hashlib
import json
import pickle
from typing import Any, Optional, Dict, List, Callable
from functools import wraps
from collections import OrderedDict
import threading

logger = logging.getLogger(__name__)


class LRUCache:
    """Thread-safe LRU (Least Recently Used) cache."""
    
    def __init__(self, capacity: int = 1000):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                self.hits += 1
                return self.cache[key]['value']
            self.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache."""
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.capacity:
                    # Remove oldest item
                    self.cache.popitem(last=False)
            
            self.cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl if ttl else None
            }
    
    def delete(self, key: str):
        """Delete key from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self):
        """Clear all cache."""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        with self.lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0
            
            return {
                'size': len(self.cache),
                'capacity': self.capacity,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate
            }
    
    def _cleanup_expired(self):
        """Remove expired entries."""
        with self.lock:
            now = time.time()
            expired = [
                k for k, v in self.cache.items()
                if v['expires_at'] and v['expires_at'] < now
            ]
            for key in expired:
                del self.cache[key]


class IntelligentCacheManager:
    """Intelligent multi-tier caching system."""
    
    def __init__(self):
        # L1: In-memory LRU cache (fastest)
        self.l1_cache = LRUCache(capacity=1000)
        
        # L2: Redis cache (would be initialized if Redis available)
        self.redis_client = None
        self._init_redis()
        
        # Cache key dependencies for smart invalidation
        self.dependencies = {}  # cache_key -> [dependent_keys]
        self.dependency_lock = threading.Lock()
        
        # Cache warming queue
        self.warm_queue = []
        
        # Cache statistics
        self.stats = {
            'l1_hits': 0,
            'l1_misses': 0,
            'l2_hits': 0,
            'l2_misses': 0,
            'invalidations': 0
        }
    
    def _init_redis(self):
        """Initialize Redis connection (if available)."""
        try:
            import redis
            import os
            redis_url = os.getenv('REDIS_URL', None)
            if redis_url:
                self.redis_client = redis.from_url(redis_url)
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache connected")
            else:
                logger.info("Redis not configured, using memory cache only")
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}")
            self.redis_client = None
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache (L1 → L2 → None)."""
        # Try L1 cache first
        value = self.l1_cache.get(key)
        if value is not None:
            self.stats['l1_hits'] += 1
            return value
        
        self.stats['l1_misses'] += 1
        
        # Try L2 (Redis) if available
        if self.redis_client:
            try:
                redis_value = self.redis_client.get(key)
                if redis_value:
                    self.stats['l2_hits'] += 1
                    # Deserialize
                    value = pickle.loads(redis_value)
                    # Promote to L1
                    self.l1_cache.set(key, value)
                    return value
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
        
        self.stats['l2_misses'] += 1
        return default
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = 3600,
        dependencies: Optional[List[str]] = None
    ):
        """Set value in cache (L1 and L2)."""
        # Set in L1
        self.l1_cache.set(key, value, ttl)
        
        # Set in L2 (Redis) if available
        if self.redis_client:
            try:
                serialized = pickle.dumps(value)
                if ttl:
                    self.redis_client.setex(key, ttl, serialized)
                else:
                    self.redis_client.set(key, serialized)
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")
        
        # Register dependencies
        if dependencies:
            with self.dependency_lock:
                for dep_key in dependencies:
                    if dep_key not in self.dependencies:
                        self.dependencies[dep_key] = []
                    self.dependencies[dep_key].append(key)
    
    def delete(self, key: str, cascade: bool = True):
        """Delete key from cache."""
        # Delete from L1
        self.l1_cache.delete(key)
        
        # Delete from L2
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")
        
        self.stats['invalidations'] += 1
        
        # Cascade delete dependencies
        if cascade:
            with self.dependency_lock:
                if key in self.dependencies:
                    dependent_keys = self.dependencies[key]
                    for dep_key in dependent_keys:
                        self.delete(dep_key, cascade=False)
                    del self.dependencies[key]
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern."""
        # L1: Manual pattern matching
        keys_to_delete = [k for k in self.l1_cache.cache.keys() if pattern in k]
        for key in keys_to_delete:
            self.l1_cache.delete(key)
        
        # L2: Redis SCAN for pattern matching
        if self.redis_client:
            try:
                cursor = 0
                while True:
                    cursor, keys = self.redis_client.scan(cursor, match=f"*{pattern}*", count=100)
                    if keys:
                        self.redis_client.delete(*keys)
                    if cursor == 0:
                        break
            except Exception as e:
                logger.warning(f"Redis pattern delete failed: {e}")
        
        self.stats['invalidations'] += len(keys_to_delete)
    
    def clear_all(self):
        """Clear all caches."""
        self.l1_cache.clear()
        
        if self.redis_client:
            try:
                self.redis_client.flushdb()
            except Exception as e:
                logger.warning(f"Redis flush failed: {e}")
        
        with self.dependency_lock:
            self.dependencies.clear()
    
    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable,
        ttl: Optional[int] = 3600,
        dependencies: Optional[List[str]] = None
    ) -> Any:
        """Get from cache or compute and cache."""
        # Try to get from cache
        value = self.get(key)
        if value is not None:
            return value
        
        # Compute value
        value = compute_fn()
        
        # Cache it
        self.set(key, value, ttl, dependencies)
        
        return value
    
    def warm_cache(self, keys: List[tuple]):
        """Warm cache with pre-computed values.
        
        Args:
            keys: List of (key, compute_fn, ttl) tuples
        """
        for key, compute_fn, ttl in keys:
            try:
                value = compute_fn()
                self.set(key, value, ttl)
                logger.debug(f"Warmed cache: {key}")
            except Exception as e:
                logger.warning(f"Cache warming failed for {key}: {e}")
    
    def get_stats(self) -> Dict:
        """Get comprehensive cache statistics."""
        l1_stats = self.l1_cache.get_stats()
        
        total_hits = self.stats['l1_hits'] + self.stats['l2_hits']
        total_misses = self.stats['l1_misses'] + self.stats['l2_misses']
        total_requests = total_hits + total_misses
        
        overall_hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        
        redis_stats = {}
        if self.redis_client:
            try:
                info = self.redis_client.info('stats')
                redis_stats = {
                    'total_keys': self.redis_client.dbsize(),
                    'hits': info.get('keyspace_hits', 0),
                    'misses': info.get('keyspace_misses', 0),
                    'evictions': info.get('evicted_keys', 0)
                }
            except Exception:
                pass
        
        return {
            'l1_cache': l1_stats,
            'l2_cache': redis_stats,
            'overall': {
                'hit_rate': overall_hit_rate,
                'total_hits': total_hits,
                'total_misses': total_misses,
                'invalidations': self.stats['invalidations']
            },
            'dependencies': len(self.dependencies)
        }


# ---------------------------------------------------------------------------
# Singleton instance
# ---------------------------------------------------------------------------

_cache_manager = None

def get_cache_manager() -> IntelligentCacheManager:
    """Get singleton cache manager."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = IntelligentCacheManager()
    return _cache_manager


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------

def cached(ttl: int = 3600, key_prefix: str = '', dependencies: Optional[List[str]] = None):
    """Cache decorator for functions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix or func.__name__]
            
            # Add args to key
            for arg in args:
                if isinstance(arg, (str, int, float, bool)):
                    key_parts.append(str(arg))
                else:
                    key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
            
            # Add kwargs to key
            for k, v in sorted(kwargs.items()):
                if isinstance(v, (str, int, float, bool)):
                    key_parts.append(f"{k}={v}")
                else:
                    key_parts.append(f"{k}={hashlib.md5(str(v).encode()).hexdigest()[:8]}")
            
            cache_key = ':'.join(key_parts)
            
            # Get from cache
            cache_manager = get_cache_manager()
            value = cache_manager.get(cache_key)
            
            if value is not None:
                return value
            
            # Compute and cache
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl, dependencies)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(key_or_pattern: str, cascade: bool = True):
    """Invalidate cache by key or pattern."""
    cache_manager = get_cache_manager()
    
    if '*' in key_or_pattern:
        cache_manager.invalidate_pattern(key_or_pattern.replace('*', ''))
    else:
        cache_manager.delete(key_or_pattern, cascade)


# ---------------------------------------------------------------------------
# API Functions
# ---------------------------------------------------------------------------

def get_cache_stats() -> Dict:
    """Get cache statistics."""
    manager = get_cache_manager()
    return manager.get_stats()


def clear_cache(pattern: Optional[str] = None):
    """Clear cache."""
    manager = get_cache_manager()
    
    if pattern:
        manager.invalidate_pattern(pattern)
        return {'success': True, 'cleared': 'pattern', 'pattern': pattern}
    else:
        manager.clear_all()
        return {'success': True, 'cleared': 'all'}


def warm_cache_with_common_queries():
    """Warm cache with commonly accessed data."""
    from models import get_session, Order, Customer, Subscription
    from sqlalchemy import func
    import time as time_module
    
    manager = get_cache_manager()
    session = get_session()
    
    # Define warming tasks
    tasks = []
    
    # Recent orders count
    tasks.append((
        'stats:orders:recent_count',
        lambda: session.query(func.count(Order.id)).filter(
            Order.created_at >= time_module.time() - 86400
        ).scalar() or 0,
        300  # 5 min TTL
    ))
    
    # Active subscriptions count
    tasks.append((
        'stats:subscriptions:active_count',
        lambda: session.query(func.count(Subscription.id)).filter(
            Subscription.status == 'ACTIVE'
        ).scalar() or 0,
        600  # 10 min TTL
    ))
    
    # Total customers
    tasks.append((
        'stats:customers:total',
        lambda: session.query(func.count(Customer.receipt)).scalar() or 0,
        3600  # 1 hour TTL
    ))
    
    # Warm the cache
    manager.warm_cache(tasks)
    
    session.close()
    
    return {'success': True, 'warmed': len(tasks)}


# ---------------------------------------------------------------------------
# Query Result Caching
# ---------------------------------------------------------------------------

class QueryCache:
    """Cache for database query results."""
    
    def __init__(self, cache_manager: IntelligentCacheManager):
        self.cache = cache_manager
    
    def cache_query(
        self,
        query_key: str,
        query_fn: Callable,
        ttl: int = 300,
        invalidate_on: Optional[List[str]] = None
    ) -> Any:
        """Cache query results.
        
        Args:
            query_key: Unique key for query
            query_fn: Function that executes query
            ttl: Time to live in seconds
            invalidate_on: List of table/model names that invalidate this cache
        """
        # Generate cache key
        cache_key = f"query:{query_key}"
        
        # Try to get from cache
        result = self.cache.get(cache_key)
        if result is not None:
            return result
        
        # Execute query
        result = query_fn()
        
        # Cache result with dependencies
        dependencies = [f"table:{table}" for table in (invalidate_on or [])]
        self.cache.set(cache_key, result, ttl, dependencies)
        
        return result
    
    def invalidate_table(self, table_name: str):
        """Invalidate all queries for a table."""
        self.cache.delete(f"table:{table_name}", cascade=True)


def get_query_cache() -> QueryCache:
    """Get query cache instance."""
    return QueryCache(get_cache_manager())
