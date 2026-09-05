---
title: Cache
description: Cache façade, array/file/database stores, atomic locks, and tags.
---

## Overview

```python
from avalon.cache import Cache, cache

Cache.put("users:1", {"name": "Ada"}, 60)
Cache.get("users:1")
Cache.many(["users:1", "users:2"])
Cache.put_many({"a": 1, "b": 2}, 60)
Cache.remember("answer", 60, lambda: expensive())
Cache.forever("config", payload)
Cache.touch("users:1", 120)   # refresh TTL
Cache.forget("users:1")
Cache.flush()

cache("users:1")          # get
cache({"k": "v"}, 60)     # put many
cache()                   # default store repository
```

Configure stores in `config/cache.py`. Defaults: **array** (tests), **file**,
**database**, **null**. Redis arrives with **M16**.

`add` is atomic on every store (process lock / `flock` / `INSERT OR IGNORE`).
Database `increment` runs inside a transaction.

## Locks

```python
with Cache.lock("invoices:settle", seconds=10):
    settle()

Cache.lock("deploy").block(5, lambda: deploy())

# Cross-process release (queue workers, etc.)
owner = lock.owner_token()
Cache.restore_lock("deploy", owner).release()

Cache.flush_locks()
Cache.without_overlapping("report", lambda: build_report())
```

| Store | Lock backend |
|---|---|
| array | Atomic `add` under a process lock |
| file | `.locks/` + `fcntl.flock` |
| database | `cache_locks` table (`DatabaseLock`) |

Scheduled `without_overlapping()` prefers cache locks when Cache is booted,
falling back to the filesystem mutex.

## Tags

Tags work on the **array** store (and **Redis in M16**). File and database
stores raise — same rule as Laravel.

```python
Cache.tags("users", "authors").put("ada", user, 60)
Cache.tags("users", "authors").flush()
```

## Custom drivers

```python
Cache.extend("mongo", lambda app, cfg, name: MongoStore(...))
```

## Related

- [Task Scheduling](/scheduling/) — overlap locks
- [Queues](/queues/) — unique jobs (Redis locks in M16)
- [File Storage](/filesystem/) — file cache path under `storage/framework/cache`
