"""Application entry — boots the Avalon kernel and exposes ASGI.

HTTP routing moves fully under Avalon in M2; until then FastAPI remains the ASGI surface.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from app.Http.Controllers.ProgressController import ProgressController
from app.Http.Controllers.WelcomeController import WelcomeController
from avalon.config import config
from avalon.framework import Application

BASE_PATH = Path(__file__).resolve().parent.parent

application = Application(BASE_PATH).bootstrap()

asgi = FastAPI(title=str(config("app.name", "Progress")))
_welcome = WelcomeController()
_progress = ProgressController()


@asgi.get("/")
async def welcome() -> dict:
    return await _welcome.index()


@asgi.get("/progress")
async def progress() -> dict:
    return await _progress.index()
