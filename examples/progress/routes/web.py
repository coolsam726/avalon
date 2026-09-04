"""Web routes — browser facing, stateful, HTML responses."""

from app.http.controllers.auth_controller import AuthController
from app.http.controllers.progress_controller import ProgressController
from app.http.controllers.showcase_controller import ShowcaseController
from app.http.controllers.welcome_controller import WelcomeController

from avalon.routing import Route

with Route.group(middleware=["web"]):
    Route.get("/", [WelcomeController, "index"])
    Route.get("/progress", [ProgressController, "index"])
    Route.get("/showcase", [ShowcaseController, "index"])
    Route.get("/login", [AuthController, "show_login"], middleware=["guest"])
    Route.post("/login", [AuthController, "login"], middleware=["guest"])
    Route.post("/logout", [AuthController, "logout"], middleware=["auth"])
    Route.get("/logout", [AuthController, "logout"], middleware=["auth"])
    Route.get("/confirm-password", [AuthController, "show_confirm"], middleware=["auth"])
    Route.post("/confirm-password", [AuthController, "confirm"], middleware=["auth"])
    Route.get(
        "/settings",
        [WelcomeController, "settings"],
        middleware=["auth", "password.confirm"],
    )
