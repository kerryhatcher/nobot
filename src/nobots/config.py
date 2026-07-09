"""~/.config/nobots/config.toml loader. Precedence: CLI flag > config > default."""

import tomllib
from pathlib import Path

_DEFAULTS = {
    "provider": "ollama",
    "model": "llama3.1",
    "base_url": "http://localhost:11434/v1",
}


def _config_path() -> Path:
    return Path.home() / ".config" / "nobots" / "config.toml"


def load_config() -> dict:
    path = _config_path()
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def humanize_settings(cli_model: str | None = None, cli_base_url: str | None = None) -> dict:
    settings = dict(_DEFAULTS)
    settings.update(load_config().get("humanize", {}))
    if cli_model:
        settings["model"] = cli_model
    if cli_base_url:
        settings["base_url"] = cli_base_url
    return settings
