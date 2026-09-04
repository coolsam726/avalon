"""Response helpers."""

from __future__ import annotations

from typing import Any

from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
)
from starlette.responses import Response as StarletteResponse

__all__ = ["Response", "html", "json", "make_response", "redirect"]


def make_response(
    content: Any = None,
    *,
    status: int = 200,
    headers: dict[str, str] | None = None,
) -> StarletteResponse:
    """Normalize controller return values into an ASGI response."""
    if isinstance(content, StarletteResponse):
        if headers:
            for key, value in headers.items():
                content.headers[key] = value
        return content

    if content is None:
        return Response(status_code=status if status != 200 else 204, headers=headers)

    if isinstance(content, (dict, list)):
        return JSONResponse(content, status_code=status, headers=headers)

    if isinstance(content, (bytes, bytearray)):
        return Response(content=bytes(content), status_code=status, headers=headers)

    return PlainTextResponse(str(content), status_code=status, headers=headers)


def json(
    data: Any,
    *,
    status: int = 200,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(data, status_code=status, headers=headers)


def html(
    content: str,
    *,
    status: int = 200,
    headers: dict[str, str] | None = None,
) -> HTMLResponse:
    """Return an HTML response — the web-route counterpart to :func:`json`.

    Until Caliburn (M5) provides ``view()``, web controllers build markup here.
    """
    return HTMLResponse(content, status_code=status, headers=headers)


def redirect(
    to: str,
    *,
    status: int = 302,
    headers: dict[str, str] | None = None,
) -> RedirectResponse:
    """Redirect to `to`, resolved through `APP_URL` / `APP_BASE_PATH`."""
    from avalon.routing.url import url

    return RedirectResponse(url(to, absolute=False), status_code=status, headers=headers)
