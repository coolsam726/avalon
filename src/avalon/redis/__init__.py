"""Redis connections and façade — optional ``avalon[redis]`` extra."""

from __future__ import annotations

from avalon.redis.facade import Redis
from avalon.redis.helpers import default_redis_config, get_manager, redis, set_manager
from avalon.redis.manager import RedisManager, require_redis
from avalon.redis.provider import RedisServiceProvider

__all__ = [
    "Redis",
    "RedisManager",
    "RedisServiceProvider",
    "default_redis_config",
    "get_manager",
    "redis",
    "require_redis",
    "set_manager",
]
