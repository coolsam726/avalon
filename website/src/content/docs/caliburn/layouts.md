---
title: Layouts & Inheritance
description: "Extend layouts with @extends, @section, @yield, and @parent."
---

# Layouts & Inheritance

Caliburn layouts mirror Blade.

## Yielding sections

```html
{{-- layouts/app.cal.html --}}
<html>
  <head>
    <title>@yield("title", "Avalon")</title>
  </head>
  <body>
    @yield("content")
    @stack("scripts")
  </body>
</html>
```

## Extending a layout

```html
{{-- home.cal.html --}}
@extends("layouts.app")

@section("title", "Home")

@section("content")
  <p>Welcome.</p>
  @push("scripts")
    <script src="{{ asset('home.js') }}"></script>
  @endpush
@endsection
```

## `@parent`

When a child overrides a section that an intermediate layout already defined,
`@parent` inserts the parent section’s content:

```html
@section("content")
  @parent
  <p>Extra for this page.</p>
@endsection
```
