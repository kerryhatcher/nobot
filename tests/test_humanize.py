import pytest

pytest.importorskip("pydantic_ai")

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.test import TestModel
from pydantic_ai.providers.openai import OpenAIProvider

from nobots.humanize.agent import humanize_text


def test_humanize_invokes_model_and_returns_text():
    # TestModel returns canned output without any network/LLM call.
    result = humanize_text("Delve into the multifaceted tapestry of synergy.", model=TestModel())
    assert isinstance(result, str)
    assert len(result) > 0


def test_humanize_raises_runtime_error_when_ollama_unreachable():
    # Port 1 is a reserved/closed port -- connection fails immediately, no
    # 30s timeout, no real network dependency.
    provider = OpenAIProvider(base_url="http://127.0.0.1:1/v1", api_key="ollama")
    model = OpenAIChatModel("llama3.1", provider=provider)

    with pytest.raises(RuntimeError, match="Ollama"):
        humanize_text("Delve into the multifaceted tapestry of synergy.", model=model)
