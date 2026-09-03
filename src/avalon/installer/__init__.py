"""Installer CLI (`avalon new`, …)."""

from avalon.installer.cli import app
from avalon.installer.scaffold import ScaffoldError, scaffold_app

__all__ = ["ScaffoldError", "app", "scaffold_app"]
