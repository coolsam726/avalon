"""Smoke — Cache façade boots in progress."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from avalon.grail.cli import app as grail_app
from tests.support import purge_generated_app_modules, without_base_path

pytestmark = [pytest.mark.smoke, pytest.mark.regression]

PROGRESS = Path(__file__).resolve().parents[2] / "examples" / "progress"
runner = CliRunner()


@pytest.fixture()
def progress_cwd(monkeypatch: pytest.MonkeyPatch) -> Path:
    without_base_path(monkeypatch)
    purge_generated_app_modules()
    monkeypatch.chdir(PROGRESS)
    monkeypatch.syspath_prepend(str(PROGRESS))
    from avalon.console.kernel import ConsoleKernel

    ConsoleKernel.from_cwd(PROGRESS).register_on_typer(grail_app)
    return PROGRESS


def test_m15_progress_cache_command(progress_cwd: Path) -> None:
    result = runner.invoke(grail_app, ["progress:cache"])
    assert result.exit_code == 0, result.stdout + result.stderr
    assert "cache demo ok" in result.stdout or "remember" in result.stdout.lower()
