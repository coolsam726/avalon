---
title: CSRF Protection
description: Cross-site request forgery protection arrives with sessions in M7.
---

:::caution[Not shipped yet]
Real CSRF tokens require a **session** store. Avalon reserves the `web` middleware group for session + CSRF (M7). Caliburn already accepts an `@csrf` directive **stub** for templates; it does not mint or verify tokens until M7 wires sessions.
:::

## Planned shape (M7)

- Session-backed token on stateful `web` routes
- Verify mutating requests (`POST` / `PUT` / `PATCH` / `DELETE`)
- Caliburn `@csrf` emits a hidden `_token` field from the live session
- API routes under `routes/api.py` stay **stateless** — no CSRF (token/bearer auth instead)

## Until then

- Do not treat `@csrf` output as security
- Prefer API + bearer tokens for machine clients
- Keep browser forms on `web` routes ready to adopt M7 middleware without restructuring

## Related

- [Session](/session/)
- [Middleware](/middleware/)
- [Caliburn stacks & directives](/caliburn/stacks/)
