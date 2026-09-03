# Progress — Avalon living example

Tracks framework milestones as Avalon grows. Update controllers/`/progress` when a milestone lands.

Canonical plan: [`../../docs/PLAN.md`](../../docs/PLAN.md)

## Run (from monorepo)

```bash
cd /path/to/avalon
source .venv/bin/activate          # framework venv is fine
pip install -e .                   # ensure avalon is editable

cd examples/progress
pip install -e .                   # installs this app package
python grail serve
```

Then open another terminal and run the M2 checklist below (use the port `grail serve` prints if not 3000).

## M2 manual checklist

```bash
BASE=http://127.0.0.1:3000

# Board + welcome
curl -s "$BASE/" | python -m json.tool
curl -s "$BASE/progress" | python -m json.tool

# Group prefix + middleware header (expect X-Avalon-Demo: m2)
curl -si "$BASE/demo/ping" | head -n 20

# Path params, query, bearer, only()
curl -s "$BASE/demo/items/42?q=hello" -H "Authorization: Bearer secret" | python -m json.tool

# Request bag (all/query/post — body wins on key clashes)
curl -s -X POST "$BASE/demo/bag?q=1" -H "Content-Type: application/json" \
  -d '{"name":"bag","q":"body"}' | python -m json.tool

# Container DI into controller action
curl -s "$BASE/demo/di" | python -m json.tool

# Verbs
curl -s -X POST "$BASE/demo/items" -H "Content-Type: application/json" \
  -d '{"name":"avalon","flag":true,"count":2}' | python -m json.tool
curl -s -X PUT "$BASE/demo/items/42" | python -m json.tool
curl -s -X PATCH "$BASE/demo/items/42" | python -m json.tool
curl -s -X DELETE "$BASE/demo/items/42" | python -m json.tool
curl -s -X OPTIONS "$BASE/demo/probe" | python -m json.tool

# Validation-shaped HttpException (422)
curl -s -X POST "$BASE/demo/items" -H "Content-Type: application/json" -d '{}' | python -m json.tool

# HttpException JSON shape
curl -s "$BASE/demo/boom" | python -m json.tool
curl -s "$BASE/demo/missing" | python -m json.tool

# Second routes file (routes/api.py) + match()
curl -si "$BASE/api/health" | head -n 20
curl -s "$BASE/api/echo/7?q=api" | python -m json.tool
```

## What this proves today

| Milestone | Visible here |
| --- | --- |
| **M0** | App created with `avalon new`, `python grail serve`, layout |
| **M1** | `Application.bootstrap()`, `config()`, providers, `.env` |
| **M2** | Route DSL, middleware, verbs, **Request bag** (`all`/`query`/`post`/`only`/`except_`), container DI, `HttpException` — `/demo/*`, `/api/*` |

## Growing with Avalon

M2 Request parity is live: routes in `routes/web.py` + `routes/api.py`, middleware alias `demo.tag`, Laravel-style `Request` helpers, bootstrap only exposes `application.asgi` (no FastAPI imports). FormRequest + `python grail make:*` wait for M3.

## CLI

```bash
python grail version
python grail serve
```

Create more apps with `avalon new` from the framework install — not with Grail.
