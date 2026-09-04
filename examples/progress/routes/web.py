"""Web routes — browser facing, stateful, HTML responses."""

from app.http.controllers.progress_controller import ProgressController
from app.http.controllers.showcase_controller import ShowcaseController
from app.http.controllers.welcome_controller import WelcomeController

from avalon.routing import Route

with Route.group(middleware=["web"]):
    Route.get("/", [WelcomeController, "index"])
    Route.get("/progress", [ProgressController, "index"])
    Route.get("/showcase", [ShowcaseController, "index"])
