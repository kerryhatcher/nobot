import pytest

pytest.importorskip("pydantic_ai")

from pydantic_ai.models.test import TestModel

from nobots.humanize.agent import humanize_text


def test_humanize_invokes_model_and_returns_text():
    # TestModel returns canned output without any network/LLM call.
    result = humanize_text("Delve into the multifaceted tapestry of synergy.", model=TestModel())
    assert isinstance(result, str)
    assert len(result) > 0
