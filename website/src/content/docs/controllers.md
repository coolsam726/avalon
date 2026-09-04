---
title: Controllers
description: Organize request handling into controller classes.
---

Instead of defining all route logic as closures, you may organize related actions into controller classes under `app/http/controllers`.

## Basic controllers

```python
from avalon.http import Controller
from avalon.caliburn import view


class WelcomeController(Controller):
    async def index(self):
        return view("welcome", {"title": "Avalon"})
```

Wire the action in a route file:

```python
Route.get("/", [WelcomeController, "index"])
```

Generate a stub:

```bash
python grail make:controller PostController
```

Nested namespaces work (`python grail make:controller Admin/UserController`) and create `__init__.py` files as needed.

## Dependency injection

Constructor and method dependencies are resolved from the application container:

```python
from avalon.config import ConfigRepository
from avalon.http import Controller, Request


class DemoController(Controller):
    def __init__(self, config: ConfigRepository) -> None:
        self.config = config

    async def with_config(self, request: Request) -> dict:
        return {"app": self.config.get("app.name")}
```

Type-hint `Request` or a [`FormRequest`](/validation/) subclass to receive the current request (validated when using FormRequest).

## Single-action style

Prefer one public `index` / `store` / `show` method per intent. Avalon does not require invokable `__call__` controllers — use an explicitly named method on the route.

## Related

- [Routing](/routing/)
- [Requests](/requests/)
- [Validation](/validation/)
- [Views](/views/)
