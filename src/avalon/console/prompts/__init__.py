"""Avalon Prompts — Laravel Prompts-shaped interactive console UI."""

from __future__ import annotations

from avalon.console.prompts.busy import Progress, progress, spin
from avalon.console.prompts.confirm import confirm, pause
from avalon.console.prompts.messages import (
    alert,
    clear,
    error,
    info,
    intro,
    note,
    outro,
    table,
    warning,
)
from avalon.console.prompts.choices import multiselect, search, select, suggest
from avalon.console.prompts.inputs import number, password, text, textarea

__all__ = [
    "Progress",
    "alert",
    "clear",
    "confirm",
    "error",
    "info",
    "intro",
    "multiselect",
    "note",
    "number",
    "outro",
    "password",
    "pause",
    "progress",
    "search",
    "select",
    "spin",
    "suggest",
    "table",
    "text",
    "textarea",
    "warning",
]
