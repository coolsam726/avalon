"""Application entry — boots the Avalon kernel and exposes ASGI."""

from __future__ import annotations

from pathlib import Path

from app.http.middleware.demo_tag_middleware import DemoTagMiddleware

from avalon.framework import Application, Middleware
from avalon.translation import SetLocaleMiddleware

BASE_PATH = Path(__file__).resolve().parent.parent


def configure_middleware(middleware: Middleware) -> None:
    """Register HTTP middleware (Laravel ``bootstrap/app.php`` shape)."""
    # Behind a load balancer / ingress (from avalon.http import HEADER_X_FORWARDED_ALL):
    # middleware.trust_proxies(at="*", headers=HEADER_X_FORWARDED_ALL)
    # middleware.trust_hosts(at=["example.com", "*.example.com"])
    middleware.alias(
        {
            "locale": SetLocaleMiddleware,
            "demo.tag": DemoTagMiddleware,
        }
    )
    middleware.web(append=["locale"])
    middleware.api(append=["locale", "demo.tag"])


application = (
    Application.configure(BASE_PATH)
    .with_middleware(configure_middleware)
    .create()
)
asgi = application.asgi
