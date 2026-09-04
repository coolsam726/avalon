---
title: Asset Bundling
description: Serve CSS, JS, and images from public/ — Vite stays in starter kits.
---

Avalon serves static files from your application's `public/` directory. Framework core does **not** ship Vite, esbuild, Webpack, or Tailwind — those belong in **starter kits** that emit compiled assets into `public/` (or `public/build/`).

## The `public` directory

Place files under:

```
public/
  css/app.css
  js/app.js
  images/logo.svg
```

`python grail serve` mounts common public folders so browsers can load `/css/app.css`, `/js/app.js`, and `/images/...`.

## Generating asset URLs

Use `asset()` in Python or `@asset` / `asset()` inside Caliburn so `APP_BASE_PATH` is applied:

```python
from avalon.routing import asset

asset("css/app.css")
# → https://example.com/apps/progress/css/app.css  (when APP_BASE_PATH=/apps/progress)
```

```html
<link rel="stylesheet" href="{{ asset('css/app.css') }}">
<script src="@asset('js/app.js')" defer></script>
```

`@asset('…')` is a Caliburn directive equivalent to printing `asset(...)`.

## What about Vite?

Laravel's Asset Bundling chapter centers on Vite. Avalon's equivalent story:

| Concern | Avalon home |
| --- | --- |
| URL helpers + `public/` serving | Framework (shipped) |
| Hot module reload / Tailwind / Alpine / bundling | **Starter kits** (planned) |

Until a kit ships, author plain CSS/JS under `public/` (as the progress example does) or run your own frontend toolchain that writes into `public/`.

## Related

- [URL Generation](/urls/)
- [Views](/views/)
- [Caliburn stacks](/caliburn/stacks/) — `@push` scripts into layouts
