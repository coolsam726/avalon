---
title: Prompts
description: Beautiful interactive console prompts — Laravel Prompts for Avalon.
---

## Introduction

Avalon Prompts add Laravel Prompts-shaped interaction to Grail commands: styled text fields, arrow-key selects, confirmations, spinners, and progress bars.

```python
from avalon.console.prompts import text, select, confirm, spin, progress, intro, outro

intro("Create a user")
name = text("Name", required=True, placeholder="Ada Lovelace")
role = select("Role", ["admin", "editor", "viewer"], default="viewer")
if confirm("Proceed?", default=True):
    spin(lambda: create_user(name, role), "Creating…")
outro("Done")
```

Inside a `Command`, use the Laravel-familiar helpers:

```python
name = self.ask("Name", default="Sam")
role = self.choice("Role", ["admin", "user"])
secret = self.secret("API token")
ok = self.confirm("Continue?", default=True)
city = self.anticipate("City", ["Nairobi", "Mombasa"])
```

## Available prompts

| Helper | Purpose |
| --- | --- |
| `text` / `textarea` / `password` / `number` | Free-form input |
| `confirm` / `pause` | Yes/No and continue |
| `select` / `multiselect` | Arrow-key lists (space toggles multi) |
| `suggest` / `search` | Autocomplete / type-to-filter |
| `note` / `info` / `warning` / `error` / `alert` | Styled panels |
| `intro` / `outro` | Section bookends |
| `table` / `clear` | Rich table + clear screen |
| `spin` / `progress` | Busy UI |

### Validation

```python
text(
    "Name",
    required="Name is required.",
    validate=lambda v: "Too short" if len(v) < 3 else None,
)
```

Return an error string from `validate`, or `None` when valid (same contract as Laravel Prompts).

## Non-interactive fallbacks

When stdin/stdout are not a TTY, `CI=true`, or `AVALON_PROMPTS_INTERACTIVE=0`:

- Prompts return `default` (or the first option for `select`)
- `spin` / `progress` run without animation
- Missing required values raise `RuntimeError`

That keeps CI and scripted runs deterministic.

## Try it

```bash
cd examples/progress
python grail progress:prompts
```

## Related

- [Artisan Console](/console/)
- [Task Scheduling](/scheduling/)
