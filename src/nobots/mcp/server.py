"""MCP server exposing detect/analyze/score/humanize as tools. Requires [mcp]."""

import importlib.util

from mcp.server.fastmcp import FastMCP

from nobots.core.detect import detect_text
from nobots.core.prose import clean_prose

mcp = FastMCP("nobots")


@mcp.tool()
def detect(text: str) -> dict:
    """Quorum tell-scan for AI-sounding prose. Always available."""
    result = detect_text(clean_prose(text))
    return {
        "tells_found": result.tells_found,
        "agree": result.agree,
        "quorum": result.quorum,
        "summary": result.summary,
        "families": {k: {"vote": v[0], "detail": v[1]} for k, v in result.families.items()},
        "context": result.context,
    }


@mcp.tool()
def analyze(text: str) -> dict:
    """Deep stylometry report. Requires the [analyze] extra."""
    try:
        from nobots.core.stylometry import analyze_text
    except ImportError:
        return {"error": "analyze needs the analyze extra: uv sync --extra analyze"}
    try:
        return analyze_text(clean_prose(text))
    except ImportError:
        # analyze_text imports textdescriptives lazily, so the top-level import
        # above can succeed even when [analyze] isn't installed.
        return {"error": "analyze needs the analyze extra: uv sync --extra analyze"}


@mcp.tool()
def score(text: str) -> dict:
    """Model-based detector scores. First run downloads ~5GB. Requires [models]."""
    try:
        from nobots.core.models import score_text
    except ImportError:
        return {"error": "score needs the models extra: uv sync --extra models"}
    # score_text imports torch lazily, so the top-level import above succeeds even
    # when [models] isn't installed; probe explicitly so we still emit the hint.
    if importlib.util.find_spec("torch") is None or importlib.util.find_spec("transformers") is None:
        return {"error": "score needs the models extra: uv sync --extra models"}
    return score_text(clean_prose(text))


@mcp.tool()
def humanize(text: str) -> str:
    """Rewrite text to sound less AI-generated. Requires the [humanize] extra."""
    try:
        from nobots.humanize.agent import build_default_model, humanize_text
    except ImportError:
        return "error: humanize needs the humanize extra: uv sync --extra humanize"
    try:
        model = build_default_model()
        return humanize_text(text, model=model)
    except (ModuleNotFoundError, ImportError):
        return "error: humanize needs the humanize extra: uv sync --extra humanize"
    except RuntimeError as e:
        return f"error: {e}"


def run_server() -> None:
    mcp.run()
