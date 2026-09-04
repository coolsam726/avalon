"""Import milestone stubs and cover remaining edges for coverage."""

from __future__ import annotations

import avalon.auth
import avalon.caliburn
import avalon.http
import avalon.orm
import avalon.routing
import avalon.translation
import avalon.validation
from avalon.framework import Application, Container
from avalon.providers import ServiceProvider


def test_stub_packages_importable() -> None:
    assert avalon.routing.__all__
    assert "FormRequest" in avalon.validation.__all__
    assert "Translator" in avalon.translation.__all__
    assert "__" in avalon.translation.__all__
    assert "Model" in avalon.orm.__all__
    assert "QueryBuilder" in avalon.orm.__all__
    assert avalon.auth.__all__ == []
    assert "Engine" in avalon.caliburn.__all__
    assert "view" in avalon.caliburn.__all__
    assert "Controller" in avalon.http.__all__
    assert "Route" in avalon.routing.__all__


def test_container_instance_edge() -> None:
    container = Container()
    container.instance("app_name", "Avalon")
    assert container.resolve("app_name") == "Avalon"
    container._instances["orphan"] = 42  # noqa: SLF001
    assert container.resolve("orphan") == 42


def test_service_provider_hooks() -> None:
    app = Application(base_path=".")
    provider = ServiceProvider(app)
    provider.register()
    provider.boot()
    assert provider.app is app
