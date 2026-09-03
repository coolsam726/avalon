"""Locked M2 public contracts — HTTP + routing."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from avalon.http import Controller, HttpKernel, Middleware, Request, UploadedFile
from avalon.installer.scaffold import scaffold_app
from avalon.routing import Route, Router

pytestmark = [pytest.mark.regression]


def test_m2_public_exports() -> None:
    assert Controller is not None
    assert Middleware is not None
    assert Request is not None
    assert UploadedFile is not None
    assert HttpKernel is not None
    assert Route is not None
    assert Router is not None
    assert hasattr(Request, "all")
    assert hasattr(Request, "only")
    assert hasattr(Request, "except_")
    assert hasattr(Request, "create")


def test_scaffold_m2_bootstrap_has_no_fastapi(tmp_path: Path) -> None:
    root = scaffold_app("m2_contract", destination=tmp_path / "m2_contract")
    bootstrap = (root / "bootstrap" / "app.py").read_text(encoding="utf-8")
    web = (root / "routes" / "web.py").read_text(encoding="utf-8")
    assert "from fastapi" not in bootstrap
    assert "asgi = application.asgi" in bootstrap
    assert "Route.get" in web
    assert (root / "config" / "http.py").exists()


def test_scaffolded_app_serves_via_route_dsl(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from tests.support import purge_generated_app_modules
    import importlib

    root = scaffold_app("m2_serve", destination=tmp_path / "m2_serve")
    purge_generated_app_modules()
    monkeypatch.chdir(root)
    monkeypatch.syspath_prepend(str(root))
    monkeypatch.delenv("APP_NAME", raising=False)
    try:
        module = importlib.import_module("bootstrap.app")
        client = TestClient(module.asgi)
        payload = client.get("/").json()
        assert payload["app"] == "M2Serve"
        assert "Welcome to Avalon" in payload["message"]
    finally:
        purge_generated_app_modules()
