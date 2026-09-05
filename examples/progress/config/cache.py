"""Cache stores."""

from avalon.config import env

config = {
    "default": env("CACHE_STORE", "array"),
    "prefix": env("CACHE_PREFIX", "avalon_cache_"),
    "stores": {
        "array": {"driver": "array"},
        "file": {
            "driver": "file",
            "path": "storage/framework/cache/data",
        },
        "database": {
            "driver": "database",
            "connection": None,
            "table": "cache",
            "lock_table": "cache_locks",
        },
        "null": {"driver": "null"},
    },
}
