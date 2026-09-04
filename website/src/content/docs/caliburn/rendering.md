---
title: Rendering Views
description: Render Caliburn templates with view() and escaped echo.
---

# Rendering Views

```python
from avalon.caliburn import view

return view("greeting", {"name": user.name})
```

| Syntax | Meaning |
| --- | --- |
| `{{ value }}` | HTML-escaped echo (default, safe) |
| `{!! value !!}` | Raw HTML (explicit trust) |
| `{{-- comment --}}` | Compile-time comment |

Helpers available in every template: `config()`, `url()`, `asset()`, `e()`.

More examples land as the engine grows — see [Layouts](/caliburn/layouts/).
