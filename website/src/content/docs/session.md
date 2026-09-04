---
title: Session
description: HTTP sessions ship with authentication in M7.
---

:::caution[Not shipped yet]
Avalon does not yet provide a session driver. Session start, cookie encryption, and flash data are part of **M7** (`avalon.auth` + the `web` middleware group).
:::

## Planned shape (M7)

- Session store for stateful `web` routes
- Encrypted/signed cookies
- Flash / old input (as the auth and validation stories need them)
- Locale persistence for `web` (M4 already supports `Accept-Language` and explicit `set_locale()`)

## Until then

- Treat `web` as the **HTML polarity** surface (and the future home of session middleware)
- Keep API routes under `api` for stateless JSON clients

## Related

- [CSRF Protection](/csrf/)
- [Middleware](/middleware/)
- [Routing](/routing/)
