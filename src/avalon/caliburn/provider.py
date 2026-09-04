"""Caliburn service provider."""

from __future__ import annotations

from avalon.caliburn.engine import Engine
from avalon.caliburn.helpers import ViewFactory, set_engine
from avalon.providers.provider import ServiceProvider


class CaliburnServiceProvider(ServiceProvider):
    """Binds the view engine and registers ``resources/views``."""

    def register(self) -> None:
        app = self.app

        def factory(_container):
            engine = Engine(paths=[], cache_enabled=True)
            # Conventional Laravel-shaped path; create-on-write is the app's job.
            engine.add_path(app.path("resources", "views"))
            return engine

        app.container.singleton(Engine, factory)
        app.container.alias(Engine, "view.engine")
        app.container.singleton(ViewFactory, lambda c: ViewFactory(c.resolve(Engine)))
        app.container.alias(ViewFactory, "view")

    def boot(self) -> None:
        set_engine(self.app.make(Engine))
