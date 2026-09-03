"""Progress endpoint — compact milestone board for Avalon development."""

from __future__ import annotations

from avalon import __version__
from avalon.config import config


def _milestones() -> list[dict]:
    # Keep in sync with docs/PLAN.md as milestones land.
    return [
        {
            "id": "M0",
            "name": "Skeleton",
            "status": "complete",
            "proof": ["avalon new", "python grail serve", "examples/progress scaffold"],
        },
        {
            "id": "M1",
            "name": "Application kernel",
            "status": "complete",
            "proof": [
                "bootstrap Application",
                f"config app.name={config('app.name')}",
                "FoundationServiceProvider + AppServiceProvider",
            ],
        },
        {
            "id": "M2",
            "name": "HTTP + routing",
            "status": "next",
            "proof": ["Route DSL", "middleware", "Avalon HTTP kernel"],
        },
        {
            "id": "M3",
            "name": "Validation + DX",
            "status": "planned",
            "proof": ["FormRequest", "python grail make:*"],
        },
        {
            "id": "M4",
            "name": "ORM",
            "status": "planned",
            "proof": ["Eloquent-like models", "migrations"],
        },
        {
            "id": "M5",
            "name": "Caliburn",
            "status": "planned",
            "proof": [".cal.html", "@python blocks", "featherweight render"],
        },
        {
            "id": "M6",
            "name": "Auth",
            "status": "planned",
            "proof": ["session/token guards", "auth middleware"],
        },
    ]


class ProgressController:
    async def index(self) -> dict:
        milestones = _milestones()
        complete = [m for m in milestones if m["status"] == "complete"]
        return {
            "framework": "avalon",
            "version": __version__,
            "app": str(config("app.name")),
            "completed": len(complete),
            "total": len(milestones),
            "milestones": milestones,
        }
