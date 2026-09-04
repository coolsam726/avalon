---
title: Caliburn
description: Avalon's featherweight Blade-parity view engine for Python.
---

# Caliburn

Caliburn is Avalon's view engine — a **new templating system for Python** with
Laravel Blade's mental model: layouts, components, slots, and directives,
compiled ahead of time for a thin render path.

Templates use the **`.cal.html`** extension and live under `resources/views`.

```python
# app/http/controllers/welcome_controller.py
from avalon.caliburn import view

return view("welcome", {"name": "Artisan"})
```

```html
<!-- resources/views/welcome.cal.html -->
@extends("layouts.app")

@section("content")
  <h1>Hello, {{ name }}</h1>
@endsection
```

:::tip[Full Blade parity]
M6 exhausts Blade's app-facing surface — inheritance, control flow, components
& slots, stacks, localization directives, and custom `@directive`s — not a
minimal subset. This section grows as each surface ships.
:::

## In this section

- [Rendering Views](/caliburn/rendering/) — `view()`, data, escaping
- [Layouts & Inheritance](/caliburn/layouts/) — `@extends`, `@section`, `@yield`
- [Components & Slots](/caliburn/components/) — `<x-*>`, `@slot`, attributes
- [Control Structures](/caliburn/control/) — `@if`, `@foreach`, `@python`
- [Including Subviews](/caliburn/includes/) — `@include` and friends
- [Stacks & Directives](/caliburn/stacks/) — `@push`, `@stack`, custom directives
