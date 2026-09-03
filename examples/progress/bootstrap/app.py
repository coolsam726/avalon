"""Application entry — boots the Avalon kernel and exposes ASGI."""

from __future__ import annotations

from pathlib import Path

from avalon.framework import Application

BASE_PATH = Path(__file__).resolve().parent.parent

application = Application(BASE_PATH).bootstrap()
asgi = application.asgi
