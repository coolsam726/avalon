"""Welcome controller — Caliburn landing page."""

from __future__ import annotations

from avalon import __version__
from avalon.caliburn import view
from avalon.config import config
from avalon.http import Controller, Response
from avalon.routing import url

_API_LINKS = [
    {"href": "/api/health", "label": "middleware group + alias headers"},
    {"href": "/api/progress", "label": "milestone board as JSON"},
    {"href": "/api/orm", "label": "M5 ORM feature tour"},
    {"href": "/api/posts", "label": "eager-loaded published posts"},
    {"href": "/api/users", "label": "with_count + belongs_to_many roles"},
    {"href": "/api/items/42?q=hello", "label": "route params, query, only()"},
    {"href": "/api/bag", "label": "full Request input surface"},
    {"href": "/api/di", "label": "container injection into an action"},
    {"href": "/api/boom", "label": "HttpException JSON shape"},
]

_FEATURES = [
    {
        "title": "Caliburn views",
        "body": "Layouts, components, stacks, and control flow — Blade parity for Python.",
    },
    {
        "title": "Articulate ORM",
        "body": "Eager loading, soft deletes, morphs, and grail migrate — async by default.",
    },
    {
        "title": "Session + CSRF",
        "body": "Signed cookie sessions, EncryptCookies, and @csrf on the web group.",
    },
    {
        "title": "Web vs API",
        "body": "Same kernel, polarity-aware responses: HTML on web, JSON under /api.",
    },
]


class WelcomeController(Controller):
    async def index(self) -> Response:
        app_name = str(config("app.name", "Progress"))
        links = [
            {**link, "href": url(link["href"], absolute=False)}
            for link in _API_LINKS
        ]
        return view(
            "welcome",
            {
                "app_name": app_name,
                "version": __version__,
                "env": config("app.env", "local"),
                "board_url": url("/progress", absolute=False),
                "showcase_url": url("/showcase", absolute=False),
                "login_url": url("/login", absolute=False),
                "features": _FEATURES,
                "api_links": links,
            },
        )

    async def settings(self) -> Response:
        return view(
            "auth.settings",
            {
                "home_url": url("/", absolute=False),
            },
        )
