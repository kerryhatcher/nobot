---
name: detect-ai-writing
description: This skill should be used when the user asks to "detect AI writing", "check if this is AI-generated", "is this text written by AI", "audit this text for AI tells", "run detect-ai-writing", or provides a piece of text or file and asks whether it reads as machine-written. Invocable directly as a user command (e.g. "/nobots:detect-ai-writing path/to/file.md" or pasted text) as well as triggering automatically on these phrases.
argument-hint: [text or file-path]
allowed-tools: Read, Task, Bash
version: 0.3.0
---

Analyze a piece of text against the vocabulary, statistical, and content-level fingerprints of AI-generated writing, then report a confidence tier with concrete evidence — never a bare "yes/no" verdict.

## Step 1: Get the target text and pick a cost path

If the argument looks like a file path, read it with the Read tool. If it looks like inline pasted text, use it directly. If no argument was given, ask the user what to analyze rather than guessing.

For a fast automated pre-check on a file (the same quorum tell-scan the plugin's PostToolUse hook runs), `uvx nobots detect FILE` exits 2 if tells were found and 0 if clean, printing a nudge with the specific signals to stderr. Treat it as a cheap first pass, not a replacement for the fuller read below.

Then route by scope and by what this conversation is already paying for:

- **Single passage or file, roughly under 500 words, and this conversation is running on a model above haiku**: dispatch the scoring work to the `ai-tell-quickcheck` agent (haiku) instead of doing it inline. It's a rote pattern-matching pass; there's no reason to spend this conversation's tokens on it. Take its returned report straight into Step 5.
- **This conversation is already running on haiku**: skip dispatch (a haiku-to-haiku hop saves nothing and adds latency) and run Steps 2-4 inline instead.
- **Long document, multi-file, or PR-wide scope**: this skill is built for single-item checks. Tell the user to invoke the `ai-tell-reviewer` agent (sonnet) for a thorough, line-anchored audit instead of forcing a shallow read here.

For a long single document that still fits the "one item" case, sample multiple paragraphs from different sections rather than only the opening, since AI tells often concentrate unevenly.

## Step 2: Score against the tell categories (inline path only)

Skip this step and Step 3 if Step 1 dispatched to `ai-tell-quickcheck` — use its returned report instead. Otherwise, work through each category and record concrete hits (quote the exact phrase or sentence, don't just assert a category triggered).

**Vocabulary tells** — count occurrences of: delve, tapestry, landscape, multifaceted, nuanced, robust, leverage, utilize, seamless, foster, pivotal, paramount, holistic, innovative, streamline, transformative, vibrant, meticulous, intricate, compelling, embark, navigate, beacon, testament, plethora, myriad, moreover, furthermore, additionally, nevertheless, consequently, accordingly. Also flag the negative-parallelism construction ("it's not just X, it's Y"), significance inflation ("marks a pivotal moment," "underscores the importance of"), and vague attribution ("studies show" with no named source).

**Structural/statistical proxies** — without running an actual perplexity/burstiness model, approximate these by eye: measure sentence-length variation across a paragraph (low variation = suspicious), count consecutive sentences opening with "The"/"This"/the same subject, count em dashes per 100 words (AI text runs roughly 10-50x denser than human baseline — a raw ratio above roughly 1 per 100 words is worth flagging), and note near-total absence of contractions, fragments, or grammatical imperfection.

**Content tells** — look for superficiality dressed as depth (a claim followed by "...highlighting its lasting influence" with no supporting specifics), absence of a distinct personal voice or opinion, excessive even-handedness ("there are many perspectives"), generic examples instead of named specifics, ghost citations, and a formulaic claim → elaboration → example → transition rhythm repeating across paragraphs.

## Step 2b: Structural and narrative checks (weight these highest)

Vocabulary and burstiness are easy to fake, so weight structure higher than either. Look for:

- Uniform tone across sections. Compare the body against the intro and conclusion. Machine text stays flat where a human loosens up, and the body is the "creative chokepoint" that gives it away even when the ends are polished.
- Narrative and discourse sameness: an explicitly stated theme where a human would imply one, few named specific works or sources, formulaic paragraph shape repeated down the page.
- Smooth token-probability rhythm. You cannot see this by eye, but if an external detector reports it (Fast-DetectGPT, Binoculars, DALD, Lastde, TOCSIN), treat a "too smooth" reading as a real signal, not noise.

Remember the ceiling: paraphrase and a genuine human edit collapse most detectors, so a clean score is not proof of human authorship. Say so in the verdict.


## Step 3: Weigh the evidence, don't just tally it (inline path only)

Per the underlying research (run `uvx nobots --guide` to print the packaged field guide), vocabulary tells are the weakest and most time-bound signal — treat them as corroborating, not decisive. Structural signals (low sentence-length variation, high dependent-clause density, near-zero rhetorical questions, em-dash frequency) and content-level signals (superficiality, absence of voice, ghost citations) are more robust and should carry more weight. A text with zero banned words can still be heavily AI-patterned structurally, and a human writer can legitimately use words like "utilize" or "delve" a handful of times — isolated hits are not evidence on their own.

## Step 4: Report a confidence tier, not a verdict

Produce (or relay, if `ai-tell-quickcheck` already produced one) a structured report:

- **Tier**: one of `Likely human`, `Mixed / inconclusive signals`, `Likely AI-generated`.
- **Evidence for**: quoted excerpts mapped to the specific tell each one hits.
- **Evidence against** (if any): passages showing burstiness, specific detail, or authentic voice that cut the other way.
- **Confidence caveats**: state plainly that this is a heuristic linguistic read, not a certified detector. Edited or paraphrased AI text routinely evades detection entirely (adversarial studies show accuracy collapsing from ~40% to as low as ~17% against lightly humanized text). Conversely, false positives disproportionately hit non-native English speakers and formal technical writing — never assert authorship as settled fact, especially for anything with real stakes (academic integrity, employment, publication). For text under roughly 150 words, note explicitly that structural and statistical signals (sentence-length variation, em-dash density) are unreliable at that length — lean the verdict on vocabulary and content-level tells instead.

## Step 5: Recommend a tool when the read is borderline

If the text is long-form, high-stakes, or the manual read lands in "mixed signals," recommend a specific external check rather than pushing the manual analysis further. Consult `uvx nobots --guide` (packaged field guide, includes the tools appendix) for current free-tier APIs (GPTZero, Winston AI, Copyleaks, Sapling, ZeroGPT, Pangram, Hugging Face-hosted classifiers) and open-source/offline options, and name the one or two best suited to the text's length and stakes. This skill does not call those APIs itself — it points to them.

## Step 6: Deep stylometric analysis (only when explicitly requested)

If the user explicitly asks for a "detailed," "deep," or "thorough" analysis (rather than the default quick read), run `uvx --from 'nobots[analyze]' nobots analyze <file-path-or-->` via Bash. It uses spaCy, textdescriptives, and pybiber to compute real burstiness, lexical diversity (MTLD-style), dependency-clause complexity, POS proportions, readability grade level, entropy-per-token, and a curated set of Biber register features — actual measurements, not the eyeballed proxies from Steps 2-3. Fold its output into the report as corroborating evidence, using its own field-level `relevance` annotations to explain what each number means; its `notes` field spells out what it deliberately doesn't claim (no calibrated cutoffs, no LLM-equivalent perplexity).

Warn the user before running it the first time on a machine: it installs a real dependency set (spaCy, a language model, textdescriptives, pybiber) and can take 1-3 minutes on that first call, then is fast on every call after (`uv` caches it). Never invoke this automatically for the default case — it's opt-in rigor, not the standard path, and it does not apply to `ai-tell-quickcheck`, which deliberately stays cheap.
