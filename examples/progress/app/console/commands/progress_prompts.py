"""Demo Avalon Prompts — Laravel Prompts-shaped interactive UI."""

from __future__ import annotations

import time

from avalon.console import Command
from avalon.console.prompts import (
    confirm,
    intro,
    note,
    outro,
    progress,
    select,
    spin,
    text,
)


class ProgressPromptsCommand(Command):
    signature = "progress:prompts"
    description = "Demo Avalon Prompts (Laravel Prompts-class UI)"

    def handle(self) -> int:
        intro("Avalon Prompts")
        note("Arrow keys, styled panels, spin & progress — try it interactively.")

        name = text(
            "What should we call this demo?",
            placeholder="e.g. Excalibur",
            default="Avalon",
            hint="Shown in the outro.",
        )
        flavor = select(
            "Pick a tone",
            {"bold": "Bold & bright", "calm": "Calm & clear", "playful": "Playful"},
            default="calm",
        )
        if confirm("Run a quick spinner + progress bar?", default=True):
            spin(lambda: time.sleep(0.4), "Warming up…")
            progress(
                "Polishing prompts",
                ["text", "select", "spin", "progress"],
                lambda step: time.sleep(0.15),
            )

        outro(f"Done — {name} ({flavor}). Run again anytime: python grail progress:prompts")
        return 0
