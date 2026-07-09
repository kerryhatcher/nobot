"""Load packaged field-guide markdown for MCP/skills/--guide."""

from importlib.resources import files


def load_guide() -> str:
    return files("nobots.data").joinpath("ai-writing-guide.md").read_text(encoding="utf-8")


def load_detection_tools() -> str:
    return files("nobots.data").joinpath("ai-detection-tools.md").read_text(encoding="utf-8")
