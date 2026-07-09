import pytest

pytest.importorskip("mcp")

from nobots.mcp.server import analyze, detect, humanize, mcp, score

AI_SAMPLE = (
    "In today's rapidly evolving landscape, we must delve into the multifaceted "
    "tapestry of innovation. This is a testament to progress. It underscores the "
    "importance of synergy. Furthermore, we leverage seamless solutions — every day "
    "— to foster growth — across teams — and streamline outcomes — at scale — for "
    "all. Moreover, this pivotal moment cannot be overstated. It is important to "
    "note that we embark on a journey. We utilize holistic frameworks. We showcase "
    "meticulous care. We emphasize intricate detail. Nevertheless, the paramount "
    "goal remains. It plays a crucial role. This marks a pivotal moment for us all."
)


def test_all_four_tools_registered() -> None:
    names = {t.name for t in mcp._tool_manager.list_tools()}
    assert names == {"detect", "analyze", "score", "humanize"}


def test_detect_always_works() -> None:
    result = detect(AI_SAMPLE)
    assert result["tells_found"] is True
    assert result["agree"] >= result["quorum"]


def test_analyze_degrades_without_extra() -> None:
    out = analyze(AI_SAMPLE)
    assert "error" in out
    assert "uvx --from 'nobots[" in out["error"]
    assert "uv sync" not in out["error"]


def test_score_degrades_without_extra() -> None:
    out = score("some text")
    assert "error" in out
    assert "uvx --from 'nobots[" in out["error"]
    assert "uv sync" not in out["error"]


def test_humanize_hint_uses_uvx_form_when_extra_missing() -> None:
    try:
        import pydantic_ai  # noqa: F401

        pytest.skip("[humanize] is installed; degrade path not exercised")
    except ImportError:
        pass
    out = humanize("some text")
    assert out.startswith("error:")
    assert "uvx --from 'nobots[" in out
    assert "uv sync" not in out


def test_humanize_uses_config_settings() -> None:
    pytest.importorskip("pydantic_ai")
    from unittest.mock import patch

    sentinel_settings = {"provider": "ollama", "model": "sentinel-model", "base_url": "http://sentinel:1234/v1"}
    with (
        patch("nobots.config.humanize_settings", return_value=sentinel_settings) as mock_settings,
        patch("nobots.humanize.agent.build_default_model") as mock_build,
        patch("nobots.humanize.agent.humanize_text", return_value="rewritten") as mock_humanize,
    ):
        result = humanize("some text")

    mock_settings.assert_called_once_with()
    mock_build.assert_called_once_with(sentinel_settings)
    mock_humanize.assert_called_once_with("some text", model=mock_build.return_value)
    assert result == "rewritten"
