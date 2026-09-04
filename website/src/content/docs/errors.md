---
title: Error Handling
description: How Avalon turns exceptions into HTTP responses today — and what M8 adds.
---

## Today (M2 floor)

Unhandled `HttpException` subclasses are converted **inside** the middleware pipeline so route middleware can still decorate the response.

API (and JSON) clients receive the locked envelope:

```json
{
  "message": "Not found.",
  "status": 404,
  "errors": null
}
```

Common types from `avalon.http.exceptions`:

| Class | Status |
| --- | --- |
| `BadRequestHttpException` | 400 |
| `UnauthorizedHttpException` | 401 |
| `ForbiddenHttpException` | 403 |
| `NotFoundHttpException` | 404 |
| `MethodNotAllowedHttpException` | 405 |
| `UnprocessableEntityHttpException` | 422 |
| `TooManyRequestsHttpException` | 429 |

Validation uses `ValidationException` (422 with `errors`). Authorization failures on FormRequest use **403**.

```python
from avalon.http.exceptions import NotFoundHttpException

raise NotFoundHttpException("Post not found.")
```

Web routes may still see a minimal HTML body for some failures until the full handler layer lands.

## Coming in M8

Milestone **M8** adds a real exception **Handler**:

- `report()` / `render()` split, `dont_report`, hooks
- Polarity-aware pages: HTML for `web`, JSON envelope for `api`
- `APP_DEBUG` debug page with traceback context
- `resources/views/errors/{status}.cal.html` overrides
- Logging integration (see [Logging](/logging/))

Do not treat today's conversion as a finished Laravel-parity error stack — it is the safe floor the later handler extends without breaking the JSON contract.

## Related

- [Validation](/validation/)
- [Responses](/responses/)
- [Logging](/logging/)
