---
title: Seeding
description: Seed your database with test data using Avalon seeders.
---

Avalon includes a simple method of seeding your database with test data using seed classes. All seeders live in `database/seeders`.

:::note
Model factories are not available yet. Seed with `Model.create` / the query builder until factories ship.
:::


## Writing seeders

```
database/
  seeders/
    __init__.py
    database_seeder.py   # DatabaseSeeder — default entry point
    user_seeder.py
```

`avalon new` ships an empty `DatabaseSeeder`. Override `run` and call child seeders:

```python
from avalon.orm import Seeder
from database.seeders.user_seeder import UserSeeder

class DatabaseSeeder(Seeder):
    async def run(self) -> None:
        await self.call([UserSeeder])
        # await self.call_once(UserSeeder)
        # await self.call_with(UserSeeder, {"count": 10})
        # await self.call_silent([UserSeeder])
```

```python
class UserSeeder(Seeder):
    async def run(self, count: int = 1) -> None:
        from app.models.user import User

        for i in range(count):
            await User.create(email=f"u{i}@example.com", name=f"User {i}")
```

## Suppressing model events

```python
from avalon.orm import Seeder, WithoutModelEvents

class QuietSeeder(WithoutModelEvents, Seeder):
    async def run(self) -> None:
        await User.create(email="quiet@example.com", name="Quiet")
```

You may also wrap a block with `without_model_events()`.

## Running seeders

```bash
python grail make:seeder UserSeeder
python grail db:seed
python grail db:seed --class UserSeeder
python grail migrate --seed
python grail migrate --seed --seeder UserSeeder
python grail migrate:fresh --seed
```

`--seeder` implies seeding (you may omit `--seed` when `--seeder` is set). The default class is `DatabaseSeeder`.
