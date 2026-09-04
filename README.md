# Avalon

Laravel-inspired Python web framework with Adonis-class DX, built on FastAPI/Starlette.

| Piece | Name |
| --- | --- |
| Framework | Avalon (`avalon`) |
| Create apps | `avalon new` (like `laravel new`) |
| In-app CLI | `python grail …` (like `php artisan …`) |
| View engine | Caliburn (`avalon.caliburn`) — templates use `.cal.html` |

## Canonical plan

**[`docs/PLAN.md`](docs/PLAN.md)** is the binding architecture and milestone document. Follow it strictly unless the plan is deliberately revised.

**[`website/`](website/)** — published documentation for application developers (Astro Starlight). Run `make docs`.

**[`docs/SMOKE.md`](docs/SMOKE.md)** — smoke + regression gates. Coverage **≥ 95%** on the full suite (`make test-cov`).

## Status

**Status:** M5 — ORM complete (Articulate / `avalon.orm`): Active Record `Model` + query builder, relationships, soft deletes, events, migrations, seeders. Living example: [`examples/progress`](examples/progress). Next: **M6 — Caliburn**.

## Quick start (dev)

```bash
cd /path/to/avalon
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
avalon version
python grail version
pytest
```

## Create an application

```bash
avalon new blog
cd blog
python -m venv .venv && source .venv/bin/activate
pip install -e /path/to/avalon   # or pip install avalon once published
pip install -e .
python grail serve
```

## Package layout

```text
src/avalon/
  framework/    # Application, container, boot
  config/       # env + config repository
  providers/    # service providers
  http/         # kernel, request, response, middleware
  routing/      # Route DSL → FastAPI bridge
  validation/   # FormRequest
  translation/  # __(), trans_choice(), Number, SetLocale
  installer/    # avalon new …
  grail/        # python grail …
  orm/          # Model, query builder, migrations
  caliburn/     # later (M6)
  auth/         # later (M7)
grail           # root script → python grail …
```

## License

MIT
