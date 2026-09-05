---
title: Cache
description: Cache façade, array/file/database stores, atomic locks, and tags.
---

## Overview

```python
from avalon.cache import Cache, cache

Cache.put("users:1", {"name": "Ada"}, 60)
Cache.get("users:1")
Cache.get("missing", "default")
Cache.get("missing", lambda: expensive_default())

Cache.has("users:1")
Cache.missing("users:1")

Cache.add("users:1", {"name": "Ada"}, 60)  # only if absent (atomic)
Cache.pull("users:1")                      # get + forget

Cache.many(["users:1", "users:2"])
Cache.put_many({"a": 1, "b": 2}, 60)

Cache.remember("answer", 60, lambda: expensive())
Cache.remember_forever("config", lambda: load_config())
Cache.forever("config", payload)
Cache.touch("users:1", 120)                # refresh TTL, keep value

Cache.increment("hits")
Cache.increment("hits", 5)
Cache.decrement("hits")

Cache.forget("users:1")
Cache.flush()

cache("users:1")          # get
cache({"k": "v"}, 60)     # put many
cache()                   # default store repository
```

TTL may be seconds, a `timedelta`, or an aware/naive `datetime`.

Named stores:

```python
Cache.store("file").put("logo", svg, 3600)
Cache.store("database").get("logo")
```

## Configuration

Scaffold / progress ship `config/cache.py`:

```python
from avalon.config import env

config = {
    "default": env("CACHE_STORE", "file"),
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
```

| Store | Role |
|---|---|
| **array** | Process-local (tests / default in progress) |
| **file** | Disk under `storage/framework/cache/data` |
| **database** | `cache` table via Articulate |
| **null** | Accepts writes; never returns them |

Redis arrives with **M16**.

`add` is atomic on every store (process lock / `flock` / `INSERT OR IGNORE`).
Database `increment` / `decrement` run inside a transaction.

### Database tables

The database driver ensures two tables on first use:

```sql
-- cache
key VARCHAR(255) PRIMARY KEY, value BLOB, expiration INTEGER NULL

-- cache_locks
key VARCHAR(255) PRIMARY KEY, owner VARCHAR(255), expiration INTEGER NOT NULL
```

You can also call `ensure_cache_table()` / `ensure_cache_table_sync()` from `avalon.cache` in migrations or bootstraps.

## Locks

```python
lock = Cache.lock("invoices:settle", seconds=10)
if lock.get():
    try:
        settle()
    finally:
        lock.release()

# Callback form (auto-release)
Cache.lock("deploy").get(lambda: deploy())
Cache.lock("deploy").block(5, lambda: deploy())

with Cache.lock("invoices:settle", seconds=10):
    settle()

# Cross-process release (queue workers, etc.)
owner = lock.owner_token()
Cache.restore_lock("deploy", owner).release()

lock.force_release()   # ignore owner
Cache.flush_locks()
Cache.without_overlapping("report", lambda: build_report())
```

| Store | Lock backend |
|---|---|
| array | Atomic `add` under a process lock |
| file | `.locks/` + `fcntl.flock` |
| database | `cache_locks` table (`DatabaseLock`) |

Scheduled `without_overlapping()` prefers cache locks when Cache is booted,
falling back to the filesystem mutex — see [Task Scheduling](/scheduling/).

## Tags

Tags work on the **array** store (and **Redis in M16**). File and database
stores raise `RuntimeError` — same rule as Laravel.

```python
Cache.tags("users", "authors").put("ada", user, 60)
Cache.tags("users", "authors").get("ada")
Cache.tags("users", "authors").remember("ada", 60, lambda: load())
Cache.tags("users", "authors").forever("ada", user)
Cache.tags("users", "authors").forget("ada")
Cache.tags("users", "authors").flush()
```

## Custom drivers

```python
from avalon.cache import Cache
from avalon.cache.store import Repository

Cache.extend("mongo", lambda app, cfg, name: Repository(MongoStore(...)))
# then set stores.mongo.driver = "mongo" in config/cache.py
```

## Related

- [Task Scheduling](/scheduling/) — overlap locks
- [Queues](/queues/) — unique jobs (Redis locks in M16)
- [File Storage](/filesystem/) — file cache path under `storage/framework/cache`
