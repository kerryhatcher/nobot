"""Deep spaCy/textdescriptives/pybiber stylometry. Ported from deep_stylometry.py.

Raw measurements only — no verdict. Requires the [analyze] extra (spaCy +
en_core_web_sm, pinned to the Python 3.12 range). Pure: no argv/stdin/exit.
"""

import json  # noqa: F401  (kept for parity; callers may json.dumps the dict)

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


def analyze_text(text: str, doc_id: str = "input") -> dict:
    word_count = len(text.split())
    if word_count < 20:
        raise ValueError(f"input too short for stylometric analysis ({word_count} words, need 20+)")
    return {
        "word_count": word_count,
        "textdescriptives": run_textdescriptives(text),
        "biber_features": run_biber(text, doc_id),
        "notes": (
            "Raw measurements only, no verdict computed here. Biber features are "
            "normalized per 1000 tokens except type_token and mean_word_length; "
            "no calibrated human/AI cutoff exists for any single value — weigh them "
            "as corroborating context only. textdescriptives' own perplexity fields "
            "are omitted (they exponentiate an entropy sum and explode on long text); "
            "use derived.entropy_per_token, itself only a static-unigram proxy."
        ),
    }
