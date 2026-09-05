---
title: Task Scheduling
description: Schedule DSL, cron expressions, overlap mutex, schedule:run and schedule:work.
---

## Defining schedules

Put schedule definitions in `routes/console.py`. The HTTP kernel skips this file; `python grail schedule:run` (and `schedule:work`) load it.

```python
# routes/console.py
from avalon.console import schedule

def heartbeat() -> None:
    ...

schedule.call(heartbeat, description="heartbeat").every_minute()
schedule.command("inspire").hourly()
schedule.command("mail:digest").daily().withoutOverlapping()
```

Fresh apps from `avalon new` ship a commented stub.

## Frequencies

| Method | Cron |
| --- | --- |
| `every_minute()` | `* * * * *` |
| `every_five_minutes()` | `*/5 * * * *` |
| `hourly()` | `0 * * * *` |
| `daily()` | `0 0 * * *` |
| `cron("…")` | custom 5-field expression |

Filters: `weekdays()`, `weekends()`. Overlap control: `withoutOverlapping()` /
`without_overlapping_lock()` — prefers **cache locks** when the Cache manager is
booted (`Cache.lock("schedule:…")`), otherwise a filesystem mutex under
`storage/framework/schedule/`. See [Cache](/cache/).

## Running the schedule

```bash
# Once (wire to system cron: * * * * * cd /path/to/app && python grail schedule:run)
python grail schedule:run

# Long-running ticker (dev / containers)
python grail schedule:work --sleep=60
```

Due events print `Running: …`. Callbacks run in-process; command events invoke the console kernel (`inspire`, app commands, …). Queue-backed jobs wait on **M11**.

## Related

- [Artisan Console](/console/)
- [Cache](/cache/) — preferred overlap locks
- [Error Handling](/errors/)
