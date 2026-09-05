"""Discover and run Avalon console commands."""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import pkgutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer

from avalon.console.command import Command, parse_signature

if TYPE_CHECKING:
    from avalon.framework.application import Application


class ConsoleKernel:
    """Registers Command subclasses and runs them with M8 exception reporting."""

    def __init__(self, app: Application) -> None:
        self.app = app
        self.commands: dict[str, type[Command]] = {}

    @classmethod
    def from_cwd(cls, cwd: Path | None = None) -> ConsoleKernel:
        from avalon.framework.application import Application

        root = Path(cwd or Path.cwd())
        application = Application(root)
        application.load_environment()
        application.load_configuration()
        application.apply_middleware_callbacks()
        application.register_configured_providers()
        application.boot()
        application._bootstrapped = True  # noqa: SLF001
        kernel = cls(application)
        kernel.discover()
        return kernel

    def discover(self) -> None:
        self._load_package("avalon.console.commands")
        self._load_package("app.console.commands")
        self._load_path(self.app.path("app", "console", "commands"))

    def register(self, command_cls: type[Command]) -> None:
        if not command_cls.signature:
            return
        self.commands[command_cls.name()] = command_cls

    def _load_package(self, package_name: str) -> None:
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            return
        paths = list(getattr(package, "__path__", []))
        for module_info in pkgutil.iter_modules(paths):
            module = importlib.import_module(f"{package_name}.{module_info.name}")
            self._register_module(module)

    def _load_path(self, directory: Path) -> None:
        if not directory.is_dir():
            return
        for file in sorted(directory.glob("*.py")):
            if file.name.startswith("_"):
                continue
            module_name = f"avalon_app_command_{file.stem}_{abs(hash(file))}"
            spec = importlib.util.spec_from_file_location(module_name, file)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            self._register_module(module)

    def _register_module(self, module: Any) -> None:
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Command) and obj is not Command and obj.signature:
                self.register(obj)

    def load_console_routes(self) -> None:
        path = self.app.path("routes", "console.py")
        if not path.is_file():
            return
        module_name = f"avalon_console_routes_{abs(hash(path))}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            return
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

    def run_command(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
    ) -> int:
        command_cls = self.commands.get(name)
        if command_cls is None:
            raise KeyError(f"Command not found: {name}")
        instance = command_cls(self.app)
        try:
            return instance.run(arguments=arguments, options=options)
        except Exception as exc:
            from avalon.debug import DumpAndDie

            if isinstance(exc, DumpAndDie):
                # dd() already pretty-printed; exit cleanly (not an app error).
                return 0
            self._report_exception(exc)
            raise

    def run_argv(self, name: str, argv: list[str]) -> int:
        command_cls = self.commands.get(name)
        if command_cls is None:
            raise KeyError(f"Command not found: {name}")
        _, arguments_meta, options_meta = parse_signature(command_cls.signature)
        arguments, options = _parse_argv(argv, arguments_meta, options_meta)
        return self.run_command(name, arguments=arguments, options=options)

    def _report_exception(self, exc: BaseException) -> None:
        try:
            from avalon.exceptions.handler import Handler

            if self.app.container.bound(Handler):
                handler = self.app.make(Handler)
            else:
                handler = Handler(self.app)
            handler.report(exc)
        except Exception:
            pass
        typer.secho(f"{type(exc).__name__}: {exc}", fg=typer.colors.RED, err=True)

    def register_on_typer(self, typer_app: typer.Typer) -> None:
        existing = {cmd.name for cmd in typer_app.registered_commands}
        for name, command_cls in sorted(self.commands.items()):
            if command_cls.hidden or name in existing:
                continue
            self._attach(typer_app, command_cls)

    def _attach(self, typer_app: typer.Typer, command_cls: type[Command]) -> None:
        name = command_cls.name()

        def callback(ctx: typer.Context) -> None:
            code = self.run_argv(name, list(ctx.args))
            if code:
                raise typer.Exit(code=code)

        callback.__doc__ = command_cls.description or command_cls.__doc__
        typer_app.command(
            name=name,
            help=command_cls.description or None,
            context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
        )(callback)


def _parse_argv(
    argv: list[str],
    arguments_meta: list[dict[str, Any]],
    options_meta: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    options: dict[str, Any] = {
        opt["name"].replace("-", "_"): (False if opt["is_flag"] else opt["default"])
        for opt in options_meta
    }
    positional: list[str] = []
    index = 0
    while index < len(argv):
        token = argv[index]
        if token.startswith("--"):
            key = token[2:]
            if "=" in key:
                key, value = key.split("=", 1)
                options[key.replace("-", "_")] = value
            else:
                meta = next((o for o in options_meta if o["name"] == key), None)
                if meta and meta["is_flag"]:
                    options[key.replace("-", "_")] = True
                elif index + 1 < len(argv) and not argv[index + 1].startswith("-"):
                    options[key.replace("-", "_")] = argv[index + 1]
                    index += 1
                else:
                    options[key.replace("-", "_")] = True
        else:
            positional.append(token)
        index += 1

    arguments: dict[str, Any] = {}
    pos_index = 0
    for meta in arguments_meta:
        key = meta["name"].replace("-", "_")
        if meta["variadic"]:
            arguments[key] = positional[pos_index:]
            pos_index = len(positional)
            break
        if pos_index < len(positional):
            arguments[key] = positional[pos_index]
            pos_index += 1
        elif meta["default"] is not None:
            arguments[key] = meta["default"]
        elif meta["optional"]:
            arguments[key] = None
        else:
            raise typer.BadParameter(f"Missing required argument: {meta['name']}")
    return arguments, options
