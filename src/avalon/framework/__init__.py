"""Application kernel: Application, IoC container, boot lifecycle."""

from avalon.framework.application import Application
from avalon.framework.container import Container, ResolutionError

__all__ = ["Application", "Container", "ResolutionError"]
