---
title: CSRF Protection
description: Verify mutating web requests with a session-backed CSRF token.
---

Stateful `web` routes mint a CSRF token in the session and reject unsafe methods
when the token is missing or wrong. API routes stay **stateless** — use bearer
tokens instead of CSRF.

## How it works

1. `StartSession` loads the signed (and encrypted) session cookie
2. `VerifyCsrfToken` ensures `_csrf_token` exists and checks mutating requests
3. Caliburn `@csrf` emits a hidden `_token` field from `csrf_token`

Accepted sources for the token:

- Form field `_token` (from `@csrf`)
- Header `X-CSRF-TOKEN`
- Header `X-XSRF-TOKEN`

Mismatch raises **419** (`TokenMismatchError`).

## Caliburn

```html
<!-- resources/views/auth/login.cal.html -->
<form method="post" action="/login">
  @csrf
  <input name="email" type="email">
  <button type="submit">Sign in</button>
</form>
```

`AuthServiceProvider` shares `csrf_token` into every view so `@csrf` works without
manual wiring.

## Middleware group

Register on the `web` stack (scaffold default):

```python
# bootstrap/app.py
middleware.web(
    prepend=["cookies.encrypt", "session.start", "csrf", "auth.start"],
    append=["locale"],
)
```

Do **not** put `csrf` on the `api` group.

## Related

- [Session](/session/)
- [Middleware](/middleware/)
- [Caliburn stacks & directives](/caliburn/stacks/)
