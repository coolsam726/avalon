"""Application bootstrap — Laravel/Adonis boot story."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any

from avalon.config import ConfigRepository, load_environment, set_repository
from avalon.framework.container import Container
from avalon.providers.provider import ServiceProvider
from avalon.routing.router import Router, set_router


class Application:
    """Avalon application kernel."""

    def __init__(self, base_path: str | Path | None = None) -> None:
        self.base_path = Path(base_path or Path.cwd()).resolve()
        self.container = Container()
        self.config = ConfigRepository()
        self.router = Router()
        from avalon.http.kernel import HttpKernel

        self.http_kernel = HttpKernel(self, self.router)
        self._providers: list[ServiceProvider] = []
        self._booted = False
        self._bootstrapped = False
        self._routes_loaded = False

        self.container.instance(Application, self)
        self.container.instance(Container, self.container)
        self.container.instance(ConfigRepository, self.config)
        self.container.instance(Router, self.router)
        self.container.instance(HttpKernel, self.http_kernel)
        set_repository(self.config)
        set_router(self.router)

    @property
    def is_booted(self) -> bool:
        return self._booted

    @property
    def is_bootstrapped(self) -> bool:
        return self._bootstrapped

    @property
    def asgi(self) -> Any:
        """Compiled FastAPI ASGI application (hidden from app-level imports)."""
        if not self._bootstrapped:
            self.bootstrap()
        return self.http_kernel.create_asgi()

    def path(self, *parts: str) -> Path:
        return self.base_path.joinpath(*parts)

    def bootstrap(self) -> Application:
        """Full boot: env → config → register providers → boot → load routes."""
        if self._bootstrapped:
            return self

        self.load_environment()
        self.load_configuration()
        self.register_configured_providers()
        self.boot()
        self.load_routes()
        self._bootstrapped = True
        return self

    def load_environment(self) -> bool:
        return load_environment(self.base_path)

    def load_configuration(self) -> None:
        self.config.load_directory(self.path("config"))
        set_repository(self.config)

    def register(self, provider: ServiceProvider | type[ServiceProvider] | str) -> ServiceProvider:
        instance = self._make_provider(provider)
        instance.register()
        self._providers.append(instance)
        return instance

    def register_configured_providers(self) -> None:
        from avalon.providers.foundation import FoundationServiceProvider

        self.register(FoundationServiceProvider)
        providers = self.config.get("app.providers", []) or []
        for provider in providers:
            if provider in (
                FoundationServiceProvider,
                "avalon.providers.foundation.FoundationServiceProvider",
            ):
                continue
            self.register(provider)

    def boot(self) -> None:
        if self._booted:
            return
        for provider in self._providers:
            provider.boot()
        self._booted = True

    def load_routes(self) -> None:
        if self._routes_loaded:
            return
        set_router(self.router)
        routes_dir = self.path("routes")
        if routes_dir.is_dir():
            for file in sorted(routes_dir.glob("*.py")):
                if file.name.startswith("_"):
                    continue
                self._load_route_file(file)
        self._routes_loaded = True

    def _load_route_file(self, file: Path) -> None:
        module_name = f"avalon_app_routes_{file.stem}_{abs(hash(file))}"
        spec = importlib.util.spec_from_file_location(module_name, file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load route file: {file}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        finally:
            # Keep module around so controller class refs from the file stay valid if needed.
            pass

    def make(self, abstract: type | str) -> Any:
        return self.container.make(abstract)

    def resolve(self, abstract: type | str) -> Any:
        return self.container.resolve(abstract)

    def _make_provider(
        self,
        provider: ServiceProvider | type[ServiceProvider] | str,
    ) -> ServiceProvider:
        if isinstance(provider, ServiceProvider):
            return provider
        if isinstance(provider, str):
            cls = self._import_provider(provider)
            return cls(self)
        if isinstance(provider, type) and issubclass(provider, ServiceProvider):
            return provider(self)
        raise TypeError(f"Invalid service provider: {provider!r}")

    def _import_provider(self, dotted_path: str) -> type[ServiceProvider]:
        module_path, _, name = dotted_path.rpartition(".")
        if not module_path:
            raise ImportError(f"Invalid provider path: {dotted_path!r}")
        module = importlib.import_module(module_path)
        cls = getattr(module, name)
        if not isinstance(cls, type) or not issubclass(cls, ServiceProvider):
            raise TypeError(f"{dotted_path!r} is not a ServiceProvider subclass")
        return cls
