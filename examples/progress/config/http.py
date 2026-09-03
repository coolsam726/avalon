"""HTTP kernel configuration."""

from app.Http.Middleware.DemoTagMiddleware import DemoTagMiddleware

config = {
    "middleware": [],
    "middleware_aliases": {
        "demo.tag": DemoTagMiddleware,
    },
}
