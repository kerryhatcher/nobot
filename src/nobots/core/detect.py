"""Pure quorum tell-detector. Ported from the old check_ai_tells.py hook.

Requires a QUORUM of independent signal families (vocabulary, punctuation,
sentence-length variation) to agree before it declares tells found — a lone
noisy family is not enough. No I/O, no sys.exit, no stdin: the CLI/hook owns
those. Depends on lexicalrichness + textstat (core deps) and stdlib.
"""

import lzma
import re
import statistics
from dataclasses import dataclass, field

MIN_WORDS_FOR_STATS = 150
MIN_WORDS_FOR_DIVERSITY = 50
LOW_BURSTINESS_THRESHOLD = 0.35
VERY_LOW_BURSTINESS = 0.25
QUORUM = 2

TELL_WORDS = re.compile(
    r"\b(delve|delves|delving|tapestry|multifaceted|nuanced|leverage|leveraging|"
    r"utilize|utilizing|seamless|foster|fosters|pivotal|paramount|holistic|"
    r"streamline|transformative|meticulous|intricate|embark|embarking|beacon|"
    r"testament|plethora|myriad|moreover|furthermore|nevertheless|underscores|"
    r"underscoring|showcase|showcases|showcasing|emphasize|emphasizes|"
    r"emphasizing)\b",
    re.IGNORECASE,
)
TELL_PHRASES = re.compile(
    r"it'?s not just [a-z ]+, it'?s|it is important to note that|"
    r"in today'?s rapidly evolving|cannot be overstated|embark on a journey|"
    r"a testament to|plays a (crucial|vital|pivotal) role|it'?s worth noting",
    re.IGNORECASE,
)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


@dataclass
class DetectResult:
    families: dict[str, tuple[int, str]] = field(default_factory=dict)
    agree: int = 0
    quorum: int = QUORUM
    tells_found: bool = False
    context: dict[str, float | None] = field(default_factory=dict)
    summary: str = ""


def _sentence_word_lengths(text: str) -> list[int]:
    sentences = [s for s in SENTENCE_SPLIT.split(text) if s.strip()]
    return [len(s.split()) for s in sentences if s.split()]


def _burstiness_ratio(lengths: list[int]) -> float | None:
    if len(lengths) < 5:
        return None
    mean = statistics.mean(lengths)
    if mean == 0:
        return None
    return statistics.pstdev(lengths) / mean


def _compression_ratio(text: str) -> float | None:
    raw = text.encode("utf-8")
    if not raw:
        return None
    return len(lzma.compress(raw, preset=6)) / len(raw)


def _lexical_diversity(text: str, word_count: int) -> float | None:
    if word_count < MIN_WORDS_FOR_DIVERSITY:
        return None
    try:
        from lexicalrichness import LexicalRichness

        return LexicalRichness(text).mtld(threshold=0.72)
    except Exception:
        return None


def _readability_grade(text: str) -> float | None:
    try:
        import textstat

        return textstat.flesch_kincaid_grade(text)
    except Exception:
        return None


def detect_text(text: str) -> DetectResult:
    """Score prose for AI tells via robust quorum aggregation."""
    result = DetectResult()
    word_count = len(text.split())
    if word_count == 0:
        return result

    word_hits = TELL_WORDS.findall(text)
    phrase_hits = TELL_PHRASES.findall(text)
    total_hits = len(word_hits) + len(phrase_hits)
    em_dash_count = text.count("—")
    families = result.families

    if total_hits >= 4:
        uniq = sorted({w.lower() for w in word_hits if isinstance(w, str)})
        families["vocabulary"] = (2, f"vocabulary/phrase hits: {', '.join(uniq)} ({total_hits} total)")
    elif total_hits >= 2:
        uniq = sorted({w.lower() for w in word_hits if isinstance(w, str)})
        families["vocabulary"] = (1, f"vocabulary/phrase hits: {', '.join(uniq)} ({total_hits} total)")

    if em_dash_count >= 6 and em_dash_count > word_count / 100:
        families["punctuation"] = (2, f"very high em dash density ({em_dash_count} in ~{word_count} words)")
    elif em_dash_count >= 3 and em_dash_count > word_count / 150:
        families["punctuation"] = (1, f"em dash density looks high ({em_dash_count} in ~{word_count} words)")

    diversity = grade = burst = None
    if word_count >= MIN_WORDS_FOR_STATS:
        burst = _burstiness_ratio(_sentence_word_lengths(text))
        if burst is not None:
            if burst < VERY_LOW_BURSTINESS:
                families["burstiness"] = (2, f"very low sentence-length variation (burstiness {burst:.2f})")
            elif burst < LOW_BURSTINESS_THRESHOLD:
                families["burstiness"] = (1, f"low sentence-length variation (burstiness {burst:.2f}, human prose usually clears 0.35)")
        diversity = _lexical_diversity(text, word_count)
        grade = _readability_grade(text)

    result.agree = len(families)
    result.tells_found = result.agree >= QUORUM
    result.context = {
        "mtld": diversity,
        "flesch_kincaid": grade,
        "lzma_ratio": _compression_ratio(text),
    }

    if result.tells_found:
        signals = [msg for _, msg in families.values()]
        result.summary = (
            f"possible AI writing tells ({result.agree} independent signals agree: "
            f"{'; '.join(signals)})."
        )
    return result
