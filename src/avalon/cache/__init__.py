"""Laravel-shaped Cache — stores, locks, and ``cache()`` helper."""

from __future__ import annotations

from avalon.cache.helpers import cache, default_cache_config, get_manager, set_manager
from avalon.cache.locks import CacheLock, DatabaseLock, FileLock, LockTimeoutError
from avalon.cache.manager import Cache, CacheManager
from avalon.cache.provider import CacheServiceProvider
from avalon.cache.schema import ensure_cache_table, ensure_cache_table_sync
from avalon.cache.store import Repository, TaggedCache

__all__ = [
    "Cache",
    "CacheLock",
    "CacheManager",
    "CacheServiceProvider",
    "DatabaseLock",
    "FileLock",
    "LockTimeoutError",
    "Repository",
    "TaggedCache",
    "cache",
    "default_cache_config",
    "ensure_cache_table",
    "ensure_cache_table_sync",
    "get_manager",
    "set_manager",
]
