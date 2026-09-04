---
title: Stacks & Custom Directives
description: "@push, @prepend, @stack, @once, and Engine.directive()."
---

# Stacks & Custom Directives

## Stacks

Push fragments from a child view; flush them in the layout (usually **after**
`@yield` so pushes from sections are visible):

```html
{{-- layout --}}
@yield("content")
@stack("scripts")

{{-- page --}}
@push("scripts")
  <script src="{{ asset('app.js') }}"></script>
@endpush
```

| Directive | Role |
| --- | --- |
| `@push` / `@endpush` | Append to a named stack |
| `@prepend` / `@endprepend` | Prepend to a named stack |
| `@stack("name")` | Render the stack |
| `@once` / `@endonce` | Render the block only once per request |

## Framework stubs

```html
@csrf
@asset("css/app.css")

@error("email")
  <span class="error">{{ message }}</span>
@enderror
```

- `@csrf` emits a hidden `_token` input from `context["csrf_token"]` (empty until sessions land).
- `@error("field")` shows the block when `errors` is a field→messages mapping; `message` is the first error string.
- `@asset(...)` calls the injected `asset()` helper (subpath-aware).

## Custom directives

Register handlers on the engine (or `ViewFactory.directive`). The handler
receives the expression inside the parentheses (or `""`) and returns Python
source lines to emit into the compiled render function:

```python
engine.directive(
    "datetime",
    lambda expr: f"__w(__e(str(__eval({expr!r}))))",
)
```

```html
@datetime(now.isoformat())
```

## Composers, creators, and fragment cache

```python
engine.composer("profile.*", lambda ctx: ctx.setdefault("title", "Profile"))
engine.creator(["dashboard", "dashboard.*"], seed_once)

# In a template:
# @cache("sidebar") ... @endcache
engine.cache_views()  # warm compile cache
engine.clear_cache()  # compiled views + fragments + creators
```
