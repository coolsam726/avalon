"""Welcome controller — home of the progress tracker example."""

from __future__ import annotations

from avalon import __version__
from avalon.config import config


class WelcomeController:
    async def index(self) -> dict:
        return {
            "message": "Avalon progress tracker",
            "framework_version": __version__,
            "app": str(config("app.name", "Progress")),
            "env": str(config("app.env", "local")),
            "links": {
                "progress": "/progress",
                "plan": "docs/PLAN.md (framework repo)",
                "smoke": "docs/SMOKE.md (framework repo)",
            },
        }
