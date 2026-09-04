---
title: Authentication
description: Guards, providers, attempt(), remember-me, events, and protecting routes.
---

Avalon authentication mirrors Laravel’s mental model: **guards** decide how a
request is authenticated, **providers** retrieve users, and `auth()` is the
request-scoped manager.

Session/CSRF for browsers live on the `web` group; the `api` group stays
stateless and uses the token guard (bearer / `api_token`).

## Config

Scaffolded by `avalon new`:

```python
# config/auth.py
config = {
    "defaults": {"guard": "web", "passwords": "users"},
    "guards": {
        "web": {"driver": "session", "provider": "users"},
        "api": {"driver": "token", "provider": "users"},
    },
    "providers": {
        "users": {
            "driver": "articulate",
            "model": "app.models.user.User",
        },
    },
    "password_timeout": 10800,
}
```

## Retrieving the user

```python
# app/http/controllers/auth_controller.py
from avalon.auth import auth

user = auth().user()
auth().check()
auth().guest()
auth().id()
auth().guard("api").user()

# Laravel $request->user()
request.user()
request.user("api")
```

Caliburn `@auth` / `@guest` read `auth_user` / `__authenticated` shared by
`AuthServiceProvider`.

## Attempt login

```python
# app/http/controllers/auth_controller.py
ok = await auth().attempt(
    {"email": email, "password": password},
    remember=True,
)
if not ok:
    # auth.failed translation
    ...
await auth().logout()
```

With `remember=True`, Avalon rotates the user’s `remember_token` and queues a
long-lived `remember_{guard}` cookie (`{id}|{token}`). `EncryptCookies` encrypts
it; `StartAuth` hydrates the session from that cookie when no login payload
exists. Logout clears the cookie and nulls the token.

Passwords are verified with [`Hash`](/hashing/). On success, Avalon rehashes when
`Hash.needs_rehash` says the work factor changed.

Failed and successful attempts dispatch auth events (`Attempting`, `Validated`,
`Login`, `Failed`, `Logout`, …) — listen with `avalon.auth.listen`.

## Intended URL

Unauthenticated browser hits on `auth` middleware store `url.intended` in the
session and redirect to `/login`. After `attempt()`, redirect with
`pull_intended_url("/")`.

## Protecting routes

```python
# routes/web.py
Route.get("/settings", [SettingsController, "edit"], middleware=["auth"])
Route.get("/login", [AuthController, "show"], middleware=["guest"])
Route.get("/admin", ..., middleware=["auth:web"])
Route.get("/api/me", ..., middleware=["auth:api"])
```

| Alias | Role |
| --- | --- |
| `auth` / `auth:guard` | Require authentication |
| `guest` | Redirect if already authenticated |
| `password.confirm` | Require recent password confirmation |
| `auth.basic` | HTTP Basic (`email` + password by default) |

Unauthenticated JSON/API clients receive **401**; browser `web` routes redirect
to `/login`. Unknown bearer tokens do **not** invent a guest identity — only a
provider hit authenticates the `api` guard.

## viaRequest

```python
# app/http/controllers/auth_controller.py
from avalon.auth import auth

auth().via_request("custom", lambda request: lookup(request))
```

## User model

```python
# app/models/user.py
from avalon.auth import AuthenticatableMixin
from avalon.orm import Model

class User(AuthenticatableMixin, Model):
    fillable = ("email", "name", "password", "remember_token", "api_token")
    hidden = ("password", "remember_token")
```

## Related

- [Hashing](/hashing/)
- [Passwords](/passwords/)
- [Session](/session/)
- [CSRF Protection](/csrf/)
