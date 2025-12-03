"""
Caching module for the Local Council Data Explorer backend.

This module provides a simple in-memory cache with TTL (time-to-live) support
for caching API responses to reduce external API calls and improve response times.

The cache uses a dictionary-based storage with automatic expiration of entries
based on their TTL values. It is thread-safe for basic operations.
"""

import logging
import time
from dataclasses import dataclass
from threading import Lock
from typing import Any, Dict, Generic, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    """Represents a single entry in the cache.

    Attributes:
        value: The cached value.
        expires_at: Unix timestamp when the entry expires.
        created_at: Unix timestamp when the entry was created.
    """

    value: T
    expires_at: float
    created_at: float

    def is_expired(self) -> bool:
        """Check if this cache entry has expired.

        Returns:
            True if the entry has expired, False otherwise.
        """
        return time.time() > self.expires_at


class InMemoryCache:
    """Thread-safe in-memory cache with TTL support.

    This cache stores key-value pairs with automatic expiration.
    Expired entries are cleaned up lazily on access and periodically
    via the cleanup method.

    Attributes:
        default_ttl: Default time-to-live for entries in seconds.
    """

    def __init__(self, default_ttl: int = 300):
        """Initialize the cache.

        Args:
            default_ttl: Default time-to-live for cache entries in seconds.
                        Defaults to 300 seconds (5 minutes).
        """
        self._cache: Dict[str, CacheEntry[Any]] = {}
        self._lock = Lock()
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache.

        If the entry exists but has expired, it will be removed and None returned.

        Args:
            key: The cache key to look up.

        Returns:
            The cached value if found and not expired, None otherwise.
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                logger.debug(f"Cache miss for key: {key}")
                return None

            if entry.is_expired():
                logger.debug(f"Cache entry expired for key: {key}")
                del self._cache[key]
                return None

            logger.debug(f"Cache hit for key: {key}")
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value in the cache.

        Args:
            key: The cache key.
            value: The value to cache.
            ttl: Time-to-live in seconds. If not provided, uses default_ttl.
        """
        if ttl is None:
            ttl = self.default_ttl

        current_time = time.time()
        entry = CacheEntry(
            value=value,
            expires_at=current_time + ttl,
            created_at=current_time,
        )

        with self._lock:
            self._cache[key] = entry
            logger.debug(f"Cached value for key: {key}, TTL: {ttl}s")

    def delete(self, key: str) -> bool:
        """Remove an entry from the cache.

        Args:
            key: The cache key to remove.

        Returns:
            True if the key existed and was removed, False otherwise.
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Deleted cache entry for key: {key}")
                return True
            return False

    def clear(self) -> None:
        """Remove all entries from the cache."""
        with self._lock:
            self._cache.clear()
            logger.debug("Cache cleared")

    def cleanup(self) -> int:
        """Remove all expired entries from the cache.

        Returns:
            Number of entries removed.
        """
        removed = 0
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
                removed += 1

        if removed > 0:
            logger.debug(f"Cleaned up {removed} expired cache entries")
        return removed

    def size(self) -> int:
        """Get the number of entries in the cache.

        Returns:
            Number of cache entries (including potentially expired ones).
        """
        with self._lock:
            return len(self._cache)

    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments.

        This helper method creates consistent cache keys from function arguments.

        Args:
            prefix: A prefix for the cache key (e.g., service name).
            *args: Positional arguments to include in the key.
            **kwargs: Keyword arguments to include in the key.

        Returns:
            A string cache key.
        """
        parts = [prefix]
        parts.extend(str(arg) for arg in args if arg is not None)
        parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()) if v is not None)
        return ":".join(parts)


# Global cache instances for each service
# These are initialized with appropriate TTLs for each data type

bins_cache = InMemoryCache(default_ttl=3600)  # 1 hour for bin schedules
planning_cache = InMemoryCache(default_ttl=1800)  # 30 minutes for planning data
air_quality_cache = InMemoryCache(default_ttl=600)  # 10 minutes for air quality


def get_bins_cache() -> InMemoryCache:
    """Get the cache instance for bin collection data.

    Returns:
        InMemoryCache instance configured for bin data.
    """
    return bins_cache


def get_planning_cache() -> InMemoryCache:
    """Get the cache instance for planning application data.

    Returns:
        InMemoryCache instance configured for planning data.
    """
    return planning_cache


def get_air_quality_cache() -> InMemoryCache:
    """Get the cache instance for air quality data.

    Returns:
        InMemoryCache instance configured for air quality data.
    """
    return air_quality_cache
