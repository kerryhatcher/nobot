# nobots fold-in plan: recent AI-writing-detection research

Status: proposed (not yet executed). Drafted 2026-07-06.

Source of the updates: a compilation of recent academic AI-writing-detection research (32 peer-reviewed
paper extracts, a synthesis report, and a human-prose skill draft). This plan folds the notable new
findings into nobots' existing reference docs, skills, hook, and stylometry script.

## Where nobots already stands

nobots' vocabulary, punctuation, and burstiness layers are strong and roughly current. Its
detector-landscape coverage (accuracy tables, the Sadasivan TV-distance ceiling, non-native
false-positive harm, legal and institutional detail through 2026) is rich. It also ships working code
(the zero-cost hook, the deep stylometry script), a Haiku/Sonnet cost-tiering design, and a verified
engineering caveat (the textdescriptives `perplexity` field is broken, exploding to roughly 1e+86;
nobots substitutes a length-normalized `entropy_per_token`). None of that gets regressed.

The fold-in targets are the durable structural detectors the guide gestures at but never
operationalizes, the token-probability sequence family, and the leverage-ordered evasion tiers.

## Guiding rules

- Additive only. Keep everything nobots already does better.
- Orchestration caveat: an edit agent handed both a structured (schema) return and a file-write in one
  task will often satisfy the schema and silently skip the write. Have the agent return the full
  content as a field and write the file from the orchestrator. Sweep em dashes out of any
  agent-generated prose before commit (nobots' own no-em-dash rule).
- Work on a branch. nobots has no git remote and is the only copy, so a branch is the safety net.
- Do not commit until reviewed.

## Phase 1: reference guide (`ai-writing-guide.md`)

The source of truth the skills and hook cite. Add three subsections:

1. Cross-model / origin attribution (Sniffer, arXiv 2304.14072). Perplexity fingerprints are
   model-specific and survive paraphrase and quality gains; fooling one model does nothing; a 22-dim
   cross-model fingerprint names the source model; instruction-tuned models (Alpaca, Dolly) trace to
   their ChatGPT training origin, not their base model. This corrects the guide's single-model LZMA
   "perplexity proxy" framing.
2. Token-probability sequence family. Fast-DetectGPT, Binoculars (over 90% at 0.01% FPR), DALD,
   Lastde / Lastde++ (sequence dynamics: human token-probability jumps abruptly, AI stays smooth),
   TOCSIN (token cohesiveness), RAIDAR (rewriting-based, resists non-native bias). The guide today
   has only probability level and variance, not the sequence signal.
3. Durable structural detectors. Beyond Checkmate (cross-segment tone; the body is the "creative
   chokepoint"), StoryScope (narrative discourse structure, 93.2% macro-F1, survives style-editing;
   theme-stated 77% vs 52%, named-works 24% vs 47%). This operationalizes the guide's existing claim
   that structure outlasts vocabulary.

## Phase 2: humanize skill (`skills/humanize-writing/SKILL.md`)

The write-side. Changes:

- Reorder rules by leverage (edit pass, then structural variation, then specificity, then rhythm,
  then vocabulary polish).
- Add cross-segment tone variation (Beyond Checkmate): deliberately shift register across intro,
  body, and conclusion.
- Add generation-setting levers: nucleus sampling, repetition penalty near 1.2, decoding choice
  (RAID-benchmark tier-1 cheap wins).
- Add a "what does NOT work" list: single-word swaps, prompting for variety, assuming short text is
  safe.
- Rotate banned vocabulary: add `showcasing`, `emphasizing`, `underscoring`-as-verb (GPT-4o and GPT-5
  vintage); note the list decays and the Latinate bias is the stable signal.
- Add a discrete pre-send checklist (checkbox form).

## Phase 3: detect skill (`skills/detect-ai-writing/SKILL.md`)

- Add narrative and cross-segment structural checks to the scoring rubric, not just vocabulary and
  burstiness.
- Add sequence-dynamics awareness (why smooth token probability is itself a tell).

## Phase 4: the hook (`hooks/scripts/check_ai_tells.py`), code, highest value

- Replace the naive `total_hits >= 2` tally with RoPoLL-style robust aggregation: require at least 3
  independent signal families to agree (vocabulary, burstiness, structure) via a median or quorum
  rather than a raw sum. The current tally is exactly the naive aggregation RoPoLL warns against.
- Add the rotated tell-words and tell-phrases to the regex sets.
- Keep the fail-open, exit-2-nudge behavior.

## Phase 5: deep stylometry (`scripts/deep_stylometry.py`), optional, heavier

- Add a cross-segment variance metric (Beyond Checkmate): compute burstiness and register per third,
  flag low inter-segment variance.
- Add a lightweight narrative-structure proxy (StoryScope-lite): theme-statement and named-entity
  ratios.

## Not changing

- The detector-landscape accuracy tables, TV-distance ceiling, non-native false-positive coverage,
  and legal / institutional detail. Already strong and current.
- The Haiku/Sonnet cost-tiering and the textdescriptives perplexity-bug workaround. nobots is ahead.

## Effort, risk, order

- Phases 1 through 3 are prose edits: low risk, additive.
- Phase 4 is a real code change: test against sample texts before commit.
- Phase 5 is optional and the most work.
- Recommended order: 4, then 1, 2, 3, then 5. The hook is highest-leverage and most-wrong today.

## Source references

- Sniffer: arXiv 2304.14072.
- Fast-DetectGPT, Binoculars, DALD, Lastde / Lastde++, TOCSIN, RAIDAR, Beyond Checkmate, StoryScope,
  RoPoLL: cited by name; each is a published paper locatable on arXiv or its venue.
- House style: nobots' own `ai-writing-guide.md` (no em dashes, burstiness, contractions, banned
  vocabulary, radical specificity).
