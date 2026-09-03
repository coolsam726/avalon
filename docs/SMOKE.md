# Smoke & Regression

> Binding architecture: [`PLAN.md`](PLAN.md).  
> Coverage gate: **≥ 95%** on the **full** suite (CI `test` job).  
> Complete the milestone smoke gate before advancing.

## Commands

| Command | What it does |
| --- | --- |
| `make smoke` / `pytest -q tests/smoke` | Smoke gate only — **no coverage** (clean exit) |
| `make regression` / `pytest -q -m regression` | Smoke + locked public contracts |
| `make test` / `pytest -q` | Full unit + smoke (no coverage) |
| `make test-cov` | Full suite with **coverage fail-under 95%** |

```bash
pip install -e ".[dev]"
make smoke
make regression
make test-cov
```

## Anti-regression measures

1. **Smoke suite** (`@pytest.mark.smoke`) — end-to-end developer path for M0/M1  
2. **Contract suite** (`tests/regression/`, `@pytest.mark.regression`) — locks public exports, bootstrap lifecycle, scaffold files, IoC autowire, `.env` override  
3. **CI jobs (all required conceptually):**
   - `Smoke (regression gate)` — `pytest tests/smoke`
   - `Regression contracts` — `pytest -m regression`
   - `Unit + coverage ≥95%` — full suite with `pytest-cov`
4. **Do not remove or weaken** a regression test to green CI — fix the product or consciously revise [`PLAN.md`](PLAN.md) + this doc

Markers are declared in `pyproject.toml` under `[tool.pytest.ini_options]`.

---

## M0 — Skeleton

Automated: `tests/smoke/test_m0_smoke.py`

| ID | Check | Expected |
| --- | --- | --- |
| S1 | `avalon version` | Exit 0, `Avalon 0.1.0` |
| S2 | `avalon new <app>` | Tree with `grail`, `bootstrap/app.py`, controllers |
| S3 | Invalid name / non-empty dir | Non-zero exit |
| S4 | `GET /` on generated ASGI | `200` + Welcome JSON |
| S5 | Grail `version` | Exit 0 |
| S6 | `serve` without bootstrap | Exit 1 |
| S7 | `serve` with scaffold | Calls Uvicorn `bootstrap.app:asgi` |

### Manual (once per M0 cut)

```bash
avalon new smoke_blog --path /tmp
cd /tmp/smoke_blog
pip install -e /path/to/avalon && pip install -e .
python grail serve
curl -s http://127.0.0.1:3000/
rm -rf /tmp/smoke_blog
```

(`serve` starts at **3000** and tries the next free port through **3099** if needed.)

---

## M1 — Application kernel

Automated: `tests/smoke/test_m1_smoke.py` + `tests/regression/test_m1_contracts.py`

| ID | Check | Expected |
| --- | --- | --- |
| K1 | Scaffold + `Application(...).bootstrap()` | `is_booted`, `config("app.name")` |
| K2 | Import `bootstrap.app` | Kernel bootstrapped; `GET /` includes config `app` name |
| R1 | Public exports | `Application`, `Container`, `config`, `env`, providers stable |
| R2 | Bootstrap idempotent | Double `bootstrap()` safe |
| R3 | Scaffold contract | `.env`, providers, `Application(...).bootstrap()` in bootstrap |
| R4 | Container autowire | Constructor injection + `ResolutionError` |
| R5 | `.env` override | App `.env` overrides stale process env |

### Manual (once per M1 cut)

```bash
avalon new kernel_blog --path /tmp
cd /tmp/kernel_blog
pip install -e /path/to/avalon && pip install -e .
python -c "from avalon.framework import Application; a=Application('.').bootstrap(); print(a.config.get('app.name'), a.is_booted)"
python grail serve
curl -s http://127.0.0.1:3000/
```

### M1 exit criteria

- [ ] `make smoke` green
- [ ] `make regression` green
- [ ] `make test-cov` green (coverage ≥ 95%)
- [ ] Manual M1 checks once locally
- [ ] No M2 routing work until this gate passes

---

## Out of scope until later milestones

- Routing DSL / middleware (M2)
- FormRequest (M3)
- ORM, Caliburn, Auth (M4+)
