---
title: Grail Console
description: Grail commands, Command classes, discovery, and the Fiddle REPL.
---

## Grail

Every Avalon application ships **Grail** — the in-app CLI. With your virtualenv active and Avalon installed, run commands as `grail …`. You can also invoke the root `grail` script with `python grail …`.

```bash
grail list
grail make:command SendDigest
grail inspire
grail fiddle
```

`fiddle` is Avalon’s interactive REPL. Familiar aliases work the same way:

```bash
grail fiddle
grail tinker
grail repl
```

Framework commands (`serve`, `migrate`, `make:*`, …) live on the same surface as discovered app `Command` subclasses.

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

Generate a stub with `grail make:command SendDigest`.

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

`line`, `info`, `comment`, `warn`, `error`, `success`, `table`, `confirm` — typed output helpers on `Command`.

## Discovery

`ConsoleKernel` loads:

1. Framework commands in `avalon.console.commands` (e.g. `inspire`)
2. App package `app.console.commands`
3. Files under `app/console/commands/*.py`

Register extras via the container-bound `ConsoleKernel` if needed. Failed command runs report through the exception `Handler` before exiting.

## Fiddle REPL

`grail fiddle` (or `tinker` / `repl`) boots the application and opens an interactive shell with helpers and models available.

Articulate is **async**. Fiddle auto-resolves coroutine expression results, so these both work:

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

Debug helpers live on the package root:

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

Interactive UI lives in [`avalon.console.prompts`](/prompts/) — `text`, `select`, `confirm`, `spin`, `progress`, and Command helpers `ask` / `choice` / `secret` / `anticipate`.

## Related

- [Prompts](/prompts/)
- [Task Scheduling](/scheduling/)
- [Error Handling](/errors/)
- [Logging](/logging/)
