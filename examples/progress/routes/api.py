"""API routes — second routes file loaded by Application.load_routes()."""

from app.Http.Controllers.DemoController import DemoController
from avalon.routing import Route

with Route.group(prefix="/api", middleware=["demo.tag"]):
    Route.get("/health", [DemoController, "ping"])
    Route.match(["GET", "POST"], "/echo/{item}", [DemoController, "show"])
