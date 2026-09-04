"""StatusBadge — class-based Caliburn component."""

from __future__ import annotations

from avalon.caliburn import Component


class StatusBadge(Component):
    """Colored status pill for the showcase."""

    def __init__(self, status: str = "planned") -> None:
        self.status = status

    def render(self) -> str:
        return "components.status_badge"
