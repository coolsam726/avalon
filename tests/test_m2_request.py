"""Extra coverage for Request helpers and remaining HTTP edges."""

from __future__ import annotations

import pytest
from starlette.requests import Request as StarletteRequest
from starlette.responses import JSONResponse

from avalon.http import Middleware, Request, make_response
from avalon.http.middleware import Middleware as MiddlewareBase
from avalon.routing import Route


def _starlette_request(
    path: str = "/demo/1",
    query: str = "q=1",
    headers: list[tuple[bytes, bytes]] | None = None,
) -> StarletteRequest:
    if headers is None:
        headers = [(b"authorization", b"Bearer secret-token")]
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": query.encode(),
        "headers": headers,
        "client": ("127.0.0.1", 123),
        "server": ("test", 80),
    }
    request = StarletteRequest(scope)
    request.scope["path_params"] = {"id": "1"}
    return request


def test_request_helpers() -> None:
    raw = _starlette_request()
    request = Request(raw)
    assert request.method == "GET"
    assert request.path == "/demo/1"
    assert "demo" in request.url
    assert request.input("id") == "1"
    assert request.input("q") == "1"
    assert request.input("missing", "x") == "x"
    assert request.bearer_token() == "secret-token"
    assert request.path_params["id"] == "1"
    assert request.headers.get("authorization")
    assert request.query_params.get("q") == "1"
    assert request.raw is raw


def test_request_bearer_absent() -> None:
    request = Request(_starlette_request(headers=[]))
    assert request.bearer_token() is None


@pytest.mark.asyncio
async def test_middleware_default_passthrough() -> None:
    mw = MiddlewareBase()

    async def nxt(req: Request):
        return JSONResponse({"ok": True})

    response = await mw.handle(Request(_starlette_request()), nxt)
    assert response.status_code == 200


def test_make_response_passthrough_headers() -> None:
    original = JSONResponse({"a": 1})
    wrapped = make_response(original, headers={"X-Test": "1"})
    assert wrapped.headers["x-test"] == "1"


def test_route_static_facade_methods() -> None:
    from avalon.routing.router import Router, set_router

    router = Router()
    set_router(router)
    Route.post("/p", lambda: None)
    Route.put("/u", lambda: None)
    Route.patch("/h", lambda: None)
    Route.delete("/d", lambda: None)
    Route.options("/o", lambda: None)
    Route.any("/any", lambda: None)
    Route.match(["GET"], "/m", lambda: None)
    with Route.group(prefix="/g"):
        Route.get("/x", lambda: None)
    assert any(route.uri == "/g/x" for route in router.routes)
