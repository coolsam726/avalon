"""Demo Support helpers + Str in the living example."""

from __future__ import annotations

from avalon.console.command import Command
from avalon.support import Arr, Number, Str, blank, str_


class ProgressHelpersCommand(Command):
    signature = "progress:helpers"
    description = "Demo Arr / Str / Number helpers (M14)"

    def handle(self) -> int:
        payload = {"user": {"name": "Ada", "roles": ["admin", "editor"]}}
        self.info(f"data path → {Arr.get(payload, 'user.name')}")
        self.info(f"slug → {Str.slug('Hello Avalon Framework')}")
        self.info(f"fluent → {str_('foo_bar').camel()}")
        self.info(f"ordinal → {Number.ordinal(3)}")
        self.info(f"blank('') → {blank('')}")
        self.line(Str.of("m14").upper().prepend("SHIPPED ").to_string())
        return 0
