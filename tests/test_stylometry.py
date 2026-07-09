import pytest

spacy = pytest.importorskip("spacy")  # skip whole module without the [analyze] extra

from nobots.core.stylometry import analyze_text

SAMPLE = (
    "The morning started badly. I spilled coffee on the keyboard, and the space bar "
    "stuck for the rest of the day. Still, we shipped the release on time. Barely. "
    "The team pulled together, reviewed forty files, and caught two real bugs before "
    "they reached production. Not bad for a Tuesday that began with a soaked laptop."
)


def test_analyze_text_returns_expected_keys():
    report = analyze_text(SAMPLE)
    assert set(report) >= {"word_count", "textdescriptives", "biber_features", "notes"}
    assert report["word_count"] == len(SAMPLE.split())
    td = report["textdescriptives"]
    assert "descriptive_stats" in td and "readability" in td and "derived" in td
    burst = td["derived"]["burstiness_ratio"]
    assert burst is None or burst >= 0


def test_analyze_text_rejects_short_input():
    with pytest.raises(ValueError):
        analyze_text("too short")
