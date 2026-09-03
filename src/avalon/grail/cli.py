"""Grail — in-application CLI (Artisan equivalent).

Preferred usage from an app (or this repo) root::

    python grail version
    python grail serve
    python grail make:controller UserController

Project creation uses ``avalon new``, not Grail.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
import uvicorn

from avalon import __version__
from avalon.grail.ports import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    MAX_PORT,
    NoFreePortError,
    find_available_port,
)

app = typer.Typer(
    name="grail",
    help="Grail — Avalon in-app CLI (Artisan equivalent). Prefer: python grail …",
    no_args_is_help=True,
)

DEFAULT_ASGI = "bootstrap.app:asgi"


@app.callback()
def main() -> None:
    """Run application commands."""


@app.command("version")
def version() -> None:
    """Show Avalon version."""
    typer.echo(f"Avalon {__version__}")


@app.command("serve")
def serve(
    host: str = typer.Option(DEFAULT_HOST, help="Bind host"),
    port: Optional[int] = typer.Option(
        None,
        help=(
            f"Bind port (default: first free port from {DEFAULT_PORT}–{MAX_PORT}; "
            "if the chosen port is busy, try the next)"
        ),
    ),
    reload: bool = typer.Option(True, help="Auto-reload on code changes"),
    app_path: str = typer.Option(
        DEFAULT_ASGI,
        "--app",
        help="ASGI import path (default: bootstrap.app:asgi)",
    ),
) -> None:
    """Serve the application with Uvicorn.

    Defaults to port 3000. If that port is taken, tries 3001, 3002, … up to 3099
    (Laravel-style). Passing ``--port`` still auto-advances from that starting port.
    """
    module_file = Path.cwd() / "bootstrap" / "app.py"
    if app_path == DEFAULT_ASGI and not module_file.is_file():
        typer.secho(
            "No bootstrap/app.py found. Run this from an Avalon app created with "
            "`avalon new`, or pass --app IMPORT_PATH.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    start_port = DEFAULT_PORT if port is None else port
    # Default discovery window is 3000–3099 (100 ports). Explicit --port uses
    # the same window size starting from the requested port.
    window = MAX_PORT - DEFAULT_PORT
    end_port = start_port + window if start_port > MAX_PORT else max(start_port, MAX_PORT)

    try:
        chosen = find_available_port(host=host, start=start_port, end=end_port)
    except NoFreePortError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    if chosen != start_port:
        typer.secho(
            f"Port {start_port} is in use, using http://{host}:{chosen} instead.",
            fg=typer.colors.YELLOW,
        )

    typer.echo(f"Serving {app_path} on http://{host}:{chosen}")
    uvicorn.run(app_path, host=host, port=chosen, reload=reload)


if __name__ == "__main__":
    app()
