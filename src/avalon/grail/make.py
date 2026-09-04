"""Class generators behind `python grail make:*`."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from avalon.orm.inflector import snake

_SEGMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class MakeError(ValueError):
    """Invalid generator request."""


@dataclass(frozen=True)
class Blueprint:
    directory: tuple[str, ...]
    stub: str

def _controller_stub(name: str) -> str:
    return f'''"""{name}."""

from __future__ import annotations

from avalon.http import Controller


class {name}(Controller):
    """{name}."""

    async def index(self) -> dict[str, str]:
        # Web routes return html(...); api routes return dict / list.
        return {{"controller": "{name}"}}
'''


def _middleware_stub(name: str) -> str:
    return f'''"""{name}."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from avalon.http import Middleware, Request


class {name}(Middleware):
    """{name}."""

    async def handle(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Any]],
    ) -> Any:
        return await call_next(request)
'''


def _provider_stub(name: str) -> str:
    return f'''"""{name}."""

from __future__ import annotations

from avalon.providers import ServiceProvider


class {name}(ServiceProvider):
    """{name}."""

    def register(self) -> None:
        """Bind services into the container."""

    def boot(self) -> None:
        """Bootstrap services after all providers are registered."""
'''


def _request_stub(name: str) -> str:
    return f'''"""{name}."""

from __future__ import annotations

from avalon.validation import Field, FormRequest


class {name}(FormRequest):
    """{name}."""

    name: str = Field(min_length=1)

    def authorize(self) -> bool:
        return True

    def messages(self) -> dict[str, str]:
        return {{}}
'''


def _model_stub(name: str) -> str:
    return f'''"""{name} model."""

from __future__ import annotations

from avalon.orm import Model


class {name}(Model):
    """{name} model."""

    fillable: tuple[str, ...] = ()
'''


def _seeder_stub(name: str) -> str:
    return f'''"""{name}."""

from __future__ import annotations

from avalon.orm import Seeder


class {name}(Seeder):
    """{name}."""

    async def run(self) -> None:
        """Seed the application's database."""
'''


BLUEPRINTS: dict[str, Blueprint] = {
    "controller": Blueprint(("app", "http", "controllers"), "controller"),
    "middleware": Blueprint(("app", "http", "middleware"), "middleware"),
    "provider": Blueprint(("app", "providers"), "provider"),
    "request": Blueprint(("app", "http", "requests"), "request"),
    "model": Blueprint(("app", "models"), "model"),
    "seeder": Blueprint(("database", "seeders"), "seeder"),
}

_STUBS = {
    "controller": _controller_stub,
    "middleware": _middleware_stub,
    "provider": _provider_stub,
    "request": _request_stub,
    "model": _model_stub,
    "seeder": _seeder_stub,
}


def _split(name: str) -> tuple[tuple[str, ...], str]:
    parts = [part for part in name.replace("\\", "/").split("/") if part]
    if not parts:
        raise MakeError("A class name is required.")
    for part in parts:
        if not _SEGMENT_RE.match(part):
            raise MakeError(
                f"Invalid name segment {part!r}. Use letters, numbers, and underscores; "
                "must start with a letter."
            )
    return tuple(parts[:-1]), parts[-1]


def make(kind: str, name: str, *, base_path: Path, force: bool = False) -> Path:
    """Generate a class file and return its path.

    CLI names stay PascalCase (`PostController`, `Admin/UserController`);
    packages and module files use Python snake_case
    (`app/http/controllers/admin/user_controller.py`).
    """
    blueprint = BLUEPRINTS.get(kind)
    if blueprint is None:
        raise MakeError(f"Unknown generator {kind!r}.")

    namespace, class_name = _split(name)
    package_ns = tuple(snake(part) for part in namespace)
    module_name = snake(class_name)
    directory = base_path.joinpath(*blueprint.directory, *package_ns)
    target = directory / f"{module_name}.py"
    if target.exists() and not force:
        raise MakeError(f"{target.relative_to(base_path)} already exists. Use --force to overwrite.")

    directory.mkdir(parents=True, exist_ok=True)
    _ensure_packages(base_path, blueprint.directory + package_ns)
    target.write_text(_STUBS[kind](class_name), encoding="utf-8")
    return target

def _ensure_packages(base_path: Path, parts: tuple[str, ...]) -> None:
    """Generated directories must be importable packages."""
    for depth in range(1, len(parts) + 1):
        init = base_path.joinpath(*parts[:depth], "__init__.py")
        if not init.exists():
            init.write_text("", encoding="utf-8")
