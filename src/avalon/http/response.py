"""Response helpers."""

from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse, PlainTextResponse, Response
from starlette.responses import Response as StarletteResponse


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
