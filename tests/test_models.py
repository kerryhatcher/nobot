import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("NOBOTS_MODEL_TESTS") != "1",
    reason="model tests are slow (download ~5GB); set NOBOTS_MODEL_TESTS=1 to run",
)

HUMAN = (
    "I broke the build again yesterday. Classic. The fix took four minutes; finding "
    "it took two hours because the error pointed at the wrong file entirely."
)
AI = (
    "In today's rapidly evolving landscape, we must delve into the multifaceted "
    "tapestry of innovation to leverage seamless, holistic, transformative synergy."
)


def test_score_text_all_detectors_finite_and_in_range():
    from nobots.core.models import score_text

    for sample in (HUMAN, AI):
        scores = score_text(sample)
        assert set(scores) == {"binoculars", "fast_detectgpt", "gltr", "roberta"}
        roberta = scores["roberta"]
        if isinstance(roberta, dict):
            assert 0.0 <= roberta["p_ai"] <= 1.0
        gltr = scores["gltr"]
        if isinstance(gltr, dict):
            frac = gltr["top_k_fractions"]
            assert frac["top_10"] <= frac["top_100"] <= frac["top_1000"]  # monotonic buckets


def test_one_failing_detector_does_not_kill_the_rest(monkeypatch):
    import nobots.core.models as m

    def boom(text):
        raise RuntimeError("simulated failure")

    monkeypatch.setattr(m, "binoculars", boom)
    scores = m.score_text("some prose here for scoring")
    assert isinstance(scores["binoculars"], str) and scores["binoculars"].startswith("ERR")
    assert isinstance(scores["roberta"], dict) or isinstance(scores["roberta"], str)
