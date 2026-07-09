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


def test_score_degrades_without_extra() -> None:
    out = score("some text")
    assert "error" in out


def test_humanize_degrades_without_extra() -> None:
    out = humanize("some text")
    assert out.startswith("error:")
