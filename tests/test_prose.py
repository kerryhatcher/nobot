from nobots.core.prose import clean_prose, prose_windows


def test_clean_prose_strips_frontmatter_code_and_markup():
    text = (
        "---\n"
        "title: My Doc\n"
        "---\n"
        "# Heading\n\n"
        "Real sentence one with a [link](http://x) and `inline`.\n\n"
        "```python\n"
        "print('code should vanish')\n"
        "```\n\n"
        "<!-- a comment -->\n"
        "| col | col |\n"
        "| --- | --- |\n"
        "| a   | b   |\n\n"
        "Real sentence two."
    )
    out = clean_prose(text)
    assert "title: My Doc" not in out
    assert "code should vanish" not in out
    assert "a comment" not in out
    assert "col" not in out
    assert "http://x" not in out
    assert "Real sentence one" in out
    assert "link" in out          # link *text* is kept
    assert "Real sentence two." in out


def test_prose_windows_splits_at_word_count():
    text = " ".join(str(i) for i in range(650))
    windows = prose_windows(text, words=300)
    assert len(windows) == 3
    assert len(windows[0].split()) == 300
    assert len(windows[1].split()) == 300
    assert len(windows[2].split()) == 50


def test_prose_windows_empty_returns_empty():
    assert prose_windows("   \n  ") == []
