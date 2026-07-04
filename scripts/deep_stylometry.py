#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.12.*"
# dependencies = [
#     "textdescriptives",
#     "pybiber",
#     "click",
#     "en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl",
# ]
# ///
"""Deep stylometric analysis for detect-ai-writing / ai-tell-reviewer / ai-tell-quickcheck.

Not a hook. This pulls in spaCy plus a downloaded language model, textdescriptives,
and pybiber, so first invocation is a real install (a couple hundred MB, roughly
1-3 minutes depending on connection) that uv then caches for near-instant reuse.
Never call this from the PostToolUse hook, which needs to be pure and fast on
every single Write/Edit; call it from an agent or skill on explicit request for a
thorough read instead.

Emits a JSON report of raw measurements to stdout for the calling agent/skill to
interpret against $CLAUDE_PLUGIN_ROOT/ai-writing-guide.md. This script does not
compute a verdict or confidence tier itself -- it has no opinion about what counts
as "too AI-sounding," only numbers. The `click` dependency works around a real
upstream bug: spaCy's CLI module imports click directly but newer releases of
typer (which spaCy declares instead) no longer pull click in transitively.

Usage:
    ./deep_stylometry.py path/to/file.md
    cat notes.txt | ./deep_stylometry.py -
"""

import json
import sys

# Curated subset of pybiber's 67 Biber features that map onto specific claims in
# ai-writing-guide.md, rather than dumping all 67 (most of which have no discussed
# AI/human baseline and would just be noise to the calling agent).
BIBER_FEATURES_OF_INTEREST = {
    "f_06_first_person_pronouns": "authentic personal voice (guide: AI defaults to generic, voiceless prose)",
    "f_07_second_person_pronouns": "direct address to the reader",
    "f_14_nominalizations": "nominalization density (guide: robust to paraphrasing, outlasts vocabulary tells)",
    "f_16_other_nouns": "general noun density",
    "f_25_present_participle": "participial constructions (guide: '...highlighting its lasting influence' pattern, 2-5x rate in AI text)",
    "f_27_past_participle_whiz": "reduced relative clauses (whiz-deletion)",
    "f_28_present_participle_whiz": "reduced relative clauses (whiz-deletion)",
    "f_34_sentence_relatives": "sentence-final relative clauses",
    "f_43_type_token": "type-token ratio (raw; MTLD from lexicalrichness is more length-robust)",
    "f_44_mean_word_length": "mean word length (guide: AI favors longer Latinate words over Anglo-Saxon equivalents)",
    "f_45_conjuncts": "formal connector density (moreover/furthermore/additionally, etc.)",
    "f_46_downtoners": "hedging language",
    "f_47_hedges": "hedging language (guide: 'excessive even-handedness' tell)",
    "f_48_amplifiers": "intensifiers (guide: 'importance inflation' tell)",
    "f_59_contractions": "contraction rate (guide: AI avoids contractions, elevating formality)",
}


def load_text(arg: str) -> str:
    if arg == "-":
        return sys.stdin.read()
    with open(arg, encoding="utf-8", errors="ignore") as f:
        return f.read()


def run_textdescriptives(text: str) -> dict:
    import spacy
    import textdescriptives  # noqa: F401  (registers the textdescriptives/* factories)

    nlp = spacy.load("en_core_web_sm")
    # Deliberately skip textdescriptives/quality and textdescriptives/all: the
    # quality component has an upstream confection/pydantic config-validation
    # bug (list vs Tuple[int, int]) as of textdescriptives 2.8.4 / spacy 3.8.14.
    for component in (
        "textdescriptives/descriptive_stats",
        "textdescriptives/readability",
        "textdescriptives/dependency_distance",
        "textdescriptives/pos_proportions",
        "textdescriptives/coherence",
        "textdescriptives/information_theory",
    ):
        nlp.add_pipe(component)

    doc = nlp(text)
    stats = doc._.descriptive_stats
    pos = doc._.pos_proportions

    content_tags = ("NOUN", "VERB", "ADJ", "ADV")
    function_mass = sum(v for k, v in pos.items() if k.replace("pos_prop_", "") not in content_tags)
    content_mass = sum(v for k, v in pos.items() if k.replace("pos_prop_", "") in content_tags)

    n_tokens = stats.get("n_tokens") or 0
    derived = {
        "burstiness_ratio": (
            stats["sentence_length_std"] / stats["sentence_length_mean"]
            if stats.get("sentence_length_mean")
            else None
        ),
        "content_to_function_word_ratio": (content_mass / function_mass if function_mass else None),
        "entropy_per_token": (doc._.entropy / n_tokens if n_tokens and doc._.entropy is not None else None),
    }

    return {
        "descriptive_stats": stats,
        "readability": doc._.readability,
        "dependency_distance": doc._.dependency_distance,
        "pos_proportions": pos,
        "coherence": doc._.coherence,
        # textdescriptives' own "perplexity"/"per_word_perplexity" fields are
        # deliberately omitted: they're exp() of a per-token entropy *sum*
        # (extensive, grows with doc length) rather than a proper per-token
        # average in log-space, so they blow up to nonsense (e.g. 1e+86) on
        # anything longer than a short paragraph. "entropy" itself is kept raw
        # here; "derived.entropy_per_token" is this script's own length-normalized
        # fix, based on static unigram lexeme frequencies (not a language
        # model's contextual probabilities -- a much weaker signal than the
        # perplexity the guide discusses for GPT/Claude-style detection).
        "entropy_raw": doc._.entropy,
        "derived": derived,
    }


def run_biber(text: str, doc_id: str) -> dict:
    import polars as pl
    import pybiber

    corpus = pl.DataFrame({"doc_id": [doc_id], "text": [text]})
    result = pybiber.run_biber(corpus, model="en_core_web_sm").to_dicts()[0]
    subset = {
        name: {"value": result.get(name), "relevance": note}
        for name, note in BIBER_FEATURES_OF_INTEREST.items()
        if name in result
    }
    return subset


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "usage: deep_stylometry.py <file-path|->"}), file=sys.stderr)
        return 1

    arg = sys.argv[1]
    try:
        text = load_text(arg)
    except OSError as e:
        print(json.dumps({"error": f"could not read input: {e}"}), file=sys.stderr)
        return 1

    word_count = len(text.split())
    if word_count < 20:
        print(json.dumps({"error": f"input too short for stylometric analysis ({word_count} words, need 20+)"}))
        return 1

    try:
        report = {
            "source": arg,
            "word_count": word_count,
            "textdescriptives": run_textdescriptives(text),
            "biber_features": run_biber(text, arg),
            "notes": (
                "Raw measurements only, no verdict computed here. Interpret against "
                "$CLAUDE_PLUGIN_ROOT/ai-writing-guide.md. textdescriptives' own "
                "'perplexity'/'per_word_perplexity' fields are dropped from this "
                "report: they exponentiate a per-token entropy *sum* rather than a "
                "proper per-token log-space average, so they explode to nonsense "
                "values on anything longer than a short paragraph. Use "
                "derived.entropy_per_token instead, and even that is based on "
                "static unigram word frequencies, not an LLM's contextual "
                "probabilities -- a much weaker, indirect proxy than the perplexity "
                "the guide discusses for actual model detection. Biber features are "
                "normalized per 1000 tokens except type_token and mean_word_length; "
                "no calibrated human/AI cutoff exists for any single value here, "
                "weigh them as corroborating context only, same as burstiness_ratio "
                "and content_to_function_word_ratio."
            ),
        }
    except Exception as e:
        print(json.dumps({"error": f"analysis failed: {type(e).__name__}: {e}"}), file=sys.stderr)
        return 1

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
