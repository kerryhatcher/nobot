# nobots

A Claude Code plugin that fights the "AI-sounding" tell, in both directions: it helps Claude write prose that doesn't read as machine-generated, and it helps you tell when something else's prose does.

Everything in this plugin is grounded in two research-backed reference documents at the plugin root:

- **`ai-writing-guide.md`** — a field guide to the vocabulary, statistical, and content-level signatures of AI-generated text, plus a practical playbook for avoiding them.
- **`ai-detection-tools.md`** — a catalog of open-source/offline detection tools, free-tier commercial APIs, and benchmark pointers.

## Components

| Component | What it does |
|---|---|
| **Skill** — `humanize-writing` | Auto-activates whenever Claude drafts long-form prose (READMEs, docs, blog posts, guides, articles, emails). Distills the writing guide into rules Claude applies while drafting: kill the vocabulary fingerprint, engineer sentence-length variation, break a few grammar rules on purpose, write from a specific voice, add radical specificity, avoid formulaic structure, and cut em dashes. Does not apply to commit messages or one-line PR summaries — those have their own conventions. |
| **Skill** — `detect-ai-writing` | Invoke directly (`/nobots:detect-ai-writing [text or file path]`) or ask naturally ("is this AI-generated?"). Scores a piece of text against vocabulary, structural, and content-level tells, weighs them by reliability (structure and content outweigh vocabulary), and reports a confidence tier — never a bare yes/no. For a short single passage, it dispatches the actual scoring to the cheap `ai-tell-quickcheck` agent rather than spending the parent conversation's tokens on rote pattern-matching. Recommends a specific external tool from `ai-detection-tools.md` when the read is borderline; never calls an API itself. |
| **Agent** — `ai-tell-reviewer` (Sonnet) | Heavier-weight, document- or PR-wide audit. Triggers proactively after Claude finishes a long-form deliverable (the same way a code-reviewer agent runs after code changes) or on explicit request. Reads every file in scope and returns a line-anchored, evidence-backed report rather than a single check. |
| **Agent** — `ai-tell-quickcheck` (Haiku) | Cheap, single-passage/single-file sibling to `ai-tell-reviewer`. Dispatched by the `detect-ai-writing` skill when the scope is small (roughly under 500 words) and the parent conversation is running a pricier model than haiku — skipped entirely when the parent is already on haiku, since there's nothing to save by hopping to another haiku call. |
| **Hook** — `PostToolUse` on `Write`/`Edit` | Non-blocking. After a `.md`/`.markdown`/`.txt` file is written or edited, `hooks/scripts/check_ai_tells.py` scans it for exact vocabulary/phrase tells plus real stylometric proxies (sentence-length burstiness, lexical diversity via MTLD, Flesch-Kincaid grade level, LZMA compression ratio as a perplexity proxy). If enough signals cross threshold, it nudges Claude via stderr to run a humanizing pass — the file is never blocked or reverted. |
| **Script** — `scripts/deep_stylometry.py` | Not auto-run by anything. A shared, on-demand deep-analysis utility any component can shell out to via Bash: real dependency-parse complexity, POS proportions, semantic coherence, entropy, and a curated set of Biber register features (spaCy + textdescriptives + pybiber). `ai-tell-reviewer` uses it on every file as part of its thorough audit; `detect-ai-writing` offers it only when the user explicitly asks for a "deep"/"detailed" read; `ai-tell-quickcheck` deliberately never touches it, to stay cheap. |

## Model cost tiering

Agents are the lever for pinning a component to a specific model tier (frontmatter `model: haiku|sonnet|opus|inherit`); skills and prompt-based hooks don't expose that field, so they just run on whatever model the parent conversation is already using. This plugin splits detection into two agents rather than one:

- `ai-tell-reviewer` — `model: sonnet`, for real multi-file/PR-wide audits.
- `ai-tell-quickcheck` — `model: haiku`, for a single short passage, dispatched by `detect-ai-writing` only when doing so actually saves cost (parent conversation on a model above haiku).

The `check_ai_tells.py` hook has no model involved at all — it's a self-executing `uv` script (PEP 723 inline dependencies via `lexicalrichness` and `textstat`, plus stdlib `lzma`/`statistics` for compression-ratio and burstiness math). Zero LLM cost regardless of model tier, which is why the automatic per-write scan uses that instead of a prompt-based hook. `uv` provisions the tiny dependency set on first run and caches it; later runs are near-instant.

## Deep stylometric analysis

`scripts/deep_stylometry.py` is a heavier sibling to the hook's proxies, also a self-executing `uv` script, but pulling in spaCy plus a downloaded `en_core_web_sm` model, `textdescriptives`, and `pybiber`. First run on a machine installs a real dependency set (roughly 150-250MB) and can take 1-3 minutes; `uv` caches it after that, so later runs finish in a few seconds. This is deliberately **not** wired into the hook — it would defeat the point of a hook that has to run on every single `Write`/`Edit`. It's meant to be shelled out to on demand by `ai-tell-reviewer` (always) and `detect-ai-writing` (only when the user asks for a "deep"/"detailed" pass).

It reports real dependency-parse complexity, POS proportions, semantic coherence between sentences, a length-normalized entropy-per-token measure, and a curated subset of Biber's 67 register features (nominalization density, participial constructions, contraction rate, hedges, and more — chosen because each maps onto a specific claim in `ai-writing-guide.md`). It deliberately emits no verdict of its own; it hands the calling agent/skill raw, labeled numbers to weigh against the guide.

One thing worth knowing if you read the code: `textdescriptives`' own `perplexity`/`per_word_perplexity` fields are dropped from the report entirely. They're computed as `exp()` of a per-token entropy *sum* rather than a proper per-token average in log-space, so they explode to physically meaningless values (`1e+86`-scale) on anything longer than a short paragraph — confirmed by reading the installed library's source, not assumed. The script substitutes its own length-normalized `entropy_per_token`, though even that is built on static unigram word frequencies rather than an LLM's contextual probabilities, so treat it as a weak, indirect proxy, not the perplexity the guide discusses for GPT/Claude-style detection.

## Installation

Test locally without publishing:

```bash
cc --plugin-dir /home/kwhatcher/projects/nobots
```

Or copy/symlink this directory into a project's `.claude-plugin/` for project-scoped testing.

**Note:** hooks load at session start. After editing `hooks/hooks.json` or `hooks/scripts/check_ai_tells.py`, restart the Claude Code session for changes to take effect. The hook requires `uv` on `PATH`; if it's missing, the shebang fails and the hook silently no-ops rather than blocking the edit.

## Verifying it works

- [ ] Ask Claude to "write a README for X" or "draft a blog post about Y" in a session with this plugin loaded — the output should avoid banned vocabulary, vary sentence length, and skip em dashes.
- [ ] Run `/nobots:detect-ai-writing` against a pasted paragraph, or ask "is this AI-generated?" with text attached — expect a confidence tier plus quoted evidence, not a flat verdict.
- [ ] Ask Claude to review a long doc or PR for AI-sounding writing, or finish writing a long README/spec and watch whether the `ai-tell-reviewer` agent gets suggested proactively.
- [ ] In a session running on Sonnet or Opus, run `/nobots:detect-ai-writing` against a short pasted paragraph and confirm (via the transcript or `claude --debug`) that it dispatches to `ai-tell-quickcheck` rather than scoring inline.
- [ ] Write or edit a `.md` file containing several banned words (e.g. "delve," "moreover," heavy em-dash use) and confirm the hook nudges toward a revision without blocking the write. `claude --debug` shows hook execution in the transcript.
- [ ] Ask for a "deep"/"detailed" AI-writing check on a file, or ask Claude to review a long document, and confirm `scripts/deep_stylometry.py` gets invoked (expect a real install pause the first time) and its numbers show up cited in the report.

## License

MIT — see `LICENSE`.
