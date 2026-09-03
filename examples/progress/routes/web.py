"""Web routes."""

from app.Http.Controllers.DemoController import DemoController
from app.Http.Controllers.ProgressController import ProgressController
from app.Http.Controllers.WelcomeController import WelcomeController
from avalon.routing import Route

Route.get("/", [WelcomeController, "index"])
Route.get("/progress", [ProgressController, "index"])

# M2 surface: group prefix + middleware alias + HTTP verbs
with Route.group(prefix="/demo", middleware=["demo.tag"]):
    Route.get("/ping", [DemoController, "ping"])
    Route.get("/items/{item}", [DemoController, "show"])
    Route.post("/items", [DemoController, "store"])
    Route.get("/bag", [DemoController, "echo_bag"])
    Route.post("/bag", [DemoController, "echo_bag"])
    Route.get("/di", [DemoController, "with_config"])
    Route.put("/items/{item}", [DemoController, "update"])
    Route.patch("/items/{item}", [DemoController, "patch"])
    Route.delete("/items/{item}", [DemoController, "destroy"])
    Route.options("/probe", [DemoController, "options_probe"])
    Route.get("/boom", [DemoController, "boom"])
    Route.get("/missing", [DemoController, "missing"])
