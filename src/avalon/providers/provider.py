"""Base service provider."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from avalon.framework.application import Application


class ServiceProvider:
    def __init__(self, app: Application) -> None:
        self.app = app

    def register(self) -> None:
        """Bind services into the container."""

    def boot(self) -> None:
        """Run after all providers have registered."""
