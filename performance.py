#!/usr/bin/env python3
"""
Performance Optimization - SURESH AI ORIGIN
Response caching, rate limiting, and query optimization
"""

from functools import wraps, lru_cache
from flask import request, jsonify
import time
import hashlib
import json
from collections import defaultdict
from threading import Lock

# In-memory cache
cache_store = {}
cache_ttl = {}
cache_lock = Lock()

# Rate limiting storage
rate_limit_store = defaultdict(list)
rate_limit_lock = Lock()

def cache_response(ttl=300):
    """
    Cache decorator for Flask routes.
    Args:
        ttl: Time to live in seconds (default 5 minutes)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from route, args, and query params
            cache_key = f"{func.__name__}:{args}:{sorted(request.args.items())}"
            cache_hash = hashlib.md5(cache_key.encode()).hexdigest()
            
            now = time.time()
            
            with cache_lock:
                # Check if cached and not expired
                if cache_hash in cache_store and cache_hash in cache_ttl:
                    if now < cache_ttl[cache_hash]:
                        cached_data, cached_status = cache_store[cache_hash]
                        return jsonify(cached_data), cached_status
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache the response
            if isinstance(result, tuple):
                data, status = result
            else:
                data, status = result, 200
            
            with cache_lock:
                cache_store[cache_hash] = (data.get_json() if hasattr(data, 'get_json') else data, status)
                cache_ttl[cache_hash] = now + ttl
            
            return result
        
        return wrapper
    return decorator

def clear_cache_for(pattern=''):
    """Clear cache entries matching pattern."""
    with cache_lock:
        keys_to_remove = [k for k in cache_store if pattern in k]
        for key in keys_to_remove:
            cache_store.pop(key, None)
            cache_ttl.pop(key, None)
        return len(keys_to_remove)

def rate_limit(max_requests=60, window=60):
    """
    Rate limiting decorator.
    Args:
        max_requests: Maximum requests allowed
        window: Time window in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get identifier (IP or customer ID)
            identifier = request.headers.get('X-Customer-ID') or request.remote_addr
            now = time.time()
            
            with rate_limit_lock:
                # Clean old entries
                rate_limit_store[identifier] = [
                    timestamp for timestamp in rate_limit_store[identifier]
                    if now - timestamp < window
                ]
                
                # Check if rate limited
                if len(rate_limit_store[identifier]) >= max_requests:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'retry_after': int(window - (now - rate_limit_store[identifier][0]))
                    }), 429
                
                # Record this request
                rate_limit_store[identifier].append(now)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

@lru_cache(maxsize=1000)
def get_cached_prediction(customer_id, model_type):
    """Cache expensive prediction calculations."""
    # This would be imported and used in predictive_analytics.py
    pass

def optimize_database_queries():
    """
    Add indexes to frequently queried columns.
    Run this once to optimize database performance.
    """
    import sqlite3
    from utils import _get_db_path
    
    try:
        conn = sqlite3.connect(_get_db_path())
        cursor = conn.cursor()
        
        # Check existing indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        existing = {row[0] for row in cursor.fetchall()}
        
        indexes = [
            ("idx_orders_status", "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)"),
            ("idx_orders_created", "CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at)"),
            ("idx_orders_receipt", "CREATE INDEX IF NOT EXISTS idx_orders_receipt ON orders(receipt)"),
            ("idx_payments_order", "CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id)"),
            ("idx_payments_status", "CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)"),
            ("idx_subscriptions_receipt", "CREATE INDEX IF NOT EXISTS idx_subscriptions_receipt ON subscriptions(receipt)"),
            ("idx_subscriptions_status", "CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status)"),
            ("idx_customers_receipt", "CREATE INDEX IF NOT EXISTS idx_customers_receipt ON customers(receipt)"),
        ]
        
        created = 0
        for index_name, sql in indexes:
            if index_name not in existing:
                cursor.execute(sql)
                created += 1
                print(f"✅ Created index: {index_name}")
        
        conn.commit()
        conn.close()
        
        if created > 0:
            print(f"\n✅ Created {created} database indexes for better performance")
        else:
            print("✅ All indexes already exist")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create indexes: {e}")
        return False

def get_cache_stats():
    """Get cache statistics."""
    with cache_lock:
        total_entries = len(cache_store)
        expired = sum(1 for expire_time in cache_ttl.values() if time.time() > expire_time)
        active = total_entries - expired
        
        return {
            'total_entries': total_entries,
            'active_entries': active,
            'expired_entries': expired,
            'hit_rate': 'N/A'  # Would need to track hits/misses
        }

def get_rate_limit_stats():
    """Get rate limiting statistics."""
    with rate_limit_lock:
        total_clients = len(rate_limit_store)
        active_requests = sum(len(requests) for requests in rate_limit_store.values())
        
        return {
            'tracked_clients': total_clients,
            'active_requests': active_requests
        }

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'optimize':
        print("🔧 Optimizing database...")
        optimize_database_queries()
    else:
        print("Usage:")
        print("  python performance.py optimize  - Create database indexes")
