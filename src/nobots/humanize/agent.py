"""Pydantic AI agent that rewrites prose to remove AI tells.

Default model is a local Ollama endpoint (OpenAI-compatible). Raises a clear
error if Ollama is unreachable. Requires the [humanize] extra.
"""

from nobots.core.guide import load_guide

_SYSTEM_PROMPT_HEAD = (
    "You rewrite prose so it reads as authentically human, removing the "
    "vocabulary, statistical, and structural fingerprints of machine writing. "
    "Return only the rewritten prose, no preamble. Rules and rationale:\n\n"
)


def _system_prompt() -> str:
    return _SYSTEM_PROMPT_HEAD + load_guide()


def build_default_model(settings: dict | None = None):
    """Build the default Ollama-backed Pydantic AI model; error if unreachable."""
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider

    settings = settings or {}
    model_name = settings.get("model", "llama3.1")
    base_url = settings.get("base_url", "http://localhost:11434/v1")
    try:
        provider = OpenAIProvider(base_url=base_url, api_key="ollama")
        return OpenAIChatModel(model_name, provider=provider)
    except Exception as e:
        raise RuntimeError(
            f"could not reach the humanize model at {base_url}: {e}. "
            "Is Ollama running? Start it with `ollama serve` or set "
            "[humanize] in ~/.config/nobots/config.toml."
        ) from e


def humanize_text(text: str, model=None) -> str:
    """Rewrite `text` to remove AI tells using a Pydantic AI agent."""
    from pydantic_ai import Agent

    if model is None:
        model = build_default_model()
    agent = Agent(model=model, system_prompt=_system_prompt())
    result = agent.run_sync(text)
    return result.output
