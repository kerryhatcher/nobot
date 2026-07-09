# src/nobots/cli.py
"""Typer CLI. Owns exit codes, --json, and missing-extra install hints."""

import importlib.util
import json
from pathlib import Path

import typer

app = typer.Typer(add_completion=False, help="Detect, analyze, and humanize prose.")


def _read(file: Path) -> str:
    return file.read_text(encoding="utf-8", errors="ignore")


def _missing_extra(extra: str, cmd: str) -> typer.Exit:
    typer.echo(
        f"{cmd} needs the {extra} extra: "
        f"uvx --from 'nobots[{extra}]' nobots {cmd}",
        err=True,
    )
    return typer.Exit(code=1)


@app.command()
def detect(
    file: Path = typer.Argument(..., exists=False),
    json_out: bool = typer.Option(False, "--json", help="Emit families + scores as JSON to stdout."),
):
    """Quorum tell-scan. Exit 0 clean / 2 tells found. Fails open on any error."""
    try:
        from nobots.core.detect import detect_text
        from nobots.core.prose import clean_prose

        if not file.is_file() or file.suffix.lower() not in {".md", ".markdown", ".txt"}:
            raise typer.Exit(code=0)
        result = detect_text(clean_prose(_read(file)))
        if json_out:
            typer.echo(json.dumps({
                "file": str(file),
                "tells_found": result.tells_found,
                "agree": result.agree,
                "quorum": result.quorum,
                "families": {k: {"vote": v[0], "detail": v[1]} for k, v in result.families.items()},
                "context": result.context,
            }, indent=2))
        elif result.tells_found:
            typer.echo(f"nobots: {file} {result.summary}", err=True)
        raise typer.Exit(code=2 if result.tells_found else 0)
    except typer.Exit:
        raise
    except Exception:
        raise typer.Exit(code=0)  # fail open — a hook bug must never block a Write/Edit


@app.command()
def analyze(file: Path = typer.Argument(...), json_out: bool = typer.Option(False, "--json")):
    """Deep stylometry report (raw numbers). Requires the [analyze] extra."""
    try:
        from nobots.core.stylometry import analyze_text
    except ImportError:
        raise _missing_extra("analyze", "analyze")
    from nobots.core.prose import clean_prose

    if not file.is_file():
        typer.echo(f"file not found: {file}", err=True)
        raise typer.Exit(code=1)
    try:
        report = analyze_text(clean_prose(_read(file)), doc_id=str(file))
    except ImportError:
        raise _missing_extra("analyze", "analyze")
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1)
    typer.echo(json.dumps(report, indent=2))


@app.command()
def score(
    file: Path = typer.Argument(...),
    json_out: bool = typer.Option(False, "--json"),
    chunk: bool = typer.Option(False, "--chunk", help="Average over prose windows for long input."),
    words: int = typer.Option(300, "--words", help="Window size for --chunk."),
):
    """Model-based detector scores. First run downloads ~5GB. Requires [models]."""
    try:
        from nobots.core.models import score_text
    except ImportError:
        raise _missing_extra("models", "score")
    # score_text imports torch lazily, so the top-level import above succeeds even
    # when [models] isn't installed; probe explicitly so we still emit the hint.
    if importlib.util.find_spec("torch") is None or importlib.util.find_spec("transformers") is None:
        raise _missing_extra("models", "score")
    from nobots.core.prose import clean_prose, prose_windows

    if not file.is_file():
        typer.echo(f"file not found: {file}", err=True)
        raise typer.Exit(code=1)
    prose = clean_prose(_read(file))
    if chunk:
        results = [score_text(w) for w in prose_windows(prose, words=words)]
        out = {"windows": results, "n_windows": len(results)}
    else:
        out = score_text(prose)
    typer.echo(json.dumps(out, indent=2, default=str))


@app.command()
def humanize(
    file: Path = typer.Argument(...),
    model: str = typer.Option(None, "--model", help="Pydantic AI model id override."),
    in_place: bool = typer.Option(False, "--in-place", help="Overwrite the file with the rewrite."),
):
    """Pydantic AI rewrite. Default Ollama; hard-errors if Ollama down. Requires [humanize]."""
    try:
        from nobots.humanize.agent import build_default_model, humanize_text
    except ImportError:
        raise _missing_extra("humanize", "humanize")
    from nobots.config import humanize_settings

    if not file.is_file():
        typer.echo(f"file not found: {file}", err=True)
        raise typer.Exit(code=1)
    settings = humanize_settings(cli_model=model)
    try:
        built = build_default_model(settings)
        rewritten = humanize_text(_read(file), model=built)
    except (ModuleNotFoundError, ImportError):
        # build_default_model imports pydantic_ai lazily, so a missing [humanize]
        # extra surfaces here rather than at the top-level import above.
        raise _missing_extra("humanize", "humanize")
    except RuntimeError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1)
    if in_place:
        file.write_text(rewritten, encoding="utf-8")
        typer.echo(f"rewrote {file}", err=True)
    else:
        typer.echo(rewritten)


@app.command()
def tui():
    """Live TUI for AI-tell detection. Requires [tui]."""
    try:
        from nobots.tui.app import run_tui
    except ImportError:
        raise _missing_extra("tui", "tui")
    run_tui()


@app.callback()
def _root(
    guide: bool = typer.Option(False, "--guide", help="Print the packaged field guide and exit."),
):
    if guide:
        from nobots.core.guide import load_guide

        typer.echo(load_guide())
        raise typer.Exit(code=0)
