"""Console schedule — loaded by ``python grail schedule:run``."""

from __future__ import annotations

from pathlib import Path

from avalon.console import schedule


def _heartbeat() -> None:
    stamp = Path("storage/framework/schedule-heartbeat.txt")
    stamp.parent.mkdir(parents=True, exist_ok=True)
    stamp.write_text("ok\n", encoding="utf-8")


schedule.call(_heartbeat, description="progress-heartbeat").every_minute()
schedule.command("progress:hello").hourly()
