---
title: Artisan Console
description: Grail commands, Command classes, discovery, and the Fiddle REPL.
---

## Grail

Every Avalon app ships a root `grail` script — the in-application CLI (Laravel Artisan class):

```bash
python grail list
python grail make:command SendDigest
python grail inspire
python grail fiddle
```

Framework Typer commands (`serve`, `migrate`, `make:*`, …) live on the same surface as discovered `Command` subclasses.

## Writing commands

```python
# app/console/commands/send_digest.py
from avalon.console import Command

class SendDigest(Command):
    signature = "mail:digest {user?} {--queue=default}"
    description = "Send the daily digest"

    def handle(self) -> int:
        user = self.argument("user") or "everyone"
        self.info(f"Queue={self.option('queue')} → {user}")
        return 0
```

Generate a stub with `python grail make:command SendDigest`.

### Signature tokens

| Token | Meaning |
| --- | --- |
| `{name}` | Required argument |
| `{name?}` | Optional argument |
| `{name=value}` | Optional with default |
| `{tags...}` | Variadic |
| `{--flag}` | Boolean option |
| `{--queue=default}` | Option with default |

### Output helpers

`line`, `info`, `comment`, `warn`, `error`, `success`, `table`, `confirm` — Laravel-shaped wrappers over Typer.

## Discovery

`ConsoleKernel` loads:

1. Framework commands in `avalon.console.commands` (e.g. `inspire`)
2. App package `app.console.commands`
3. Files under `app/console/commands/*.py`

Register extras via the container-bound `ConsoleKernel` if needed. Failed command runs report through the M8 `Handler` before exiting.

## Fiddle REPL

`python grail fiddle` boots the application and opens a Tinker-class shell.

Avalon's ORM is **async**. Fiddle auto-resolves coroutine expression results, so these both work:

```python
User.all()
await User.query().get()
users = run(User.all())   # explicit sync bridge for assignments
```

Results render as **JSON key/value panels** (models, collections, dicts, lists). Helpers:

```python
dump(users)          # pretty dump, continue
dd(users)            # dump and exit Fiddle
to_json(users)       # JSON string
serialize(users)     # plain Python dict/list
```

## `dump()` / `dd()`

Laravel-shaped debug helpers live on the package root:

```python
from avalon import dump, dd

dump(user, request)   # Rich panel(s) in the terminal; execution continues
dd(User.find(1))      # same chrome, then halt
```

| Context | Behavior |
| --- | --- |
| HTTP **web** | Dedicated `dd()` HTML page (CDN-free), status 200 — not reported as an error |
| HTTP **api** | JSON `{dd, caller, values}` |
| Console command | Pretty print, exit code `0` |
| Fiddle | Pretty print, leave the REPL |

`DumpAndDie` is never logged by the exception Handler (`should_report` is false).

In Caliburn views: `@dump(user)` embeds an HTML card; `@dd(user)` halts with the dump page. See [Stacks & Directives](/caliburn/stacks/#debugging).

Shell preference:

1. **IPython** (preferred) — colored prompts, autoawait, coroutine displayhook
2. **ptpython** — if IPython is absent
3. **Rich fallback** — pretty output + tip to install IPython

```bash
pip install 'avalon[fiddle]'
# or, for contributors:
pip install -e '.[dev]'
```

Preloaded names typically include `app`, `config`, `Route`, `url`, `DB`, `Model`, `log`, `run`, and app models such as `User` / `Post` when present.

## Prompts

Interactive UI lives in [`avalon.console.prompts`](/prompts/) — Laravel Prompts-shaped `text`, `select`, `confirm`, `spin`, `progress`, and Command helpers `ask` / `choice` / `secret` / `anticipate`.

## Related

- [Prompts](/prompts/)
- [Task Scheduling](/scheduling/)
- [Error Handling](/errors/)
- [Logging](/logging/)
