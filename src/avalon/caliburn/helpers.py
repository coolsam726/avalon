"""``view()`` helper and factory."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from starlette.responses import HTMLResponse

from avalon.caliburn.compiler import DirectiveHandler
from avalon.caliburn.engine import ComposerCallback, Engine
from avalon.http.response import html

_engine: Engine | None = None


def set_engine(engine: Engine | None) -> None:
    global _engine
    _engine = engine


def get_engine() -> Engine:
    if _engine is None:
        raise RuntimeError("Caliburn engine is not set. Bootstrap the Application first.")
    return _engine


class ViewFactory:
    """Laravel-shaped view factory bound in the container."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def make(self, name: str, data: dict[str, Any] | None = None) -> str:
        return self.engine.render(name, data)

    def composer(
        self,
        views: str | Sequence[str],
        callback: ComposerCallback,
    ) -> None:
        self.engine.composer(views, callback)

    def directive(self, name: str, handler: DirectiveHandler) -> None:
        self.engine.directive(name, handler)

    def clear_cache(self) -> None:
        self.engine.clear_cache()

    def cache(self) -> int:
        return self.engine.cache_views()

    def __call__(
        self,
        name: str,
        data: dict[str, Any] | None = None,
        *,
        status: int = 200,
        headers: dict[str, str] | None = None,
    ) -> HTMLResponse:
        return view(name, data, status=status, headers=headers)


def view(
    name: str,
    data: dict[str, Any] | None = None,
    *,
    status: int = 200,
    headers: dict[str, str] | None = None,
) -> HTMLResponse:
    """Render a Caliburn template to an HTML response."""
    content = get_engine().render(name, data)
    return html(content, status=status, headers=headers)


def render(name: str, data: dict[str, Any] | None = None) -> str:
    """Render a Caliburn template to a string (no HTTP wrapper)."""
    return get_engine().render(name, data)
