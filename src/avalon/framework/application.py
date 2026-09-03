"""Application bootstrap — Laravel/Adonis boot story."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from avalon.config import ConfigRepository, load_environment, set_repository
from avalon.framework.container import Container
from avalon.providers.provider import ServiceProvider


class Application:
    """Avalon application kernel."""

    def __init__(self, base_path: str | Path | None = None) -> None:
        self.base_path = Path(base_path or Path.cwd()).resolve()
        self.container = Container()
        self.config = ConfigRepository()
        self._providers: list[ServiceProvider] = []
        self._booted = False
        self._bootstrapped = False

        self.container.instance(Application, self)
        self.container.instance(Container, self.container)
        self.container.instance(ConfigRepository, self.config)
        set_repository(self.config)

    @property
    def is_booted(self) -> bool:
        return self._booted

    @property
    def is_bootstrapped(self) -> bool:
        return self._bootstrapped

    def path(self, *parts: str) -> Path:
        return self.base_path.joinpath(*parts)

    def bootstrap(self) -> Application:
        """Full boot: env → config → register providers → boot providers."""
        if self._bootstrapped:
            return self

        self.load_environment()
        self.load_configuration()
        self.register_configured_providers()
        self.boot()
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
