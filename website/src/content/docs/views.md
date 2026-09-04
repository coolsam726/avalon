---
title: Views
description: Render HTML with Caliburn from controllers and routes.
---

Views separate your controller from HTML. Avalon's view engine is **Caliburn** — Blade-parity templates compiled to Python (`.cal.html`).

## Creating and returning views

```python
# app/http/controllers/welcome_controller.py
from avalon.caliburn import view


async def index(self):
    return view("welcome", {"title": "Avalon"})
```

Templates live under `resources/views`. Dots map to directories: `view("posts.show")` → `resources/views/posts/show.cal.html`.

```html
<!-- resources/views/welcome.cal.html -->
@extends("layouts.app")

@section("content")
  <h1>{{ title }}</h1>
@endsection
```

## Passing data

The second argument to `view()` is a dict of template data. Helpers such as `url`, `asset`, `e`, and `__` are injected automatically for Caliburn templates.

## Escaping

- `{{ value }}` — HTML-escaped (safe default)
- `{!! value !!}` — raw HTML (only when you trust the content)

## When to use `html()`

[`html()`](/responses/) is for small hand-built fragments or low-level responses. Prefer `view()` for pages, layouts, and components.

## Deep dive

This Basics page is the entry point. Full Caliburn documentation lives in its own section:

- [Caliburn](/caliburn/) — overview
- [Rendering Views](/caliburn/rendering/)
- [Layouts & Inheritance](/caliburn/layouts/)
- [Components & Slots](/caliburn/components/)
- [Control Structures](/caliburn/control/)
- [Including Subviews](/caliburn/includes/)
- [Stacks & Directives](/caliburn/stacks/)

## Related

- [Responses](/responses/)
- [Asset Bundling](/asset-bundling/)
- [URL Generation](/urls/)
