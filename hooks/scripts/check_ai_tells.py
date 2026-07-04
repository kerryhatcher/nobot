#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "lexicalrichness",
#     "textstat",
# ]
# ///
"""Non-blocking PostToolUse hook: scan a written/edited prose file for AI writing tells.

Combines exact vocabulary/phrase matching with real stylometric proxies for the
guide's core signals (burstiness, lexical diversity, readability, compression-ratio
perplexity) instead of guessing at them with word lists alone. Never blocks the
edit; exits 2 (stderr fed back to Claude) only when enough signals cross threshold,
exits 0 (silent) otherwise. Fails open on any unexpected error so a hook bug never
breaks a Write/Edit.
"""

import json
import lzma
import re
import statistics
import sys
from pathlib import Path

PROSE_EXTENSIONS = {".md", ".markdown", ".txt"}
MIN_WORDS_FOR_STATS = 150
MIN_WORDS_FOR_DIVERSITY = 50
LOW_BURSTINESS_THRESHOLD = 0.35  # rough band; guide cites ~0.18-0.33 as the AI/human split

TELL_WORDS = re.compile(
    r"\b(delve|delves|delving|tapestry|multifaceted|nuanced|leverage|leveraging|"
    r"utilize|utilizing|seamless|foster|fosters|pivotal|paramount|holistic|"
    r"streamline|transformative|meticulous|intricate|embark|embarking|beacon|"
    r"testament|plethora|myriad|moreover|furthermore|nevertheless|underscores|"
    r"underscoring)\b",
    re.IGNORECASE,
)
TELL_PHRASES = re.compile(
    r"it'?s not just [a-z ]+, it'?s|it is important to note that|"
    r"in today'?s rapidly evolving|cannot be overstated|embark on a journey|"
    r"a testament to",
    re.IGNORECASE,
)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def read_target_file_path() -> str:
    payload = json.load(sys.stdin)
    return payload.get("tool_input", {}).get("file_path", "") or ""


def sentence_word_lengths(text: str) -> list[int]:
    sentences = [s for s in SENTENCE_SPLIT.split(text) if s.strip()]
    return [len(s.split()) for s in sentences if s.split()]


def burstiness_ratio(lengths: list[int]) -> float | None:
    if len(lengths) < 5:
        return None
    mean = statistics.mean(lengths)
    if mean == 0:
        return None
    return statistics.pstdev(lengths) / mean


def compression_ratio(text: str) -> float | None:
    raw = text.encode("utf-8")
    if not raw:
        return None
    return len(lzma.compress(raw, preset=6)) / len(raw)


def lexical_diversity(text: str, word_count: int) -> float | None:
    if word_count < MIN_WORDS_FOR_DIVERSITY:
        return None
    try:
        from lexicalrichness import LexicalRichness

        return LexicalRichness(text).mtld(threshold=0.72)
    except Exception:
        return None


def readability_grade(text: str) -> float | None:
    try:
        import textstat

        return textstat.flesch_kincaid_grade(text)
    except Exception:
        return None


def analyze(file_path: str) -> int:
    path = Path(file_path)
    if path.suffix.lower() not in PROSE_EXTENSIONS or not path.is_file():
        return 0

    content = path.read_text(encoding="utf-8", errors="ignore")
    word_count = len(content.split())
    if word_count == 0:
        return 0

    word_hits = TELL_WORDS.findall(content)
    phrase_hits = TELL_PHRASES.findall(content)
    total_hits = len(word_hits) + len(phrase_hits)

    em_dash_count = content.count("—")
    em_dash_flag = em_dash_count >= 3 and em_dash_count > word_count / 150

    signals = []
    triggered = False

    if total_hits >= 2:
        triggered = True
        uniq = sorted({w.lower() for w in word_hits})
        signals.append(f"vocabulary/phrase hits: {', '.join(uniq)} ({total_hits} total)")

    if em_dash_flag:
        triggered = True
        signals.append(f"em dash density looks high ({em_dash_count} in ~{word_count} words)")

    diversity = None
    grade = None
    burst = None
    if word_count >= MIN_WORDS_FOR_STATS:
        burst = burstiness_ratio(sentence_word_lengths(content))
        if burst is not None and burst < LOW_BURSTINESS_THRESHOLD:
            triggered = True
            signals.append(
                f"low sentence-length variation (burstiness ratio {burst:.2f}, "
                "human prose typically runs well above 0.3)"
            )
        diversity = lexical_diversity(content, word_count)
        grade = readability_grade(content)

    if not triggered:
        return 0

    message = f"nobots: {file_path} shows possible AI writing tells ({'; '.join(signals)})."

    context = []
    if diversity is not None:
        context.append(f"lexical diversity (MTLD): {diversity:.1f}")
    if grade is not None:
        context.append(f"Flesch-Kincaid grade level: {grade:.1f}")
    ratio = compression_ratio(content)
    if ratio is not None:
        context.append(f"LZMA compression ratio: {ratio:.2f} (lower tends to mean more predictable text)")
    if context:
        message += " Additional context (informational, not independently calibrated): " + "; ".join(context) + "."

    message += (
        " Consider a pass with the humanize-writing skill before finishing, or run "
        "detect-ai-writing for a full read. This is a non-blocking heuristic warning "
        "based on statistical proxies, not a verdict."
    )

    print(message, file=sys.stderr)
    return 2


def main() -> int:
    try:
        file_path = read_target_file_path()
        if not file_path:
            return 0
        return analyze(file_path)
    except Exception:
        # Fail open: a hook bug must never block or spam a Write/Edit.
        return 0


if __name__ == "__main__":
    sys.exit(main())
