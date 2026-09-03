"""M2 demo controller — exercises verbs, Request, and HttpException."""

from __future__ import annotations

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
            "query": request.input("q"),
            "method": request.method,
            "path": request.path,
            "bearer": request.bearer_token(),
        }

    async def store(self, request: Request) -> dict[str, object]:
        body = await request.json()
        if not isinstance(body, dict) or "name" not in body:
            raise UnprocessableEntityHttpException(
                "Validation failed",
                errors={"name": ["The name field is required."]},
            )
        return {"created": True, "name": body["name"]}

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
