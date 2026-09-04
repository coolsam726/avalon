---
title: Collections
description: Fluent Support collections via collect() — Laravel Illuminate\Support\Collection parity.
---

Avalon ships two collection types:

| Type | Import | Role |
| --- | --- | --- |
| **Support** | `from avalon.support import collect, Collection` | General list/map fluency |
| **Articulate** | `from avalon.orm import Collection` | Model results — **extends** Support + `load` / `model_keys` |

```python
# app/http/controllers/welcome_controller.py
from avalon.support import collect

collect(["", "Ada", None, "Grace"]).filter().values().all()
# ["Ada", "Grace"]
```

## Keys

Like Laravel, collections are ordered maps. Filtering **preserves keys**. Call
`values()` when you want a reindexed list:

```python
# app/support_demo.py
collect([0, 1, 2]).filter().all()           # {1: 1, 2: 2}
collect([0, 1, 2]).filter().values().all()  # [1, 2]
```

`pop` / `shift` reindex integer keys so list-like collections stay contiguous.

## Construction

```python
# app/support_demo.py
collect([1, 2, 3])
Collection.make({"a": 1})
Collection.times(3)                 # [1, 2, 3]
Collection.times(3, lambda i: i * 10)
Collection.range(3, 1)              # [3, 2, 1]
Collection.wrap("x")                # ["x"]
Collection.unwrap(collect([1]))     # [1]
Collection.from_json('{"a": 1}')
```

## Conversion (Laravel `toArray` / `toJson`)

Avalon uses Python snake_case. Same ideas as Laravel:

| Laravel | Avalon | Notes |
| --- | --- | --- |
| `all()` | `all()` | Underlying list **or** dict (when keys aren’t `0..n-1`) |
| `toArray()` | `to_array()` | Alias of `all()` on Support collections |
| `toJson()` | `to_json(**kwargs)` | `json.dumps` of `to_array()` |
| — | `to_pretty_json()` | Indented JSON (Laravel-style pretty dump) |
| `Collection::fromJson` | `Collection.from_json(...)` | Classmethod |

```python
# app/support_demo.py
collect([1, 2, 3]).to_array()           # [1, 2, 3]
collect({"a": 1}).to_json()             # '{"a": 1}'
collect({"a": 1}).to_pretty_json()

# Articulate model collections also expose to_dict() (serialize each model):
users = await User.query().get()
users.to_dict()                         # [{...}, ...]
users.to_json()                         # JSON of the Support all()/to_array() shape
```

## Common chains

```python
# app/support_demo.py
rows = collect([
    {"name": "Ada", "votes": 10},
    {"name": "Grace", "votes": 5},
])

rows.where("votes", ">", 5).pluck("name").values().all()
rows.sort_by_desc("votes").first()
rows.group_by(lambda row: row["votes"] >= 10)
rows.chunk(2)
rows.partition(lambda row: row["votes"] > 5)
rows.dot()          # flatten nested maps/lists with dotted keys
```

## Method surface

Snake_case mirrors Laravel’s Available Methods. Notable renames / notes:

| Laravel | Avalon |
| --- | --- |
| `toArray` / `toJson` | `to_array` / `to_json` (see Conversion above) |
| `except` | `except_` / `except_keys` (`except` is reserved) |
| `toPrettyJson` | `to_pretty_json` |
| `fromJson` | `from_json` (classmethod) |
| `reduceSpread` | `reduce_spread` |
| `diffAssocUsing` / `intersect*` | same snake_case |
| `dd` / `dump` | skipped (debug theater) |
| `lazy` / `LazyCollection` | deferred |

Transformers return **new** instances. Mutators (`push`, `put`, `pop`, `pull`, `transform`, `splice`, …) match Laravel mutability.

```python
# app/support_demo.py
c = collect([1, 2, 3, 4, 5])
removed = c.splice(1, 2, [9, 8])  # returns [2, 3]; c becomes [1, 9, 8, 4, 5]

collect([1, 2]).multiply(3).all()           # [1, 2, 1, 2, 1, 2]
collect([[1, 2], [3, 4]]).reduce_spread(lambda c, a, b: c + a + b, 0)  # 10
collect({"a": 1}).to_pretty_json()
```

## Macros

```python
# app/support_demo.py
Collection.macro("sum_votes", lambda c: c.sum("votes"))
collect([{"votes": 1}, {"votes": 2}]).sum_votes()  # 3
```

## Articulate

```python
# app/http/controllers/welcome_controller.py
users = await User.query().get()  # avalon.orm.Collection
await users.load("posts")
users.pluck("email").values().all()
```

:::note
`LazyCollection` is deferred until a streaming consumer needs it.
:::

## Related

- [Articulate ORM](/articulate/)
- [Pagination](/database/pagination/)
