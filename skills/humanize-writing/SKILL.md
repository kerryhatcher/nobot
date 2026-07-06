---
name: humanize-writing
description: This skill should be used when writing long-form prose intended to read as human-authored, such as README files, documentation, blog posts, guides, articles, emails, or explanatory text. Trigger phrases include "write a README", "write a blog post", "draft documentation", "write a guide", "write an article", "write release notes", "write an explanation of", or any request to produce prose that will be read by people rather than short mechanical text like commit messages or one-line PR summaries. Applies continuously while drafting, not just as a final pass.
version: 0.1.0
---

Produce prose that reads as authentically human by eliminating the vocabulary, statistical, and structural fingerprints of machine writing. Apply these rules while drafting. Don't bolt on a cleanup pass afterward and call it done.

## Why this matters

LLM output carries measurable signatures: predictable word choices, uniform sentence rhythm, low perplexity, content that sounds profound but says little. These aren't style quirks. They're the actual features detection tools and skeptical readers key on. The full research behind every rule below lives in `$CLAUDE_PLUGIN_ROOT/ai-writing-guide.md`. Consult it when a judgment call needs more grounding than the summary here provides, for example when deciding whether a specific statistic or hedge is safe to keep.

## Eliminate the vocabulary fingerprint

Ban these words and phrases outright: delve, tapestry, landscape, multifaceted, nuanced, robust, leverage, utilize, seamless, foster, pivotal, paramount, holistic, innovative, streamline, transformative, vibrant, meticulous, intricate, compelling, embark, navigate, beacon, testament, plethora, myriad. Ban these formal connectors: moreover, furthermore, additionally, nevertheless, consequently, accordingly.

Replace Latinate words with Anglo-Saxon equivalents: "use" not "utilize," "help" not "facilitate," "start" not "commence," "show" not "demonstrate," "improve" not "enhance." Replace formal connectors with "but," "and," "also," "plus," "still," "so." Or drop the connector entirely and let the logic carry itself.

Before writing on an unfamiliar topic, list the 20 words a model would reach for first, then refuse to use any of them.

Avoid the negative-parallelism construction ("It's not just X, it's Y"), the rule-of-three list pattern, significance inflation ("marks a pivotal moment," "underscores the importance of"), and vague attribution ("studies show," "research suggests" without naming the study).

## Engineer burstiness into every paragraph

Never write three consecutive sentences of similar length. Mix aggressively: a three-word sentence, then a sprawling thought that runs to thirty-five words before it lands, then a medium one, then a fragment. Use fragments for emphasis. "Exactly." "Not even close." Allow the occasional run-on that mimics how people actually think when they're excited about something. Read a finished paragraph back. If it sounds monotone, break the rhythm.

Avoid repetitive sentence openers. Don't start three sentences in a row with "The," "This," or the same subject.

## Break grammar rules on purpose

Write "don't," "can't," "it's" instead of the formal expansions, except where the formal version buys real emphasis. Start sentences with "And," "But," "So," "Because." End on a preposition when that's how it would actually be said. Split an infinitive. Drop a subject in a casual aside ("Went to check. Still broken."). Flawless grammar reads as machine-generated; strategic imperfection reads as human.

## Build a specific, consistent voice

Write from a specific persona with a point of view, not a generically helpful assistant summarizing all sides. Take positions: "this approach is mostly wrong, and here's why" beats "there are various perspectives on this matter." Let frustration, enthusiasm, self-doubt, or humor show through where genuine. A voice that never disagrees with anything and never sounds annoyed about anything is a tell on its own.

## Add radical specificity

Replace every generic claim with a concrete one:
- Not "a local business" but a named one.
- Not "improved performance" but the actual before/after numbers.
- Not "studies show" but the author, institution, and year.

Use domain jargon the way an actual practitioner would, without stopping to define terms an insider already knows. Reference real tool names, version numbers, dates, prices. Specificity is the hardest thing for a model to fake convincingly. It's the single most effective differentiator between AI and human prose.

## Destroy formulaic structure

Never open with "In this article, we will explore." Start with a hook: an anecdote, a claim someone could disagree with, a question, or straight into the argument. Vary paragraph length wildly, one sentence, then five, then two. Digress and circle back on purpose ("But I'm getting ahead of myself"). Don't tie off every thread. Skip "In conclusion." Stop when the point is made, or end on a new thought instead of a summary. In a context where flowing prose is expected, don't reach for bullet points and bold text as a substitute for actually connecting ideas in sentences.

## Fix the em dash problem

AI-generated text uses em dashes roughly 10-50x more often than human writing: every 50-80 words versus every 500 or so. Replace most em dashes with a comma, period, semicolon, or a restructured sentence. Don't default to curly quotes where straight quotes are the norm for the context.

## Two-pass check before finishing

After a first draft, read it aloud, mentally or literally. Flag anything that sounds like a press release. Restore any missing personal or concrete detail. Rewrite any sentence that doesn't sound like something an actual person with this specific voice would say. This final pass matters more than any individual rule above. The rules describe what tends to go wrong; the read-aloud test catches what they miss.

## Apply these in leverage order

The edits are not equal. Spend effort top-down: a genuine rewrite beats everything, structural variation beats vocabulary swaps, and single-word substitutions barely register.

1. Rewrite, do not lightly edit. A real pass in your own words breaks the most signals at once.
2. Vary structure and tone across sections (see below).
3. Add radical specificity: real names, numbers, dates.
4. Break sentence rhythm and grammar on purpose.
5. Swap the tell vocabulary last. It is the weakest lever.

## Vary tone across sections

Detectors that survive paraphrase read the whole document, not one line. The body is where machine sameness shows most, because intros and conclusions get edited and bodies do not. Shift register on purpose between the opening, the middle, and the close. Let one section run terse and another loosen up. Uniform tone across every paragraph is itself a tell.

## Generation settings, if you control them

When you can set decoding parameters, nudge them off the defaults: nucleus sampling, a repetition penalty near 1.2, and a decoding strategy other than plain greedy. Greedy, low-temperature output is the most predictable and the easiest to flag. Cheap, high-leverage, worth doing before any hand-editing. Also add `showcase`, `showcasing`, `emphasize`, and `emphasizing` to the banned list; they are the current-generation replacements for the older tells.

## What does not move the needle

Skip the effort here. Swapping one flagged word for a synonym while leaving the sentence structure intact. Asking a model to "write less like AI" without changing anything concrete. Assuming a short passage is safe: short text cannot carry the specificity and structural variation that beat the durable detectors, so it stays easy to flag.

## Pre-send checklist

- No banned vocabulary (delve, leverage, seamless, showcase, emphasize, and the rest).
- No em dashes used as connectors.
- Sentence lengths vary; no run of three similar-length sentences.
- Tone shifts at least once across sections.
- At least one concrete name, number, or date a reader could check.
- No ghost citations ("studies show") without a real source.
- No rule-of-three padding, no "it's not just X, it's Y".
- Read it aloud once. Anywhere you would not say it, rewrite it.


## When in doubt

For deeper grounding on any specific claim above, whether a rule still holds, what the research actually measured, or how confident to be about a given tell, read `$CLAUDE_PLUGIN_ROOT/ai-writing-guide.md`. It documents the vocabulary, statistical (perplexity/burstiness), and content-level signatures in full, with sourcing and caveats about which signals are well-validated versus internet folklore.
