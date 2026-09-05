---
title: Cache
description: Cache stores, remembering values, atomic locks, and tags.
---

## Introduction

Avalon’s cache layer stores temporary data behind a single façade. Use it to
memoize expensive work, share short-lived state between requests, and take
cross-process locks for scheduled tasks or jobs.

```python
from avalon.cache import Cache, cache

Cache.put("users:1", {"name": "Ada"}, 60)
user = Cache.get("users:1")
Cache.remember("stats:home", 120, lambda: compute_stats())
```

## Configuration

Scaffolded apps ship `config/cache.py`. The default store and key prefix come
from the environment:

### Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `CACHE_STORE` | `file` | Name of the default store (`array`, `file`, `database`, `null`, …) |
| `CACHE_PREFIX` | `avalon_cache_` | Prefix applied to every cache key |

```env
CACHE_STORE=file
CACHE_PREFIX=avalon_cache_
```

```python
# config/cache.py
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

### Choosing a store

| Store | When to use it |
| --- | --- |
| **array** | Process-local only — ideal for tests and demos (progress defaults here) |
| **file** | Single-server apps; data under `storage/framework/cache/data` |
| **database** | Shared cache across app processes via Articulate (`cache` + `cache_locks` tables) |
| **null** | Disable caching without removing call sites (writes accepted, reads miss) |

A Redis driver arrives with milestone **M16**. Until then, prefer `file` or
`database` in multi-process deployments.

Switch stores per call:

```python
Cache.store("file").put("logo", svg, 3600)
Cache.store("database").get("logo")
```

## Retrieving items

```python
Cache.get("users:1")
Cache.get("missing", "default")
Cache.get("missing", lambda: expensive_default())

Cache.has("users:1")
Cache.missing("users:1")

Cache.many(["users:1", "users:2"])
Cache.pull("users:1")   # get + forget
```

### Storing items

```python
Cache.put("users:1", {"name": "Ada"}, 60)
Cache.put_many({"a": 1, "b": 2}, 60)
Cache.forever("config", payload)

Cache.add("users:1", {"name": "Ada"}, 60)  # only if absent (atomic)
Cache.touch("users:1", 120)                # refresh TTL, keep value
```

TTL may be seconds, a `timedelta`, or an aware/naive `datetime`.

### Remembering values

```python
value = Cache.remember("answer", 60, lambda: expensive())
value = Cache.remember_forever("config", lambda: load_config())
```

`remember` stores the callback result on a miss and returns it on hits.

### The `cache()` helper

```python
from avalon.cache import cache

cache("users:1")          # get
cache({"k": "v"}, 60)     # put many
repo = cache()            # default store repository
```

### Incrementing / decrementing

```python
Cache.increment("hits")
Cache.increment("hits", 5)
Cache.decrement("hits")
```

Database `increment` / `decrement` run inside a transaction. `add` is atomic on
every store (process lock / `flock` / `INSERT OR IGNORE`).

### Removing items

```python
Cache.forget("users:1")
Cache.flush()
```

## Database tables

The database driver ensures two tables on first use:

```sql
-- cache
key VARCHAR(255) PRIMARY KEY, value BLOB, expiration INTEGER NULL

-- cache_locks
key VARCHAR(255) PRIMARY KEY, owner VARCHAR(255), expiration INTEGER NOT NULL
```

You can also call `ensure_cache_table()` / `ensure_cache_table_sync()` from
`avalon.cache` in migrations or bootstraps.

## Atomic locks

Locks coordinate work across processes:

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
| --- | --- |
| array | Atomic `add` under a process lock |
| file | `.locks/` + `fcntl.flock` |
| database | `cache_locks` table |

Scheduled `without_overlapping()` prefers cache locks when Cache is booted,
falling back to a filesystem mutex — see [Task Scheduling](/scheduling/).

## Cache tags

Tags let you invalidate related keys as a group. They work on the **array**
store today (Redis tags arrive with M16). File and database stores raise
`RuntimeError` if you call `tags()` — Avalon is honest about driver support.

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
