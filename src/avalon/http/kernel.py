"""HTTP kernel — compiles Avalon routes onto FastAPI."""

from __future__ import annotations

import importlib
import inspect
from collections.abc import Awaitable, Callable, Sequence
from typing import TYPE_CHECKING, Any, get_type_hints

from fastapi import FastAPI
from fastapi import Request as FastAPIRequest
from fastapi.responses import JSONResponse
from starlette.responses import Response as StarletteResponse

from avalon.http.exceptions import HttpException
from avalon.http.middleware import Middleware
from avalon.http.request import Request
from avalon.http.response import make_response
from avalon.routing.router import Action, RouteDefinition, Router

if TYPE_CHECKING:
    from avalon.framework.application import Application


class HttpKernel:
    """Builds the ASGI app from Avalon routes, middleware, and controllers."""

    def __init__(self, app: Application, router: Router) -> None:
        self.app = app
        self.router = router
        self._asgi: FastAPI | None = None

    def create_asgi(self) -> FastAPI:
        if self._asgi is not None:
            return self._asgi

        title = str(self.app.config.get("app.name", "Avalon"))
        debug = bool(self.app.config.get("app.debug", False))
        asgi = FastAPI(title=title, debug=debug)

        @asgi.exception_handler(HttpException)
        async def http_exception_handler(
            _request: FastAPIRequest,
            exc: HttpException,
        ) -> JSONResponse:
            return JSONResponse(
                exc.to_dict(),
                status_code=exc.status_code,
                headers=exc.headers or None,
            )

        @asgi.exception_handler(Exception)
        async def unhandled_exception_handler(
            _request: FastAPIRequest,
            exc: Exception,
        ) -> JSONResponse:
            message = (str(exc) or exc.__class__.__name__) if debug else "Server Error"
            return JSONResponse({"message": message, "status": 500}, status_code=500)

        for route in self.router.routes:
            self._register_route(asgi, route)

        self._asgi = asgi
        return asgi

    def _register_route(self, asgi: FastAPI, route: RouteDefinition) -> None:
        endpoint = self._build_endpoint(route)
        asgi.add_api_route(
            route.uri,
            endpoint,
            methods=list(route.methods),
            name=route.name,
        )

    def _build_endpoint(
        self,
        route: RouteDefinition,
    ) -> Callable[..., Awaitable[StarletteResponse]]:
        async def endpoint(request: FastAPIRequest) -> StarletteResponse:
            avalon_request = Request(request)
            handler = self._resolve_action(route.action)

            async def call_controller(req: Request) -> StarletteResponse:
                result = await self._invoke(handler, req)
                return make_response(result)

            pipeline = self._build_middleware_pipeline(route.middleware, call_controller)
            return await pipeline(avalon_request)

        return endpoint

    def _build_middleware_pipeline(
        self,
        names: Sequence[str],
        core: Callable[[Request], Awaitable[StarletteResponse]],
    ) -> Callable[[Request], Awaitable[StarletteResponse]]:
        aliases = self.app.config.get("http.middleware_aliases", {}) or {}
        global_middleware = list(self.app.config.get("http.middleware", []) or [])
        chain_names = [*global_middleware, *names]

        pipeline = core
        for name in reversed(chain_names):
            middleware = self._resolve_middleware(name, aliases)
            pipeline = self._wrap_middleware(middleware, pipeline)
        return pipeline

    def _wrap_middleware(
        self,
        middleware: Middleware,
        next_call: Callable[[Request], Awaitable[StarletteResponse]],
    ) -> Callable[[Request], Awaitable[StarletteResponse]]:
        async def wrapped(request: Request) -> StarletteResponse:
            return await middleware.handle(request, next_call)

        return wrapped

    def _resolve_middleware(self, name: str, aliases: dict[str, Any]) -> Middleware:
        target = aliases.get(name, name)
        if isinstance(target, type):
            cls = target
        elif isinstance(target, str):
            cls = self._import_string(target)
        else:
            raise RuntimeError(f"Unknown middleware alias or class: {name!r}")

        if not isinstance(cls, type) or not issubclass(cls, Middleware):
            raise TypeError(f"{target!r} is not a Middleware subclass")
        return self.app.make(cls)

    def _resolve_action(self, action: Action) -> Callable[..., Any]:
        if callable(action) and not isinstance(action, type):
            return action

        if isinstance(action, (list, tuple)) and len(action) == 2:
            controller_cls, method_name = action
            if isinstance(controller_cls, str):
                controller_cls = self._import_string(controller_cls)
            controller = self.app.make(controller_cls)
            return getattr(controller, str(method_name))

        if isinstance(action, str) and "@" in action:
            controller_path, method_name = action.split("@", 1)
            controller_cls = self._import_string(controller_path)
            controller = self.app.make(controller_cls)
            return getattr(controller, method_name)

        raise TypeError(f"Unsupported route action: {action!r}")

    def _import_string(self, dotted: str) -> type:
        module_path, _, name = dotted.rpartition(".")
        if not module_path:
            raise ImportError(f"Invalid import path: {dotted!r}")
        module = importlib.import_module(module_path)
        return getattr(module, name)

    async def _invoke(self, handler: Callable[..., Any], request: Request) -> Any:
        try:
            signature = inspect.signature(handler)
        except (TypeError, ValueError):
            result = handler()
            return await result if inspect.isawaitable(result) else result

        try:
            hints = get_type_hints(handler)
        except Exception:
            hints = {}

        kwargs: dict[str, Any] = {}
        for name, param in signature.parameters.items():
            annotation = hints.get(name, param.annotation)
            if annotation is Request or name in {"request", "req"}:
                kwargs[name] = request
            elif name in request.path_params:
                kwargs[name] = request.path_params[name]

        result = handler(**kwargs) if kwargs else handler()
        if inspect.isawaitable(result):
            return await result
        return result
