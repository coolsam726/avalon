# Avalon — Canonical Plan

> **Status:** Binding. This document is the source of truth for architecture and milestones.
> Change it deliberately (PR / explicit decision), not casually mid-implementation.
> Last aligned: 2026-09-03 (M1 Application kernel complete).

## Working identity

- **Project / repo / distribution:** `avalon` (PyPI: `avalon`)
- **Import root:** `avalon` with intentional **subpackages**
- **CLIs (Laravel parallel):**
  - **`avalon new <app>`** — installer / project creator (like `laravel new`) — `avalon.installer`
  - **`python grail …`** — in-app commands via a root `grail` script (like `php artisan …`) — `avalon.grail`
  - Do **not** use Grail for project creation; do **not** use `avalon` for day-to-day app commands
- **HTTP engine:** FastAPI on Starlette (ASGI) — hidden behind Avalon’s programming model, with an escape hatch to the underlying FastAPI app for advanced cases
- **Validation / OpenAPI:** Pydantic v2 via Form Request–style classes
- **Views:** **Caliburn** (`avalon.caliburn`) — Blade-familiar syntax, featherweight render path, templates as **`.cal.html`**
- **Theme:** Arthurian naming for products/tools (`grail`, `Caliburn`); keep public APIs Laravel-familiar (`Route`, `Controller`, `Middleware`, `config()`, `@extends`)

## Design picture (target DX)

Developers create apps with `avalon new`, then run `python grail …` inside the app (controllers, providers, `routes/`, `config/`). Avalon boots a service container, registers providers, compiles routes into FastAPI, and serves via Uvicorn. FastAPI/Starlette remain implementation details of the HTTP kernel. Views compile Caliburn templates (`.cal.html`) to fast Python callables.

```mermaid
flowchart LR
  subgraph appDev [App_code]
    Routes[routes/*.py]
    Controllers[Controllers]
    Providers[Providers]
    Models[Models]
    CalTemplates[cal.html_templates]
  end

  subgraph avalonPkg [avalon]
    Installer[avalon_new_CLI]
    Grail[python_grail_CLI]
    Framework[avalon.framework]
    Http[avalon.http]
    Routing[avalon.routing]
    ProvidersPkg[avalon.providers]
    Orm[avalon.orm]
    Caliburn[avalon.caliburn]
  end

  subgraph engine [Engine]
    FastAPI[FastAPI]
    SA[SQLAlchemy_2]
  end

  Installer -.->|scaffolds_app_with_grail_script| Grail
  Grail --> Framework
  ProvidersPkg --> Framework
  Routes --> Routing
  Routing --> Http
  Http --> FastAPI
  Controllers --> Framework
  Models --> Orm
  Orm --> SA
  CalTemplates --> Caliburn
  Http --> Caliburn
```

## Package layout

```text
avalon/
  pyproject.toml
  src/avalon/
    framework/                 # Application, container, boot lifecycle
    config/                    # config repository, env
    providers/                 # core service providers + Provider base
    http/                      # kernel, request, response, middleware, controllers
    routing/                   # Route DSL → FastAPI bridge
    validation/                # FormRequest
    grail/                     # in-app CLI (python grail …)
    installer/                 # avalon new …
    orm/                       # M4
    caliburn/                  # M5 — optional for API apps
    auth/                      # M6
  tests/
  examples/
  docs/
```

**Import examples:**

- `from avalon.framework import Application`
- `from avalon.routing import Route`
- `from avalon.http import Controller, Middleware`
- `from avalon.providers import ServiceProvider`
- `from avalon.validation import FormRequest`
- later: `from avalon.orm import Model`
- later: `from avalon.caliburn import ViewFactory`

### Subpackage boundaries

| Subpackage | Responsibility |
| --- | --- |
| `avalon.framework` | Application, IoC container, boot |
| `avalon.config` | `.env`, config files, `config()` |
| `avalon.providers` | Provider base + framework providers |
| `avalon.http` | Kernel, request/response, middleware, base controller |
| `avalon.routing` | Route definitions, groups, compiling onto FastAPI |
| `avalon.validation` | FormRequest / validation errors |
| `avalon.grail` | In-app CLI (`python grail …`) |
| `avalon.installer` | Installer CLI (`avalon new`) |
| `avalon.orm` | Eloquent-like ORM (M4) |
| `avalon.caliburn` | Caliburn compiler/runtime (M5) |
| `avalon.auth` | Guards, middleware (M6) |

## Ecosystem growth

Start as **one installable `avalon`**. When Caliburn, kits, or queues get large:

1. **Same repo, optional extras** — e.g. `pip install avalon[caliburn]`, or
2. **Monorepo of distributions** still under the `avalon.*` namespace, plus starter-kit packages

Do **not** rename the project to `avalon_framework`. “Framework” is the `avalon.framework` subpackage.

**Rules:**

- Core happy path must not require Caliburn; API apps never import `avalon.caliburn`
- `avalon.caliburn` stays framework-light and dependency-thin; integrate via a view provider
- Starter kits and heavy subsystems stay out of the default import surface
- App code uses `avalon.*` only — no FastAPI imports on the happy path

## Decision: ORM (Eloquent-like)

**Chosen approach:** Eloquent-shaped **Active Record + Query Builder API** as `avalon.orm`, façade over **SQLAlchemy 2.0 (async-first)**.

**Public DX targets:**

- `User.query().where("email", email).first()`
- `Post.query().with_("author", "comments").find(1)`
- `user.posts().where("published", True).get()`
- model events, casts, soft deletes, scopes
- migrations via Alembic under `python grail migrate` UX

**Internal rule:** App code depends on `avalon.orm`, not SQLAlchemy — except documented escape hatches.

## Decision: Views — Caliburn

| Item | Choice |
| --- | --- |
| Product name | Caliburn |
| Package | `avalon.caliburn` |
| Template extension | **`.cal.html`** |
| Inline code | **`@python` / `@endpython` only** (no freeform Python embedding) |
| DX north star | Blade-familiar directives (Edge-style iteration) |
| Performance north star | **Featherweight** — first-class constraint |

Logic belongs in controllers, view models, and composers. `@python` is an escape hatch, not the default style.

### Performance principles (non-negotiable)

- **Compile ahead, render thin** — no re-lex/parse on the request path
- **Aggressive compiled-cache** — mtime invalidate in dev; warm cache in prod
- **Minimal runtime** — thin dependency graph on the hot path
- **Zero-cost unused features**
- **Benchmark from MVP** — echo, layout+sections, foreach; regression guards
- **Compare honestly** — Caliburn vs Jinja2 on shared fixtures

### Iteration ladder

1. **MVP:** `{{ }}`, `{!! !!}`, `@extends` / `@section` / `@yield`, `@include`, `{{-- --}}`
2. **Control flow:** `@if`, `@unless`, `@foreach`, `@forelse`, `@for`, `@while`, `@python`
3. **Components:** `@component` / `<x-*>`, slots, attributes
4. **Framework directives:** `@csrf`, `@auth`, `@guest`, `@error`, asset helpers
5. **Advanced:** composers, creators, fragment caching, custom `@directive`

## Decision: Scope discipline

Bite-sized milestones. **No** queues, notifications, scheduler, mail, or seeders until the core path is boring and tested. Seeders follow ORM maturity. Caliburn is its own track after the core gate.

## Milestones

### M0 — Skeleton — **complete**

- Repo/project `avalon`, installable distribution `avalon`
- Subpackage stubs: `framework`, `config`, `providers`, `http`, `routing`, `validation`, `grail`, `installer`, plus placeholders for `orm`, `caliburn`, `auth`
- Root `grail` script: `python grail version` works
- **`avalon new <name>`** scaffolds a Laravel-like app tree (incl. root `grail`, `bootstrap/app.py`, controllers, routes, config)
- **`python grail serve`** runs Uvicorn against `bootstrap.app:asgi` (M0 minimal FastAPI entry; Avalon HTTP kernel replaces this in M2)
- pytest harness + GitHub Actions CI (Python 3.11–3.13)
- Smoke plan: [`docs/SMOKE.md`](SMOKE.md); automated suite under `tests/smoke/`
- Coverage gate: **≥ 95%** (`pytest-cov`, enforced in CI; raise later)

### M1 — Application kernel — **complete**

- `Application.bootstrap()`: env → config → register providers → boot
- `.env` loader (`load_environment` / `env()`) and `ConfigRepository` + `config()`
- Service container: bind / singleton / instance / alias / resolve / `make` / constructor autowiring
- `ServiceProvider` + `FoundationServiceProvider`; `app.providers` from `config/app.py`
- Scaffolded apps boot the kernel from `bootstrap/app.py`
- Living example: [`examples/progress`](../examples/progress) (milestone board at `/progress`)
- Smoke: [`docs/SMOKE.md`](SMOKE.md) M1 section + `tests/smoke/test_m1_smoke.py`

### M2 — HTTP + routing

- Router DSL: `Route.get/post/...`, groups, prefixes, middleware aliases
- Controllers (async); container-resolved
- Middleware pipeline
- Compile Avalon routes into FastAPI
- Request/Response wrappers; consistent JSON error shape

### M3 — Validation + DX

- `FormRequest` (Pydantic) with Laravel-ish failure messages
- Exception handler / HTTP exceptions
- `python grail make:controller`, `make:middleware`, `make:provider`, `make:request`
- Example API app proving the loop

**Gate:** Example boots, routes, injects, validates, responds — no FastAPI imports in app code.

### M4 — `avalon.orm`

- Model base, query builder, CRUD, relationships, scopes, casts
- SQLAlchemy 2 async via provider
- `python grail make:model`, migrate commands
- Soft deletes + model events (subset)

### M5 — Caliburn (`avalon.caliburn`)

- MVP: `.cal.html`, layouts + echo + include, compile-to-Python + cache
- Wire `view()` via provider; optional extra `avalon[caliburn]`
- Benchmark suite from day one; continue parity ladder without blocking auth

### M6 — `avalon.auth`

- Session + token guards
- Middleware `auth`, `guest`

### Later (deferred)

- Queues / jobs, mail, notifications, scheduler
- Seeders/factories
- Policies/gates, broadcasting
- Starter kits
- Full Caliburn advanced parity (ongoing on M5 track)

## Quality bar for “solid core”

- Type hints + tests per subpackage boundary
- Canonical `examples/api` updated every core milestone
- Docs per milestone: mental model + FastAPI mapping under the hood
- Stable `avalon.*` imports; no Starlette/FastAPI types in happy-path app code
- Caliburn: golden fixtures + render benchmarks with regression guards
- **Coverage ≥ 95%** on `avalon` (CI fail-under on full suite; smoke runs without coverage)
- Milestone smoke + regression contracts (see [`SMOKE.md`](SMOKE.md)); `make smoke` / `make regression` / `make test-cov`

## Next implementation focus

**M2 only** — HTTP + routing (`avalon.http` + `avalon.routing`). M0 and M1 are closed.
