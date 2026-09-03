"""M2 smoke — Avalon Route DSL without FastAPI imports in app code."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from avalon.installer.cli import app as avalon_app
from avalon.installer.scaffold import scaffold_app
from tests.support import purge_generated_app_modules

pytestmark = [pytest.mark.smoke, pytest.mark.regression]

runner = CliRunner()


def test_m2_s1_scaffold_uses_route_dsl(tmp_path: Path) -> None:
    result = runner.invoke(avalon_app, ["new", "route_app", "--path", str(tmp_path)])
    assert result.exit_code == 0, result.stdout
    root = tmp_path / "route_app"
    web = (root / "routes" / "web.py").read_text(encoding="utf-8")
    bootstrap = (root / "bootstrap" / "app.py").read_text(encoding="utf-8")
    assert "Route.get" in web
    assert "from fastapi" not in bootstrap
    assert "application.asgi" in bootstrap
    assert (root / "config" / "http.py").is_file()


def test_m2_s2_progress_routes_via_kernel(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Use the real progress example path relative to repo when available;
    # otherwise scaffold a fresh app with routes.
    root = scaffold_app("m2_smoke", destination=tmp_path / "m2_smoke")
    purge_generated_app_modules()
    monkeypatch.chdir(root)
    monkeypatch.syspath_prepend(str(root))
    monkeypatch.delenv("APP_NAME", raising=False)
    try:
        module = importlib.import_module("bootstrap.app")
        assert module.application.is_bootstrapped
        client = TestClient(module.asgi)
        response = client.get("/")
        assert response.status_code == 200
        assert "Welcome to Avalon" in response.json()["message"]
        # Ensure no FastAPI in generated bootstrap
        assert "from fastapi" not in (root / "bootstrap" / "app.py").read_text(encoding="utf-8")
    finally:
        purge_generated_app_modules()
