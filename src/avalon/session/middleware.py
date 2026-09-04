"""Start the session for the ``web`` middleware group."""

from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.responses import Response as StarletteResponse

from avalon.http.middleware import Middleware, NextCall
from avalon.session.cookie import sign_payload, unsign_payload
from avalon.session.store import Session, reset_session, set_session

if TYPE_CHECKING:
    from avalon.http.request import Request


class StartSession(Middleware):
    """Load a signed session cookie, expose ``request.session``, persist on the way out."""

    cookie_name = "avalon_session"

    async def handle(self, request: Request, call_next: NextCall) -> StarletteResponse:
        from avalon.config import config

        key = str(config("app.key", "") or "")
        if not key:
            key = "avalon-insecure-dev-key-change-me"
        lifetime = int(config("session.lifetime", 120) or 120) * 60
        cookie_name = str(config("session.cookie", self.cookie_name) or self.cookie_name)

        raw = request.cookie(cookie_name)
        data = unsign_payload(raw, key=key, max_age=lifetime) if raw else None
        session = Session(data)
        if data is not None:
            session.age_flash()
        request._session = session  # noqa: SLF001
        token = set_session(session)
        try:
            response = await call_next(request)
        finally:
            reset_session(token)

        if session.dirty or data is not None:
            value = sign_payload(session.all(), key=key, max_age=lifetime)
            response.set_cookie(
                cookie_name,
                value,
                max_age=lifetime,
                httponly=True,
                samesite="lax",
                path=str(config("session.path", "/") or "/"),
                secure=bool(config("session.secure", False)),
            )
        return response
