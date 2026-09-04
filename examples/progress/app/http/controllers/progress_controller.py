"""Milestone board — HTML on the web route, JSON on the API route."""

from __future__ import annotations

from avalon import __version__
from avalon.caliburn import view
from avalon.config import config
from avalon.http import Controller, Response
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
            "status": "complete",
            "proof": [
                ".cal.html layouts + @foreach",
                "components / slots / @props",
                "@push / @stack / @parent",
                "view() + @csrf / @auth / @guest",
            ],
        },
        {
            "id": "M7",
            "name": "Auth",
            "status": "complete",
            "proof": [
                "cookie session + CSRF + EncryptCookies",
                "session + token guards / remember-me",
                "Hash (bcrypt + optional argon2id)",
                "Password broker + auth middleware",
                "GET /login · /api/me",
            ],
        },
        {
            "id": "M8",
            "name": "Error handling",
            "status": "complete",
            "proof": [
                "Handler report/render",
                "APP_DEBUG page vs production views",
                "errors:publish + log channels",
                "GET /boom · /api/explode",
            ],
        },
        {
            "id": "M9",
            "name": "Console + scheduler",
            "status": "next",
            "proof": ["Command base", "grail list", "schedule:run", "REPL"],
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
        {
            "id": "M12",
            "name": "Mail",
            "status": "planned",
            "proof": ["Mailable + Mailer", "log/array/SMTP", "Markdown mail"],
        },
        {
            "id": "M13",
            "name": "Notifications",
            "status": "planned",
            "proof": ["Notifiable", "mail + database channels", "email verification"],
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
        milestones = [
            {**m, "proof_text": ", ".join(m["proof"])}
            for m in board["milestones"]
        ]
        return view(
            "progress",
            {
                "completed": board["completed"],
                "total": board["total"],
                "version": board["version"],
                "milestones": milestones,
                "home_url": url("/", absolute=False),
                "api_url": url("/api/progress", absolute=False),
                "version": board["version"],
            },
        )

    async def data(self) -> dict:
        return _board()
