"""Shared test helpers (safe to import from any test module)."""

from __future__ import annotations

import sys


def purge_generated_app_modules() -> None:
    """Drop scaffolded ``app`` / ``bootstrap`` modules between tests."""
    for key in list(sys.modules):
        if key == "bootstrap" or key.startswith("bootstrap.") or key == "app" or key.startswith(
            "app."
        ):
            del sys.modules[key]
