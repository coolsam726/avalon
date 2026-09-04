"""Welcome controller — web route, renders HTML."""

from __future__ import annotations

from app.support.page import layout

from avalon import __version__
from avalon.config import config
from avalon.http import Controller, Response, html
from avalon.routing import url

_API_LINKS = [
    ("/api/health", "middleware group + alias headers"),
    ("/api/progress", "milestone board as JSON"),
    ("/api/orm", "M5 ORM feature tour"),
    ("/api/posts", "eager-loaded published posts"),
    ("/api/users", "with_count + belongs_to_many roles"),
    ("/api/items/42?q=hello", "route params, query, only()"),
    ("/api/bag", "full Request input surface"),
    ("/api/di", "container injection into an action"),
    ("/api/boom", "HttpException JSON shape"),
]


class WelcomeController(Controller):
    async def index(self) -> Response:
        app_name = str(config("app.name", "Progress"))
        # url() keeps links correct when the app is hosted under APP_BASE_PATH.
        links = "\n".join(
            f'    <li><a href="{url(href, absolute=False)}"><code>{href}</code></a> — {label}</li>'
            for href, label in _API_LINKS
        )
        body = f"""  <h1>Avalon progress tracker</h1>
  <p>{app_name} on Avalon {__version__} (env: {config("app.env", "local")}).</p>
  <p><a href="{url("/progress", absolute=False)}">Milestone board</a> — this page and the board are
  web routes, so they render HTML. Everything under <code>/api</code> is stateless JSON.</p>
  <h2>API surface</h2>
  <ul>
{links}
  </ul>"""
        return html(layout(f"{app_name} — Avalon", body))
