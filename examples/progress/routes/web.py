"""Web routes."""

from app.Http.Controllers.ProgressController import ProgressController
from app.Http.Controllers.WelcomeController import WelcomeController
from avalon.routing import Route

Route.get("/", [WelcomeController, "index"])
Route.get("/progress", [ProgressController, "index"])
