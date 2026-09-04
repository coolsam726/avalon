from pathlib import Path

from typer.testing import CliRunner

from avalon.grail.cli import app as grail_app
from avalon.installer.cli import app as avalon_app
from avalon.installer.scaffold import ScaffoldError, scaffold_app, validate_app_name

runner = CliRunner()


def test_avalon_version() -> None:
    result = runner.invoke(avalon_app, ["version"])
    assert result.exit_code == 0
    assert "Avalon 0.1.0" in result.stdout


def test_avalon_new_creates_app(tmp_path: Path) -> None:
    result = runner.invoke(avalon_app, ["new", "demo_app", "--path", str(tmp_path)])
    assert result.exit_code == 0, result.stdout
    root = tmp_path / "demo_app"
    assert (root / "grail").is_file()
    assert (root / "bootstrap" / "app.py").is_file()
    assert (root / "app" / "http" / "controllers" / "welcome_controller.py").is_file()
    assert "Created Avalon application" in result.stdout


def test_avalon_new_rejects_existing(tmp_path: Path) -> None:
    scaffold_app("taken", destination=tmp_path / "taken")
    result = runner.invoke(avalon_app, ["new", "taken", "--path", str(tmp_path)])
    assert result.exit_code == 1


def test_grail_has_no_new_command() -> None:
    result = runner.invoke(grail_app, ["new", "demo"])
    assert result.exit_code != 0


def test_grail_version() -> None:
    result = runner.invoke(grail_app, ["version"])
    assert result.exit_code == 0
    assert "Avalon 0.1.0" in result.stdout


def test_grail_serve_requires_bootstrap(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(grail_app, ["serve"])
    assert result.exit_code == 1
    assert "bootstrap/app.py" in result.stderr


def test_validate_app_name() -> None:
    assert validate_app_name("blog") == "blog"
    try:
        validate_app_name("9bad")
        raise AssertionError("expected ScaffoldError")
    except ScaffoldError:
        pass
