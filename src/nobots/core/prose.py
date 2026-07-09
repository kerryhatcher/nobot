"""Prose preparation shared by every detector.

clean_prose reduces markdown/HTML noise to plain sentences so signals aren't
skewed by code, tables, or markup. prose_windows chunks long inputs so
model-based detectors can average over fixed-word windows. Pure, stdlib-only.
"""

import re

_FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
_FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)
_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")   # keep link text, drop the URL
_INLINE_CODE = re.compile(r"`[^`]*`")
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s*", re.MULTILINE)
_LIST_MARKER = re.compile(r"^\s{0,3}(?:[-*+]|\d+\.)\s+", re.MULTILINE)
_EMPHASIS = re.compile(r"(\*\*|__|\*|_|~~)")
_BLOCKQUOTE = re.compile(r"^\s{0,3}>\s?", re.MULTILINE)
_MULTISPACE = re.compile(r"[ \t]+")
_MULTINEWLINE = re.compile(r"\n{3,}")


def clean_prose(text: str) -> str:
    """Strip markdown/HTML noise, returning plain prose."""
    text = _FRONTMATTER.sub("", text)
    text = _FENCED_CODE.sub("", text)
    text = _HTML_COMMENT.sub("", text)
    text = _TABLE_ROW.sub("", text)
    text = _IMAGE.sub("", text)
    text = _LINK.sub(r"\1", text)
    text = _INLINE_CODE.sub("", text)
    text = _HEADING.sub("", text)
    text = _LIST_MARKER.sub("", text)
    text = _BLOCKQUOTE.sub("", text)
    text = _EMPHASIS.sub("", text)
    text = _MULTISPACE.sub(" ", text)
    text = _MULTINEWLINE.sub("\n\n", text)
    return text.strip()


def prose_windows(text: str, words: int = 300) -> list[str]:
    """Split text into consecutive windows of at most `words` words each."""
    tokens = text.split()
    if not tokens:
        return []
    return [" ".join(tokens[i : i + words]) for i in range(0, len(tokens), words)]
