"""
Cache Manager for Finance News AgentOS
Provides Redis and database caching with TTL support
"""

from datetime import datetime, timedelta
import hashlib
import json
import logging
import sqlite3
from typing import Any

# Redis imports with fallback
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


class CacheManager:
    """Unified cache manager supporting Redis and SQLite fallback"""

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        cache_db_path: str = "cache.db",
        default_ttl: int = 1800,
    ):  # 30 minutes
        self.redis_client = None
        self.cache_db_path = cache_db_path
        self.default_ttl = default_ttl

        # Initialize Redis if available
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Falling back to SQLite cache.")
                self.redis_client = None
        else:
            logger.info("Redis not available. Using SQLite cache only.")

        # Initialize SQLite cache as fallback
        self._init_sqlite_cache()

    def _init_sqlite_cache(self):
        """Initialize SQLite cache database"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cache_entries (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at)
                """)
                conn.commit()
            logger.info("SQLite cache initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite cache: {e}")

    def _generate_key(self, prefix: str, params: dict[str, Any]) -> str:
        """Generate cache key from prefix and parameters"""
        # Sort params for consistent hashing
        sorted_params = json.dumps(params, sort_keys=True)
        hash_obj = hashlib.md5(sorted_params.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"

    def get(self, key: str) -> Any | None:
        """Get value from cache (Redis first, SQLite fallback)"""
        try:
            # Try Redis first
            if self.redis_client:
                try:
                    value = self.redis_client.get(key)
                    if value:
                        return json.loads(value)
                except Exception as e:
                    logger.warning(f"Redis get failed: {e}")

            # Fallback to SQLite
            return self._sqlite_get(key)
        except Exception as e:
            logger.error(f"Cache get failed for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache with TTL"""
        if ttl is None:
            ttl = self.default_ttl

        try:
            json_value = json.dumps(value)

            # Try Redis first
            if self.redis_client:
                try:
                    success = self.redis_client.setex(key, ttl, json_value)
                    if success:
                        return True
                except Exception as e:
                    logger.warning(f"Redis set failed: {e}")

            # Fallback to SQLite
            return self._sqlite_set(key, json_value, ttl)
        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            return False

    def _sqlite_get(self, key: str) -> Any | None:
        """Get value from SQLite cache"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.execute(
                    "SELECT value FROM cache_entries WHERE key = ? AND expires_at > ?",
                    (key, datetime.now()),
                )
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None
        except Exception as e:
            logger.error(f"SQLite get failed for key {key}: {e}")
            return None

    def _sqlite_set(self, key: str, json_value: str, ttl: int) -> bool:
        """Set value in SQLite cache"""
        try:
            expires_at = datetime.now() + timedelta(seconds=ttl)
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO cache_entries (key, value, expires_at) VALUES (?, ?, ?)",
                    (key, json_value, expires_at),
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"SQLite set failed for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            # Delete from Redis
            if self.redis_client:
                try:
                    self.redis_client.delete(key)
                except Exception as e:
                    logger.warning(f"Redis delete failed: {e}")

            # Delete from SQLite
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Cache delete failed for key {key}: {e}")
            return False

    def clear_expired(self):
        """Clear expired entries from SQLite cache"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM cache_entries WHERE expires_at <= ?", (datetime.now(),)
                )
                deleted_count = cursor.rowcount
                conn.commit()
                logger.info(f"Cleared {deleted_count} expired cache entries")
        except Exception as e:
            logger.error(f"Failed to clear expired entries: {e}")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        stats = {
            "redis_available": self.redis_client is not None,
            "sqlite_entries": 0,
            "sqlite_expired": 0,
        }

        try:
            # Redis stats
            if self.redis_client:
                try:
                    info = self.redis_client.info()
                    stats["redis_memory"] = info.get("used_memory_human", "N/A")
                    stats["redis_keys"] = self.redis_client.dbsize()
                except Exception as e:
                    logger.warning(f"Failed to get Redis stats: {e}")

            # SQLite stats
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM cache_entries")
                stats["sqlite_entries"] = cursor.fetchone()[0]

                cursor = conn.execute(
                    "SELECT COUNT(*) FROM cache_entries WHERE expires_at <= ?", (datetime.now(),)
                )
                stats["sqlite_expired"] = cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")

        return stats


# Cache configurations for different data types
CACHE_CONFIGS = {
    "market_overview": {"ttl": 900, "prefix": "market_overview"},  # 15 minutes
    "quick_analysis": {"ttl": 1800, "prefix": "quick_analysis"},  # 30 minutes
    "agent_response": {"ttl": 3600, "prefix": "agent_response"},  # 1 hour
    "daily_report": {"ttl": 86400, "prefix": "daily_report"},  # 24 hours
    "health_check": {"ttl": 300, "prefix": "health_check"},  # 5 minutes
}

# Global cache manager instance
cache_manager: CacheManager | None = None


def init_cache_manager(**kwargs) -> CacheManager:
    """Initialize global cache manager"""
    global cache_manager
    cache_manager = CacheManager(**kwargs)
    return cache_manager


def get_cache_manager() -> CacheManager | None:
    """Get global cache manager instance"""
    return cache_manager


def cache_key_for(cache_type: str, **params) -> str:
    """Generate cache key for specific type and parameters"""
    if cache_type not in CACHE_CONFIGS:
        raise ValueError(f"Unknown cache type: {cache_type}")

    config = CACHE_CONFIGS[cache_type]
    if cache_manager:
        return cache_manager._generate_key(str(config["prefix"]), params)
    return f"{config['prefix']}:fallback"


def cached_response(cache_type: str, **params):
    """Decorator for caching function responses"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            if not cache_manager:
                return func(*args, **kwargs)

            # Generate cache key
            cache_key = cache_key_for(cache_type, **params, **kwargs)

            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for {cache_type}: {cache_key}")
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)

            # Cache the result
            config = CACHE_CONFIGS[cache_type]
            ttl_value = config["ttl"]
            cache_manager.set(cache_key, result, ttl_value if isinstance(ttl_value, int) else 1800)
            logger.info(f"Cached {cache_type}: {cache_key}")

            return result

        return wrapper

    return decorator
