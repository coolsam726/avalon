"""Demo middleware — proves alias resolution + pipeline for M2."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from avalon.http import Middleware, Request


class DemoTagMiddleware(Middleware):
    async def handle(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Any]],
    ) -> Any:
        response = await call_next(request)
        response.headers["X-Avalon-Demo"] = "m2"
        response.headers["X-Avalon-Path"] = request.path
        return response
