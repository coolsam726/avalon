---
title: Helpers
description: Arr, Number, data_* helpers, and miscellaneous Support utilities.
---

## Overview

Laravel’s [Helpers](https://laravel.com/docs/helpers) catalog lives under
`avalon.support` — import what you need (Avalon does not pollute the global
namespace).

```python
from avalon.support import Arr, Number, blank, data_get, data_set, optional, retry, tap
```

Surfaces already owned by other packages (`config`, `route`, `auth`, `dispatch`,
`view`, `storage`, …) stay on those packages. This page covers **Arr**,
**Number**, **data_***, and miscellaneous utilities.

## Arrays — `Arr`

```python
from avalon.support import Arr

Arr.get({"user": {"name": "Ada"}}, "user.name")  # "Ada"
Arr.set(payload, "user.role", "admin")
Arr.dot({"a": {"b": 1}})                         # {"a.b": 1}
Arr.only(payload, ["id", "email"])
Arr.pluck(users, "email", "id")
```

Claimed methods include: `accessible`, `add`, `collapse`, `cross_join`,
`divide`, `dot`, `undot`, `except_`, `only`, `exists`, `first`, `last`,
`flatten`, `forget`, `get`, `has`, `has_any`, `is_assoc`, `is_list`, `join`,
`key_by`, `map`, `map_spread`, `map_with_keys`, `pluck`, `prepend`,
`prepend_keys_with`, `pull`, `query`, `random`, `reject`, `set`, `shuffle`,
`sort`, `sort_desc`, `sort_recursive`, `take`, `to_css_classes`,
`to_css_styles`, `where`, `where_not_null`, `wrap`.

## Data helpers

```python
from avalon.support import data_get, data_set, data_fill, data_forget, head, last

data_set(target, "a.b", 1)
data_fill(target, "a.b", 99)   # no-op — already set
data_forget(target, "a.b")
```

## Numbers — `Number`

```python
from avalon.support import Number

Number.format(1000)                 # "1,000"
Number.currency(12.5)               # "$12.50"
Number.percentage(12.345, precision=1)
Number.file_size(2_048)
Number.ordinal(3)                   # "3rd"
Number.spell(21)                    # "twenty-one"
```

## Miscellaneous

| Helper | Role |
| --- | --- |
| `blank` / `filled` | Empty-ish checks |
| `value` | Resolve callables |
| `tap` / `with_` | Pass-through / transform |
| `when` / `transform` | Conditional values |
| `optional` | Null-safe proxy |
| `retry` / `retry_async` | Retry with optional sleep |
| `once` | Memoize a callable on itself |
| `rescue` | Catch → default |
| `throw_if` / `throw_unless` | Conditional raise |
| `abort` / `abort_if` / `abort_unless` | HTTP abort |
| `e` | HTML escape |
| `class_basename` | Trailing class segment |
| `now` / `today` | UTC datetime / date |
| `base_path` / `app_path` / … | Path helpers (cwd-rooted) |

## Related

- [Strings](/strings/) — `Str` / `Stringable`
- [Collections](/collections/) — `collect()`
