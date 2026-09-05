"""Command base — signature, IoC handle(), output helpers."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, ClassVar

from avalon.console.output import Output

if TYPE_CHECKING:
    from avalon.framework.application import Application

_ARG_RE = re.compile(
    r"\{(?P<name>[a-zA-Z_][\w-]*)(?P<option>\?)?(?P<variadic>\.\.\.)?(?:=(?P<default>[^}]+))?\}"
)
_OPT_RE = re.compile(
    r"\{--(?P<name>[a-zA-Z_][\w-]*)(?:=(?P<default>[^}]*))?\}"
)


class Command:
    """Laravel-shaped console command.

    Declare ``signature`` like ``inspire {name?} {--yell}`` and implement
    ``handle()``. Arguments/options are injected as attributes before handle runs.
    """

    signature: ClassVar[str] = ""
    description: ClassVar[str] = ""
    hidden: ClassVar[bool] = False

    def __init__(self, app: Application | None = None) -> None:
        self.app = app
        self.output = Output()
        self._arguments: dict[str, Any] = {}
        self._options: dict[str, Any] = {}

    @classmethod
    def name(cls) -> str:
        """Command name (first token of the signature)."""
        return (cls.signature or cls.__name__).split()[0]

    def argument(self, key: str, default: Any = None) -> Any:
        return self._arguments.get(key, default)

    def option(self, key: str, default: Any = None) -> Any:
        return self._options.get(key, default)

    def line(self, message: str = "") -> None:
        self.output.line(message)

    def info(self, message: str) -> None:
        self.output.info(message)

    def comment(self, message: str) -> None:
        self.output.comment(message)

    def warn(self, message: str) -> None:
        self.output.warn(message)

    def error(self, message: str) -> None:
        self.output.error(message)

    def success(self, message: str) -> None:
        self.output.success(message)

    def table(self, headers: list[str], rows: list[list[Any]]) -> None:
        self.output.table(headers, rows)

    def confirm(self, question: str, default: bool = False) -> bool:
        return self.output.confirm(question, default=default)

    def ask(self, question: str, default: str | None = None) -> str:
        """Laravel ``$this->ask()`` — styled text prompt."""
        from avalon.console.prompts import text

        return text(question, default="" if default is None else default)

    def secret(self, question: str) -> str:
        """Laravel ``$this->secret()`` — hidden input."""
        from avalon.console.prompts import password

        return password(question)

    def choice(
        self,
        question: str,
        choices: list[Any] | dict[Any, str],
        default: Any = None,
    ) -> Any:
        """Laravel ``$this->choice()`` — arrow-key select."""
        from avalon.console.prompts import select

        return select(question, choices, default=default)

    def anticipate(
        self,
        question: str,
        options: list[str],
        default: str | None = None,
    ) -> str:
        """Laravel ``$this->anticipate()`` — text with suggestions."""
        from avalon.console.prompts import suggest

        return suggest(question, options, default="" if default is None else default)

    def handle(self) -> int | None:
        """Execute the command. Return a process exit code (default 0)."""
        raise NotImplementedError(f"{type(self).__name__}.handle() is not implemented")

    def run(self, arguments: dict[str, Any] | None = None, options: dict[str, Any] | None = None) -> int:
        self._arguments = dict(arguments or {})
        self._options = dict(options or {})
        for key, value in self._arguments.items():
            setattr(self, key.replace("-", "_"), value)
        for key, value in self._options.items():
            setattr(self, key.replace("-", "_"), value)
        result = self.handle()
        if result is None:
            return 0
        return int(result)


def parse_signature(signature: str) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    """Parse a Laravel-style signature into name, arguments, and options."""
    parts = signature.split()
    if not parts:
        raise ValueError("Command signature must include a name")
    name = parts[0]
    arguments: list[dict[str, Any]] = []
    options: list[dict[str, Any]] = []
    for token in parts[1:]:
        opt = _OPT_RE.fullmatch(token)
        if opt:
            options.append(
                {
                    "name": opt.group("name"),
                    "default": opt.group("default"),
                    "is_flag": opt.group("default") is None,
                }
            )
            continue
        arg = _ARG_RE.fullmatch(token)
        if arg:
            arguments.append(
                {
                    "name": arg.group("name"),
                    "optional": bool(arg.group("option")),
                    "variadic": bool(arg.group("variadic")),
                    "default": arg.group("default"),
                }
            )
            continue
        raise ValueError(f"Invalid signature token: {token!r}")
    return name, arguments, options
