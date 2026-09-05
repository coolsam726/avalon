"""Schedule DSL — daily / hourly / every_minute / cron + overlap mutex."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from avalon.console.mutex import Mutex

Callback = Callable[[], Any]


@dataclass
class Event:
    """A single scheduled event (command name or callback)."""

    description: str
    callback: Callback | None = None
    command: str | None = None
    expression: str = "* * * * *"  # min hour dom month dow
    without_overlapping: bool = False
    _filters: list[Callable[[datetime], bool]] = field(default_factory=list)

    def cron(self, expression: str) -> Event:
        self.expression = expression
        return self

    def every_minute(self) -> Event:
        return self.cron("* * * * *")

    def hourly(self) -> Event:
        return self.cron("0 * * * *")

    def daily(self) -> Event:
        return self.cron("0 0 * * *")

    def every_five_minutes(self) -> Event:
        return self.cron("*/5 * * * *")

    def weekdays(self) -> Event:
        self._filters.append(lambda dt: dt.weekday() < 5)
        return self

    def weekends(self) -> Event:
        self._filters.append(lambda dt: dt.weekday() >= 5)
        return self

    def without_overlapping_lock(self) -> Event:
        self.without_overlapping = True
        return self

    # Laravel alias
    def withoutOverlapping(self) -> Event:  # noqa: N802
        return self.without_overlapping_lock()

    def is_due(self, at: datetime | None = None) -> bool:
        moment = at or datetime.now()
        if not _cron_matches(self.expression, moment):
            return False
        return all(predicate(moment) for predicate in self._filters)

    def mutex_name(self) -> str:
        return self.command or self.description


class Schedule:
    """Collects scheduled events (Laravel ``Schedule`` shape)."""

    def __init__(self) -> None:
        self.events: list[Event] = []

    def call(self, callback: Callback, description: str | None = None) -> Event:
        event = Event(
            description=description or getattr(callback, "__name__", "call"),
            callback=callback,
        )
        self.events.append(event)
        return event

    def command(self, signature: str) -> Event:
        event = Event(description=signature, command=signature)
        self.events.append(event)
        return event

    def due_events(self, at: datetime | None = None) -> list[Event]:
        moment = at or datetime.now()
        return [event for event in self.events if event.is_due(moment)]


# Process-wide schedule used by ``routes/console.py``.
schedule = Schedule()


_FIELD_RE = re.compile(r"^(\*/\d+|\d+(-\d+)?(,\d+(-\d+)?)*|\*)$")


def _cron_matches(expression: str, moment: datetime) -> bool:
    parts = expression.split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression: {expression!r}")
    minute, hour, dom, month, dow = parts
    return (
        _field_matches(minute, moment.minute, 0, 59)
        and _field_matches(hour, moment.hour, 0, 23)
        and _field_matches(dom, moment.day, 1, 31)
        and _field_matches(month, moment.month, 1, 12)
        and _field_matches(dow, (moment.weekday() + 1) % 7, 0, 6)  # 0=Sunday
    )


def _field_matches(field: str, value: int, minimum: int, maximum: int) -> bool:
    if field == "*":
        return True
    if field.startswith("*/"):
        step = int(field[2:])
        return (value - minimum) % step == 0
    for piece in field.split(","):
        if "-" in piece:
            start_s, end_s = piece.split("-", 1)
            if int(start_s) <= value <= int(end_s):
                return True
        elif int(piece) == value:
            return True
    return False


def run_event(event: Event, *, base_path, runner: Callable[[str], int] | None = None) -> int:
    """Execute one due event, honoring withoutOverlapping.

    Prefers ``Cache.lock`` when the cache manager is booted; falls back to the
    filesystem mutex under ``storage/framework/schedule``.
    """
    lock: Any = None
    mutex: Mutex | None = None
    if event.without_overlapping:
        lock = _try_cache_lock(event.mutex_name())
        if lock is not None:
            if lock.get() is False:
                return 0
        else:
            mutex = Mutex(base_path, event.mutex_name())
            if not mutex.acquire():
                return 0
    try:
        if event.callback is not None:
            event.callback()
            return 0
        if event.command and runner is not None:
            return int(runner(event.command))
        return 0
    finally:
        if lock is not None:
            lock.release()
        if mutex is not None:
            mutex.release()


def _try_cache_lock(name: str) -> Any | None:
    try:
        from avalon.cache.manager import Cache

        Cache.manager()
        return Cache.lock(f"schedule:{name}", seconds=3600)
    except Exception:
        return None
