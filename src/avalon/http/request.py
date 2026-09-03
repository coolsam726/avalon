"""Request wrapper around Starlette/FastAPI request."""

from __future__ import annotations

from typing import Any

from starlette.requests import Request as StarletteRequest


class Request:
    """Laravel-flavored request façade over the ASGI request."""

    def __init__(self, request: StarletteRequest) -> None:
        self._request = request

    @property
    def raw(self) -> StarletteRequest:
        return self._request

    @property
    def method(self) -> str:
        return self._request.method

    @property
    def url(self) -> str:
        return str(self._request.url)

    @property
    def path(self) -> str:
        return self._request.url.path

    @property
    def headers(self) -> Any:
        return self._request.headers

    @property
    def query_params(self) -> Any:
        return self._request.query_params

    @property
    def path_params(self) -> dict[str, Any]:
        return dict(self._request.path_params)

    def input(self, key: str, default: Any = None) -> Any:
        if key in self._request.path_params:
            return self._request.path_params[key]
        if key in self._request.query_params:
            return self._request.query_params.get(key)
        return default

    def bearer_token(self) -> str | None:
        auth = self._request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            return auth[7:].strip() or None
        return None

    async def json(self) -> Any:
        try:
            return await self._request.json()
        except Exception:
            return None

    async def form(self) -> Any:
        return await self._request.form()
