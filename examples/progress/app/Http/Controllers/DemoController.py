"""M2 demo controller — Request bag, verbs, DI, and HttpException."""

from __future__ import annotations

from avalon.config import ConfigRepository
from avalon.http import (
    Controller,
    HttpException,
    NotFoundHttpException,
    Request,
    UnprocessableEntityHttpException,
)


class DemoController(Controller):
    async def ping(self) -> dict[str, str]:
        return {"demo": "ping", "via": "controller"}

    async def show(self, request: Request, item: str) -> dict[str, object]:
        return {
            "item": item,
            "route": request.route("item"),
            "query": request.query("q"),
            "all": request.all(),
            "only_q": request.only("q"),
            "method": request.method,
            "path": request.path,
            "bearer": request.bearer_token(),
            "ip": request.ip(),
            "is_get": request.is_method("GET"),
        }

    async def store(self, request: Request) -> dict[str, object]:
        if request.missing("name") or not request.filled("name"):
            raise UnprocessableEntityHttpException(
                "Validation failed",
                errors={"name": ["The name field is required."]},
            )
        return {
            "created": True,
            "name": request.string("name"),
            "post": request.post(),
            "only": request.only("name"),
            "except": request.except_("name"),
            "boolean_flag": request.boolean("flag"),
            "integer_count": request.integer("count"),
        }

    async def echo_bag(self, request: Request) -> dict[str, object]:
        """Inspect the full Laravel-style input surface for one request."""
        return {
            "all": request.all(),
            "query": request.query(),
            "post": request.post(),
            "json": request.json(),
            "route": request.route(),
            "keys": request.keys(),
            "has_name": request.has("name"),
            "has_any": request.has_any("name", "q"),
            "filled_name": request.filled("name") if request.has("name") else False,
            "missing_x": request.missing("x"),
            "headers_accept": request.header("accept"),
            "user_agent": request.user_agent(),
            "is_json": request.is_json(),
            "files": list(request.files().keys()),
        }

    async def with_config(self, config: ConfigRepository) -> dict[str, object]:
        """Proves type-hinted container resolution into controller actions."""
        return {
            "injected": "ConfigRepository",
            "app_name": str(config.get("app.name")),
        }

    async def update(self, item: str) -> dict[str, object]:
        return {"updated": item}

    async def patch(self, item: str) -> dict[str, object]:
        return {"patched": item}

    async def destroy(self, item: str) -> dict[str, object]:
        return {"deleted": item}

    async def options_probe(self) -> dict[str, str]:
        return {"allow": "GET,POST,PUT,PATCH,DELETE,OPTIONS"}

    async def boom(self) -> dict[str, str]:
        raise HttpException("Intentional demo failure", status_code=418)

    async def missing(self) -> dict[str, str]:
        raise NotFoundHttpException("Demo resource not found")
