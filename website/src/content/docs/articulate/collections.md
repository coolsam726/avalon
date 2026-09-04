---
title: Collections
description: Work with Articulate collections returned from queries.
---

All multi-result sets returned by Articulate are instances of `avalon.orm.Collection`, including results retrieved via the `get` method or accessed via a relationship. The Articulate collection object extends Python list semantics and provides many helpful methods for working with your results.

```python
# app/http/controllers/example_controller.py
from avalon.orm import Collection

users = await User.query().order_by("id").get()
users.first()
users.pluck("email")
users.where("name", "Ada")
users.filter(lambda u: u.votes > 3)
await users.load("posts")
users.to_dict()
```

## Available methods

**Container:** `len`, iterate, index, slice (returns a `Collection`), `bool`, equality with list/`Collection`.

**Access:** `all`, `first`, `last`, `is_empty`, `is_not_empty`, `count`.

**Transform:** `map`, `filter` (truthy if no callback), `reject`, `where`, `where_in`, `first_where`, `pluck` (optional index key → dict), `unique`, `sort_by` / `sort_by_desc`, `group_by`, `key_by`, `chunk`, `take`, `skip`, `each`, `contains`, `sum` / `avg` / `max` / `min`, `push`, `merge`, `reverse`, `values`.

**Models:** `model_keys`, `to_dict`, `load`, `load_missing`.

`where` on a Collection is **in-memory** (`item[key] == value`), not a SQL builder.

## Paginating results

For length-aware and simple pagination, see [Pagination](/database/pagination/).
