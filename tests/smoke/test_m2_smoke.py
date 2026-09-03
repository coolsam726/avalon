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


def test_m2_s3_progress_example_exhausts_http_surface(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Living example: groups, middleware, verbs, Request, HttpException."""
    root = Path(__file__).resolve().parents[2] / "examples" / "progress"
    assert root.is_dir(), f"missing progress example at {root}"
    purge_generated_app_modules()
    monkeypatch.chdir(root)
    monkeypatch.syspath_prepend(str(root))
    monkeypatch.delenv("APP_NAME", raising=False)
    try:
        module = importlib.import_module("bootstrap.app")
        client = TestClient(module.asgi, raise_server_exceptions=False)

        home = client.get("/")
        assert home.status_code == 200
        assert home.json()["links"]["demo_ping"] == "/demo/ping"

        board = client.get("/progress")
        assert board.status_code == 200
        assert board.json()["milestones"][2]["id"] == "M2"
        assert board.json()["milestones"][2]["status"] == "complete"

        ping = client.get("/demo/ping")
        assert ping.status_code == 200
        assert ping.json() == {"demo": "ping", "via": "controller"}
        assert ping.headers.get("x-avalon-demo") == "m2"
        assert ping.headers.get("x-avalon-path") == "/demo/ping"

        show = client.get("/demo/items/42?q=hello", headers={"Authorization": "Bearer secret"})
        assert show.status_code == 200
        assert show.json()["item"] == "42"
        assert show.json()["route"] == "42"
        assert show.json()["query"] == "hello"
        assert show.json()["bearer"] == "secret"
        assert show.json()["only_q"] == {"q": "hello"}

        created = client.post("/demo/items", json={"name": "avalon", "flag": True, "count": 2})
        assert created.status_code == 200
        assert created.json()["created"] is True
        assert created.json()["name"] == "avalon"
        assert created.json()["boolean_flag"] is True
        assert created.json()["integer_count"] == 2

        bag = client.post("/demo/bag?q=1", json={"name": "bag", "q": "body"})
        assert bag.status_code == 200
        assert bag.json()["all"]["q"] == "body"
        assert bag.json()["query"]["q"] == "1"
        assert bag.json()["post"]["name"] == "bag"
        assert bag.json()["has_name"] is True
        assert bag.json()["is_json"] is True

        di = client.get("/demo/di")
        assert di.status_code == 200
        assert di.json()["injected"] == "ConfigRepository"
        assert di.json()["app_name"]

        assert client.put("/demo/items/7").json() == {"updated": "7"}
        assert client.patch("/demo/items/7").json() == {"patched": "7"}
        assert client.delete("/demo/items/7").json() == {"deleted": "7"}
        assert client.options("/demo/probe").json()["allow"].startswith("GET")

        invalid = client.post("/demo/items", json={})
        assert invalid.status_code == 422
        assert invalid.json()["status"] == 422
        assert "name" in invalid.json()["errors"]

        boom = client.get("/demo/boom")
        assert boom.status_code == 418
        assert boom.json() == {"message": "Intentional demo failure", "status": 418}

        missing = client.get("/demo/missing")
        assert missing.status_code == 404
        assert missing.json()["message"] == "Demo resource not found"

        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.headers.get("x-avalon-demo") == "m2"
        assert client.get("/api/echo/9?q=api").json()["item"] == "9"

        assert "from fastapi" not in (root / "bootstrap" / "app.py").read_text(encoding="utf-8")
        assert "from fastapi" not in (root / "routes" / "web.py").read_text(encoding="utf-8")
    finally:
        purge_generated_app_modules()
