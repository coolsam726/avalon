---
title: Session
description: Signed cookie sessions for stateful web routes.
---

Avalon ships a **cookie session** driver for the `web` middleware group: a signed
JSON bag in `avalon_session`, wrapped by `EncryptCookies`. The `api` group stays
stateless (no session cookie).

## Web stack

```python
# bootstrap/app.py
from avalon.session import EncryptCookies, StartSession, VerifyCsrfToken
from avalon.auth.middleware import StartAuth

middleware.alias({
    "cookies.encrypt": EncryptCookies,
    "session.start": StartSession,
    "csrf": VerifyCsrfToken,
    "auth.start": StartAuth,
})
middleware.web(
    prepend=["cookies.encrypt", "session.start", "csrf", "auth.start"],
)
```

Order matters: decrypt cookies → start session → CSRF → hydrate auth.

## Request API

```python
# app/http/controllers/welcome_controller.py
request.session.put("locale", "fr")
request.session.get("locale")
request.session.flash("status", "Saved.")
request.session.forget("draft")
```

Flash values survive one redirect, then age out on the next request.

## Config

`config/session.py` (and `APP_KEY` in `config/app.py`):

| Key | Default | Role |
| --- | --- | --- |
| `session.cookie` | `avalon_session` | Cookie name |
| `session.lifetime` | `120` | Minutes |
| `session.path` | `/` | Cookie path |
| `session.secure` | `false` | HTTPS-only |
| `app.key` | — | HMAC + cookie encryption secret |

## Locale

`SetLocale` reads `session["locale"]` when present (after `StartSession`), then
falls back to `Accept-Language` / `APP_LOCALE`.

## Related

- [CSRF Protection](/csrf/)
- [Middleware](/middleware/)
- [Routing](/routing/)
