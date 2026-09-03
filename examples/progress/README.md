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

Then:

```bash
curl -s http://127.0.0.1:3000/ | python -m json.tool
curl -s http://127.0.0.1:3000/progress | python -m json.tool
```

(`python grail serve` defaults to **3000** and walks **3001–3099** if busy.)

## What this proves today

| Milestone | Visible here |
| --- | --- |
| **M0** | App created with `avalon new`, `python grail serve`, layout |
| **M1** | `Application.bootstrap()`, `config()`, providers, `.env` |
| **M2+** | Listed as `next` / `planned` on `GET /progress` |

## Growing with Avalon

When M2 lands, replace the FastAPI route wiring in `bootstrap/app.py` with Avalon `Route` definitions in `routes/`. Keep `/progress` as the milestone board.

## CLI

```bash
python grail version
python grail serve
```

Create more apps with `avalon new` from the framework install — not with Grail.
