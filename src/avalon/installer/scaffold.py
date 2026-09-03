"""Scaffold a new Avalon application tree."""

from __future__ import annotations

import re
from pathlib import Path

_APP_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


class ScaffoldError(ValueError):
    """Invalid scaffold request."""


def validate_app_name(name: str) -> str:
    if not _APP_NAME_RE.match(name):
        raise ScaffoldError(
            f"Invalid app name {name!r}. Use letters, numbers, underscores, or hyphens; "
            "must start with a letter."
        )
    return name


def title_case(name: str) -> str:
    parts = re.split(r"[-_]+", name)
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def scaffold_app(name: str, destination: Path | None = None) -> Path:
    """Create a new Avalon application directory and return its path."""
    name = validate_app_name(name)
    root = (destination or Path.cwd() / name).resolve()
    if root.exists() and any(root.iterdir()):
        raise ScaffoldError(f"Directory already exists and is not empty: {root}")

    root.mkdir(parents=True, exist_ok=True)
    display = title_case(name)

    files: dict[str, str] = {
        "grail": _GRAIL_SCRIPT,
        "README.md": _readme(name, display),
        "pyproject.toml": _pyproject(name, display),
        ".env": _env_file(display),
        ".env.example": _env_file(display),
        ".gitignore": _GITIGNORE,
        "app/__init__.py": "",
        "app/Http/__init__.py": "",
        "app/Http/Controllers/__init__.py": "",
        "app/Http/Controllers/WelcomeController.py": _welcome_controller(),
        "app/Providers/__init__.py": "",
        "app/Providers/AppServiceProvider.py": _app_service_provider(),
        "bootstrap/__init__.py": "",
        "bootstrap/app.py": _bootstrap_app(display),
        "config/__init__.py": "",
        "config/app.py": _config_app(display),
        "config/http.py": _config_http(),
        "routes/__init__.py": "",
        "routes/api.py": _routes_api(),
        "routes/web.py": _routes_web(),
        "resources/views/.gitkeep": "",
        "storage/framework/.gitkeep": "",
    }

    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        if relative == "grail":
            path.chmod(path.stat().st_mode | 0o111)

    return root


_GRAIL_SCRIPT = '''#!/usr/bin/env python
"""Grail — Avalon in-application CLI (Laravel artisan equivalent).

    python grail version
    python grail serve
"""

from __future__ import annotations

from avalon.grail.cli import app

if __name__ == "__main__":
    app()
'''

_GITIGNORE = """__pycache__/
*.py[cod]
.venv/
venv/
.env
.pytest_cache/
.ruff_cache/
.mypy_cache/
.caliburn_cache/
storage/framework/views/
*.egg-info/
dist/
build/
"""


def _env_file(display: str) -> str:
    return f"""APP_NAME={display}
APP_ENV=local
APP_DEBUG=true
APP_URL=http://127.0.0.1:3000
"""


def _readme(name: str, display: str) -> str:
    return f"""# {display}

Avalon application generated with `avalon new {name}`.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python grail serve
```

Open http://127.0.0.1:3000

In-app commands use `python grail …`. Create more apps with `avalon new`.
"""


def _pyproject(name: str, display: str) -> str:
    return f"""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{name}"
version = "0.1.0"
description = "{display} — Avalon application"
requires-python = ">=3.11"
dependencies = [
    "avalon",
]

[tool.hatch.build.targets.wheel]
packages = ["app", "bootstrap", "config", "routes"]
"""


def _bootstrap_app(display: str) -> str:
    return f'''"""Application entry — boots the Avalon kernel and exposes ASGI."""

from __future__ import annotations

from pathlib import Path

from avalon.framework import Application

BASE_PATH = Path(__file__).resolve().parent.parent

application = Application(BASE_PATH).bootstrap()
asgi = application.asgi
'''


def _config_app(display: str) -> str:
    return f'''"""Application configuration."""

from avalon.config import env

config = {{
    "name": env("APP_NAME", "{display}"),
    "env": env("APP_ENV", "local"),
    "debug": env("APP_DEBUG", True),
    "url": env("APP_URL", "http://127.0.0.1:3000"),
    "providers": [
        "app.Providers.AppServiceProvider.AppServiceProvider",
    ],
}}
'''


def _config_http() -> str:
    return '''"""HTTP kernel configuration."""

config = {
    "middleware": [],
    "middleware_aliases": {},
}
'''


def _app_service_provider() -> str:
    return '''"""Application service provider."""

from __future__ import annotations

from avalon.providers import ServiceProvider


class AppServiceProvider(ServiceProvider):
    def register(self) -> None:
        """Bind application services into the container."""

    def boot(self) -> None:
        """Bootstrap application services."""
'''


def _welcome_controller() -> str:
    return '''"""Welcome controller."""

from __future__ import annotations

from avalon.config import config
from avalon.http import Controller


class WelcomeController(Controller):
    async def index(self) -> dict[str, str]:
        return {
            "message": "Welcome to Avalon",
            "app": str(config("app.name", "Avalon")),
            "docs": "See docs/PLAN.md in the framework repository",
        }
'''


def _routes_web() -> str:
    return '''"""Web routes."""

from app.Http.Controllers.WelcomeController import WelcomeController
from avalon.routing import Route

Route.get("/", [WelcomeController, "index"])
'''


def _routes_api() -> str:
    return '''"""API routes."""

from avalon.routing import Route

# Route.get("/api/health", [HealthController, "index"])
'''
