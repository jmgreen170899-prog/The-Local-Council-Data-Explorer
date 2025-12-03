"""
Tests for the cache module.
"""

import time

import pytest

from services.cache import CacheEntry, InMemoryCache


class TestCacheEntry:
    """Tests for CacheEntry dataclass."""

    def test_cache_entry_not_expired(self):
        """Test that a fresh cache entry is not expired."""
        entry = CacheEntry(
            value="test_value",
            expires_at=time.time() + 100,
            created_at=time.time(),
        )
        assert not entry.is_expired()

    def test_cache_entry_expired(self):
        """Test that an old cache entry is expired."""
        entry = CacheEntry(
            value="test_value",
            expires_at=time.time() - 1,  # Expired 1 second ago
            created_at=time.time() - 100,
        )
        assert entry.is_expired()


class TestInMemoryCache:
    """Tests for InMemoryCache class."""

    def test_get_returns_none_for_missing_key(self):
        """Test that get returns None for a key that doesn't exist."""
        cache = InMemoryCache()
        assert cache.get("missing_key") is None

    def test_set_and_get(self):
        """Test setting and getting a value."""
        cache = InMemoryCache()
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"

    def test_get_returns_none_for_expired_entry(self):
        """Test that get returns None for an expired entry."""
        cache = InMemoryCache(default_ttl=1)
        cache.set("test_key", "test_value", ttl=0)  # Expires immediately
        
        # Wait a tiny bit for the entry to expire
        time.sleep(0.01)
        
        assert cache.get("test_key") is None

    def test_delete_existing_key(self):
        """Test deleting an existing key."""
        cache = InMemoryCache()
        cache.set("test_key", "test_value")
        
        result = cache.delete("test_key")
        
        assert result is True
        assert cache.get("test_key") is None

    def test_delete_missing_key(self):
        """Test deleting a key that doesn't exist."""
        cache = InMemoryCache()
        result = cache.delete("missing_key")
        assert result is False

    def test_clear(self):
        """Test clearing all entries."""
        cache = InMemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.size() == 0

    def test_size(self):
        """Test getting cache size."""
        cache = InMemoryCache()
        assert cache.size() == 0
        
        cache.set("key1", "value1")
        assert cache.size() == 1
        
        cache.set("key2", "value2")
        assert cache.size() == 2

    def test_cleanup_removes_expired_entries(self):
        """Test that cleanup removes expired entries."""
        cache = InMemoryCache()
        cache.set("key1", "value1", ttl=0)  # Expires immediately
        cache.set("key2", "value2", ttl=1000)  # Won't expire
        
        # Wait a tiny bit for the entry to expire
        time.sleep(0.01)
        
        removed = cache.cleanup()
        
        assert removed == 1
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_generate_key_with_prefix_only(self):
        """Test generating a cache key with just a prefix."""
        cache = InMemoryCache()
        key = cache.generate_key("service")
        assert key == "service"

    def test_generate_key_with_args(self):
        """Test generating a cache key with positional arguments."""
        cache = InMemoryCache()
        key = cache.generate_key("service", "arg1", "arg2")
        assert key == "service:arg1:arg2"

    def test_generate_key_with_kwargs(self):
        """Test generating a cache key with keyword arguments."""
        cache = InMemoryCache()
        key = cache.generate_key("service", postcode="YO1 1AA", uprn="123456")
        # kwargs should be sorted alphabetically
        assert key == "service:postcode=YO1 1AA:uprn=123456"

    def test_generate_key_ignores_none_values(self):
        """Test that None values are ignored in key generation."""
        cache = InMemoryCache()
        key = cache.generate_key("service", None, "arg1", postcode=None, uprn="123456")
        assert key == "service:arg1:uprn=123456"

    def test_custom_ttl(self):
        """Test setting a custom TTL."""
        cache = InMemoryCache(default_ttl=1)
        cache.set("test_key", "test_value", ttl=1000)
        
        # Value should still be there after default TTL would have expired
        time.sleep(0.1)
        assert cache.get("test_key") == "test_value"
