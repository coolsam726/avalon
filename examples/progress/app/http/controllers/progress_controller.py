"""Milestone board — HTML on the web route, JSON on the API route."""

from __future__ import annotations

from app.support.page import layout

from avalon import __version__
from avalon.config import config
from avalon.http import Controller, Response, html
from avalon.routing import url


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
            "status": "complete",
            "proof": [
                "Route DSL + nested groups/prefix",
                "controllers via container DI",
                "middleware groups (web/api) + aliases",
                "Request all/input/query/post/only/except_/files",
                "web HTML vs api JSON polarity",
                "HttpException JSON",
                "application.asgi",
            ],
        },
        {
            "id": "M3",
            "name": "Validation + DX",
            "status": "complete",
            "proof": [
                "FormRequest + Laravel-shaped 422",
                "authorize() -> 403, messages(), attributes()",
                "python grail make:controller/middleware/provider/request",
                "url() honoring APP_BASE_PATH",
            ],
        },
        {
            "id": "M4",
            "name": "Localization",
            "status": "complete",
            "proof": [
                "lang/ PHP+JSON catalogs",
                "__() / trans_choice() + CLDR plurals",
                "namespaces + lang:publish / missing",
                "Number helpers + SetLocale",
            ],
        },
        {
            "id": "M5",
            "name": "ORM",
            "status": "complete",
            "proof": [
                "GET /api/orm feature tour",
                "eager load / soft deletes / pivot / morphs",
                "grail migrate / make:model",
            ],
        },
        {
            "id": "M6",
            "name": "Caliburn",
            "status": "next",
            "proof": [".cal.html", "@python blocks", "featherweight render"],
        },
        {
            "id": "M7",
            "name": "Auth",
            "status": "planned",
            "proof": ["session/token guards", "auth middleware"],
        },
        {
            "id": "M8",
            "name": "Error handling",
            "status": "planned",
            "proof": ["Handler report/render", "debug page", "log channels"],
        },
        {
            "id": "M9",
            "name": "Console + scheduler",
            "status": "planned",
            "proof": ["Command base", "grail list", "schedule:run"],
        },
        {
            "id": "M10",
            "name": "Filesystem",
            "status": "planned",
            "proof": ["Storage disks", "local + S3-compatible"],
        },
        {
            "id": "M11",
            "name": "Queues + workers",
            "status": "planned",
            "proof": ["Job dispatch", "queue:work", "failed jobs"],
        },
    ]


def _board() -> dict:
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


class ProgressController(Controller):
    async def index(self) -> Response:
        board = _board()
        rows = "\n".join(
            f"""    <tr>
      <td><strong>{m["id"]}</strong></td>
      <td>{m["name"]}</td>
      <td class="{m["status"]}">{m["status"]}</td>
      <td>{", ".join(m["proof"])}</td>
    </tr>"""
            for m in board["milestones"]
        )
        body = f"""  <h1>Milestones</h1>
  <p>{board["completed"]} of {board["total"]} complete on Avalon {board["version"]}.</p>
  <table>
    <tr><th>ID</th><th>Milestone</th><th>Status</th><th>Proof</th></tr>
{rows}
  </table>
  <p><a href="{url("/", absolute=False)}">Back</a> — same data as JSON at
  <code>{url("/api/progress", absolute=False)}</code>.</p>"""
        return html(layout("Milestones — Avalon", body))

    async def data(self) -> dict:
        return _board()
