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

**[`docs/SMOKE.md`](docs/SMOKE.md)** — smoke + regression gates. Coverage **≥ 95%** on the full suite (`make test-cov`).

## Status

**M2 — HTTP + routing** complete. Living example: [`examples/progress`](examples/progress). Next: **M3 — Validation + DX**.

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
  installer/    # avalon new …
  grail/        # python grail …
  orm/          # later (M4)
  caliburn/     # later (M5)
  auth/         # later (M6)
grail           # root script → python grail …
```

## License

MIT
