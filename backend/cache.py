# backend/cache.py - Caching system for performance optimization

import redis
import json
import pickle
from datetime import timedelta
from functools import wraps
from flask import current_app

# Redis client for caching
redis_client = None

def init_cache(app):
    """Initialize Redis cache"""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=app.config.get('REDIS_HOST', 'localhost'),
            port=app.config.get('REDIS_PORT', 6379),
            db=app.config.get('REDIS_CACHE_DB', 1),  # Use DB 1 for cache
            decode_responses=True
        )
        # Test connection
        redis_client.ping()
        print("✅ Redis cache initialized successfully")
    except Exception as e:
        print(f"⚠️  Redis cache not available: {e}")
        redis_client = None

def cache_key(prefix, *args, **kwargs):
    """Generate cache key from prefix and arguments"""
    key_parts = [prefix]
    
    # Add positional arguments
    for arg in args:
        key_parts.append(str(arg))
    
    # Add keyword arguments
    for key, value in sorted(kwargs.items()):
        key_parts.append(f"{key}:{value}")
    
    return ":".join(key_parts)

def get_cache(key, default=None):
    """Get value from cache"""
    if not redis_client:
        return default
    
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return default
    except Exception as e:
        print(f"Cache get error: {e}")
        return default

def set_cache(key, value, expire_seconds=300):
    """Set value in cache with expiration"""
    if not redis_client:
        return False
    
    try:
        redis_client.setex(
            key,
            expire_seconds,
            json.dumps(value, default=str)
        )
        return True
    except Exception as e:
        print(f"Cache set error: {e}")
        return False

def delete_cache(key):
    """Delete value from cache"""
    if not redis_client:
        return False
    
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Cache delete error: {e}")
        return False

def clear_cache_pattern(pattern):
    """Clear cache entries matching pattern"""
    if not redis_client:
        return False
    
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
        return True
    except Exception as e:
        print(f"Cache clear pattern error: {e}")
        return False

def cache_decorator(prefix, expire_seconds=300):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = get_cache(key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache the result
            set_cache(key, result, expire_seconds)
            
            return result
        return wrapper
    return decorator

# Cache keys for different data types
class CacheKeys:
    USER_DASHBOARD = "user:dashboard"
    USER_SCORES = "user:scores"
    SUBJECT_LIST = "subjects:list"
    QUIZ_LIST = "quiz:list"
    QUIZ_DETAILS = "quiz:details"
    ADMIN_STATS = "admin:stats"
    USER_PROFILE = "user:profile"

# Cache expiration times (in seconds)
class CacheExpiry:
    SHORT = 60      # 1 minute
    MEDIUM = 300    # 5 minutes
    LONG = 1800     # 30 minutes
    VERY_LONG = 3600  # 1 hour

# Cache invalidation functions
def invalidate_user_cache(user_id):
    """Invalidate all cache entries for a specific user"""
    patterns = [
        f"{CacheKeys.USER_DASHBOARD}:{user_id}",
        f"{CacheKeys.USER_SCORES}:{user_id}",
        f"{CacheKeys.USER_PROFILE}:{user_id}"
    ]
    for pattern in patterns:
        clear_cache_pattern(pattern)

def invalidate_quiz_cache(quiz_id=None):
    """Invalidate quiz-related cache"""
    if quiz_id:
        patterns = [
            f"{CacheKeys.QUIZ_DETAILS}:{quiz_id}",
            f"{CacheKeys.QUIZ_LIST}:*"
        ]
    else:
        patterns = [
            f"{CacheKeys.QUIZ_DETAILS}:*",
            f"{CacheKeys.QUIZ_LIST}:*"
        ]
    
    for pattern in patterns:
        clear_cache_pattern(pattern)

def invalidate_subject_cache():
    """Invalidate subject-related cache"""
    clear_cache_pattern(f"{CacheKeys.SUBJECT_LIST}:*")

def invalidate_admin_cache():
    """Invalidate admin-related cache"""
    clear_cache_pattern(f"{CacheKeys.ADMIN_STATS}:*")

# Performance monitoring
def get_cache_stats():
    """Get cache statistics"""
    if not redis_client:
        return {"error": "Redis not available"}
    
    try:
        info = redis_client.info()
        return {
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "total_commands_processed": info.get("total_commands_processed", 0)
        }
    except Exception as e:
        return {"error": str(e)} 