---
title: Directory Structure
description: How an Avalon application is organized on disk.
---

The default Avalon application structure provides a sensible starting point for both small and large applications. Feel free to organize your application however you like — Avalon imposes almost no restrictions — but understanding the conventions will help you navigate quickly.

## The root directory

### The `app` directory

The core of your application lives here: HTTP controllers, middleware, models, and service providers.

Avalon uses **PascalCase** for class names and **snake_case** for Python packages and modules:

| Layer | Convention | Example |
| --- | --- | --- |
| Class | PascalCase | `class Post(Model)`, `PostController` |
| Package directories | lowercase | `app/models/`, `app/http/controllers/` |
| Module files | snake_case | `post.py`, `post_controller.py` |
| Imports | dotted snake_case | `from app.models.post import Post` |

Generators follow the same rules. `python grail make:model Post` writes `app/models/post.py` containing `class Post`. Nested namespaces snake-case as well: `Admin/UserController` → `app/http/controllers/admin/user_controller.py`.

### The `bootstrap` directory

Contains `app.py`, where you configure the application and register middleware — similar to Laravel 11's bootstrap file. See [Middleware](/middleware/).

### The `config` directory

All of your application's configuration files live here (`app.py`, `database.py`, `http.py`, and so on). Browse these files to become familiar with the options available to you.

### The `database` directory

Holds your database migrations and seeders. See [Migrations](/database/migrations/) and [Seeding](/database/seeding/).

### The `routes` directory

Route definitions for your application. By convention:

- `routes/web.py` — routes that return HTML
- `routes/api.py` — routes that return JSON
- `routes/console.py` — scheduled tasks (loaded by `grail schedule:run`, not the HTTP kernel)

### The `app/console` directory

Console `Command` classes (`python grail make:command …`). See [Artisan Console](/console/) and [Task Scheduling](/scheduling/).

### The `lang` directory

Translation catalogs for localization (`lang/en/…`, `lang/en.json`, and so on).

### The `grail` script

The entry point for Avalon's command-line interface. Generate code, run migrations, schedule work, and open Fiddle:

```bash
python grail make:controller PostController
python grail migrate
python grail schedule:run
python grail fiddle
python grail serve
```

:::note
Model meta such as `fillable` and `casts` stay as snake_case class attributes — that matches Laravel's attribute names and keeps generated models readable.
:::

