"""Locale demo — proves translator, plurals, Number, and Accept-Language."""

from __future__ import annotations

from avalon.http import Controller, Request
from avalon.translation import Number, __, get_locale, trans_choice


class LocaleController(Controller):
    async def index(self, request: Request) -> dict:
        count = int(request.input("count", 2) or 2)
        name = str(request.input("name", "Avalon") or "Avalon")
        return {
            "locale": get_locale(),
            "welcome": __("messages.welcome"),
            "hello": __("messages.hello", {"name": name}),
            "items": trans_choice("messages.items", count),
            "json": __("I love Avalon."),
            "number": Number.format(1234.5),
            "currency": Number.currency(99.5, "USD"),
            "humans": Number.for_humans(1_500_000, precision=1),
        }
