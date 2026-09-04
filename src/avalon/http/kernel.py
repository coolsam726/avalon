"""HTTP kernel — compiles Avalon routes onto FastAPI."""

from __future__ import annotations

import importlib
import inspect
from collections.abc import Awaitable, Callable, Sequence
from pathlib import Path
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
from avalon.validation.form_request import FormRequest

if TYPE_CHECKING:
    from avalon.framework.application import Application

_SKIP_INJECT_TYPES = {
    str,
    int,
    float,
    bool,
    bytes,
    dict,
    list,
    tuple,
    set,
    type(None),
    Any,
}


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
            return self._exception_response(exc)

        @asgi.exception_handler(Exception)
        async def unhandled_exception_handler(
            _request: FastAPIRequest,
            exc: Exception,
        ) -> JSONResponse:
            message = (str(exc) or exc.__class__.__name__) if debug else "Server Error"
            return JSONResponse({"message": message, "status": 500}, status_code=500)

        for route in self.router.routes:
            self._register_route(asgi, route)

        # Dev/DX: files under public/{css,js,images,fonts,build}/ map to /{dir}/…
        # Production may still front this with a CDN/proxy; starter kits own bundlers.
        public_dir = Path(self.app.base_path) / "public"
        if public_dir.is_dir():
            from fastapi.staticfiles import StaticFiles

            for folder in ("css", "js", "images", "fonts", "build"):
                directory = public_dir / folder
                if directory.is_dir():
                    asgi.mount(
                        f"/{folder}",
                        StaticFiles(directory=str(directory)),
                        name=f"public-{folder}",
                    )

        from avalon.http.subpath import mount_asgi

        asgi = mount_asgi(asgi, str(self.app.config.get("app.base_path", "") or ""))

        trusted = self.app.config.get("http.trusted_proxies")
        if trusted is not None and trusted != []:
            from avalon.http.trust import HEADER_X_FORWARDED_ALL, TrustProxiesASGI

            headers = int(
                self.app.config.get("http.trusted_headers", HEADER_X_FORWARDED_ALL)
                or HEADER_X_FORWARDED_ALL
            )
            asgi = TrustProxiesASGI(asgi, proxies=trusted, headers=headers)  # type: ignore[assignment]

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
            avalon_request = await Request.create(request)
            handler = self._resolve_action(route.action)

            async def call_controller(req: Request) -> StarletteResponse:
                # Convert inside the pipeline so middleware still sees the
                # response on the way out (Laravel handler placement).
                try:
                    result = await self._invoke(handler, req)
                except HttpException as exc:
                    return self._exception_response(exc)
                return make_response(result)

            pipeline = self._build_middleware_pipeline(route.middleware, call_controller)
            return await pipeline(avalon_request)

        return endpoint

    @staticmethod
    def _exception_response(exc: HttpException) -> JSONResponse:
        return JSONResponse(
            exc.to_dict(),
            status_code=exc.status_code,
            headers=exc.headers or None,
        )

    def _build_middleware_pipeline(
        self,
        names: Sequence[str],
        core: Callable[[Request], Awaitable[StarletteResponse]],
    ) -> Callable[[Request], Awaitable[StarletteResponse]]:
        aliases = self.app.config.get("http.middleware_aliases", {}) or {}
        groups = self.app.config.get("http.middleware_groups", {}) or {}
        global_middleware = list(self.app.config.get("http.middleware", []) or [])
        chain_names = self._expand_groups([*global_middleware, *names], groups)

        pipeline = core
        for name in reversed(chain_names):
            middleware = self._resolve_middleware(name, aliases)
            pipeline = self._wrap_middleware(middleware, pipeline)
        return pipeline

    def _expand_groups(
        self,
        names: Sequence[Any],
        groups: dict[str, Any],
        seen: frozenset[str] = frozenset(),
    ) -> list[Any]:
        """Flatten middleware group names (``web`` / ``api``) into their members."""
        expanded: list[Any] = []
        for name in names:
            if not isinstance(name, str) or name not in groups:
                expanded.append(name)
                continue
            if name in seen:
                raise RuntimeError(f"Circular middleware group reference: {name!r}")
            members = list(groups.get(name) or [])
            expanded.extend(self._expand_groups(members, groups, seen | {name}))
        return expanded

    def _wrap_middleware(
        self,
        middleware: Middleware,
        next_call: Callable[[Request], Awaitable[StarletteResponse]],
    ) -> Callable[[Request], Awaitable[StarletteResponse]]:
        async def wrapped(request: Request) -> StarletteResponse:
            return await middleware.handle(request, next_call)

        return wrapped

    def _resolve_middleware(self, name: str, aliases: dict[str, Any]) -> Middleware:
        param: str | None = None
        key = name
        if isinstance(name, str) and ":" in name:
            key, _, param = name.partition(":")
        target = aliases.get(key, key)
        if isinstance(target, type):
            cls = target
        elif isinstance(target, str):
            cls = self._import_string(target)
        else:
            raise RuntimeError(f"Unknown middleware alias or class: {name!r}")

        if not isinstance(cls, type) or not issubclass(cls, Middleware):
            raise TypeError(f"{target!r} is not a Middleware subclass")
        if param is not None:
            return self._instantiate_parameterized(cls, key, param)
        return self.app.make(cls)

    def _instantiate_parameterized(
        self,
        cls: type[Middleware],
        alias_name: str,
        param: str,
    ) -> Middleware:
        if alias_name in {"auth", "guest"}:
            return cls(guard=param)  # type: ignore[call-arg]
        if alias_name in {"auth.basic", "basic"}:
            return cls(field=param)  # type: ignore[call-arg]
        try:
            return cls(param)  # type: ignore[call-arg]
        except TypeError:
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
            if name == "self":
                continue
            annotation = hints.get(name, param.annotation)
            if isinstance(annotation, type) and issubclass(annotation, FormRequest):
                kwargs[name] = annotation.validate_request(request)
            elif annotation is Request or name in {"request", "req"}:
                kwargs[name] = request
            elif name in request.path_params:
                kwargs[name] = request.path_params[name]
            elif (
                annotation is not inspect.Parameter.empty
                and isinstance(annotation, type)
                and annotation not in _SKIP_INJECT_TYPES
            ):
                kwargs[name] = self.app.make(annotation)
            elif param.default is not inspect.Parameter.empty:
                continue
            else:
                raise TypeError(
                    f"Cannot resolve controller parameter {name!r} for {handler!r}"
                )

        result = handler(**kwargs) if kwargs else handler()
        if inspect.isawaitable(result):
            return await result
        return result
