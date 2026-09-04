---
title: Relationships
description: Define and eager-load Articulate relationships.
---

Database tables are often related to one another. For example, a blog post may have many comments, or an order may belong to a user. Articulate makes managing and working with these relationships easy.

Declare relationships with `@relation`. Calling the method (`user.posts()`) returns the relation object so you can keep querying. Reading the attribute (`user.posts`) returns **already loaded** data only.

```python
from avalon.orm import Model, relation, RelationNotLoadedError

class User(Model):
    @relation
    def posts(self):
        return self.has_many(Post)

    @relation
    def roles(self):
        return self.belongs_to_many(Role).with_pivot("level")

# Query through the relationship
posts = await user.posts().where("published", True).get()

# Unloaded attribute access does not hit the database
try:
    len(user.posts)
except RelationNotLoadedError:
    pass

# Opt-in awaitable lazy load (explicit await — still no silent IO)
class LazyUser(User):
    lazy_relations = True

user = await LazyUser.find(1)
posts = await user.posts
```

:::caution
By default Avalon does **not** lazy-load on attribute access. A hidden query there is how N+1 problems start. Eager-load with `with_`, query with `await user.posts().get()`, or set `lazy_relations = True` and use `await user.posts`.
:::


## Defining relationships

| Method | Laravel equivalent |
| --- | --- |
| `has_one` / `has_many` | HasOne / HasMany |
| `belongs_to` | BelongsTo (`associate` / `dissociate`) |
| `belongs_to_many` | BelongsToMany + pivot |
| `has_one_through` / `has_many_through` | HasOneThrough / HasManyThrough |
| `morph_one` / `morph_many` | MorphOne / MorphMany |
| `morph_to(name, types={…})` | MorphTo — pass the type map |
| `morph_to_many` / `morphed_by_many` | Polymorphic many-to-many |

Has-many helpers: `create`, `save`, `save_many`, `create_many`, `first_or_create`.

Belongs-to-many: `attach`, `detach`, `sync`, `toggle`, `update_existing_pivot`, `where_pivot`, `with_pivot`.

## Eager loading

```python
posts = await Post.query().with_("author").get()
posts[0].author.name

users = await User.query().with_(
    "posts",
    notes=lambda q: q.where("published", True),
).get()

await User.query().with_("posts.comments").get()
await User.query().with_count("posts").get()
user._extra["posts_count"]

await user.load("posts")
await user.load_missing("profile")
await users.load("posts")   # Collection
```

### Querying relationship existence

```python
await User.query().has("posts", ">=", 2).get()
await User.query().doesnt_have("posts").get()
await User.query().where_has(
    "posts", lambda q: q.where("published", True)
).get()
await User.query().where_doesnt_have("posts").get()
```

## Soft deletes on related models

When a related model uses soft deletes, put the mixin **before** `Model` so the global scope registers correctly:

```python
class Post(SoftDeletes, Model):
    ...
```
