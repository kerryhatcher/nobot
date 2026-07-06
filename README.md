<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/nobots-banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/nobots-banner.svg">
  <img src="assets/nobots-banner.svg" alt="nobots" width="640">
</picture>

<p><strong>Your writing sounds like a bot. Everyone can tell, and now the detectors can too. <code>nobots</code> strips the machine fingerprints out of prose while Claude drafts it, and calls out AI-sounding text when you point it at some.</strong></p>

<p>
<img alt="version 0.1.0" src="https://img.shields.io/badge/version-0.1.0-D7263D?style=flat-square&labelColor=141414">
<img alt="hook cost: zero tokens" src="https://img.shields.io/badge/hook%20cost-0%20tokens-FF3B5C?style=flat-square&labelColor=141414">
<img alt="research-backed" src="https://img.shields.io/badge/grounded%20in-32%20papers-C42847?style=flat-square&labelColor=141414">
<img alt="license MIT" src="https://img.shields.io/badge/license-MIT-FF8FA3?style=flat-square&labelColor=141414">
<img alt="PRs welcome" src="https://img.shields.io/badge/PRs-welcome-8A1020?style=flat-square&labelColor=141414">
</p>

</div>

---

<!-- site:body:start -->
## Why this exists (or: the em dash gave you away)

Advisory text doesn't change behavior. You can put "please don't write like a robot" in `CLAUDE.md` and the next draft still opens with "In today's rapidly evolving landscape" and three em dashes per paragraph. The tells are statistical and structural, not a matter of good intentions, so the fix has to touch the writing itself.

`nobots` works in both directions. While Claude drafts long-form prose, the `humanize-writing` skill applies the anti-tell rules as the words go down, not as a cleanup pass bolted on at the end. When you want to know whether some text reads as machine-written, `detect-ai-writing` scores it against the same rubric and gives you a confidence tier with reasons, never a bare yes or no. A zero-cost hook watches every file you write and taps Claude on the shoulder when the prose drifts back toward boilerplate.

None of it is guesswork. Everything traces to a research-backed field guide bundled in the repo.

## Install

`nobots` is a local Claude Code plugin. Point Claude Code at a clone of it:

```bash
git clone <your-remote>/nobots.git
claude --plugin-dir /path/to/nobots
```

If you're already inside a local clone, `/plugin marketplace add ./` works too. Hooks load at session start, so after editing `hooks/hooks.json` or the hook script, restart the session. The hook needs `uv` on `PATH`; if it's missing, the script no-ops instead of blocking your edit.

## What it does

| Piece | Role |
|---|---|
| **`humanize-writing`** skill | Fires automatically while Claude drafts prose meant for people (READMEs, docs, posts, guides, articles, emails). Kills the vocabulary fingerprint, engineers sentence-length variation, breaks a rule or two on purpose, writes from a real voice, adds radical specificity, and cuts em dashes. Leaves commit messages and one-line summaries alone. |
| **`detect-ai-writing`** skill | Run it directly (`/nobots:detect-ai-writing path/to/file.md`) or just ask "is this AI-generated?". Scores text against vocabulary, structural, and content tells, weights structure and content over vocabulary, and returns a confidence tier with evidence. Points you at a specific external tool when the read is borderline. Never calls an API itself. |
| **`ai-tell-reviewer`** agent (Sonnet) | The heavyweight. A document-wide or PR-wide audit that reads every file in scope and returns a line-anchored, evidence-backed report. Run it proactively after a big deliverable, the way a code reviewer runs after code. |
| **`ai-tell-quickcheck`** agent (Haiku) | The cheap sibling. A fast single-passage score, dispatched by `detect-ai-writing` only when the parent conversation is on a pricier model than haiku, so the rote pattern-matching doesn't burn expensive tokens. |
| **`check_ai_tells.py`** hook (PostToolUse) | Non-blocking scan after any `.md` / `.markdown` / `.txt` write or edit. Flags exact vocabulary and phrase tells plus real stylometric proxies (sentence-length burstiness, MTLD lexical diversity, Flesch-Kincaid grade, LZMA compression ratio as a perplexity stand-in). If enough signals cross threshold, it nudges Claude to run a humanizing pass. The file is never blocked or reverted. |
| **`deep_stylometry.py`** script | On-demand deep analysis any component can shell out to: dependency-parse complexity, POS proportions, semantic coherence, entropy-per-token, and a curated set of Biber register features (spaCy + textdescriptives + pybiber). Emits labeled numbers, no verdict. `ai-tell-reviewer` always uses it; `quickcheck` never does, to stay cheap. |

## What a scan looks like

Write a doc that opens the way a bot would, and the hook answers without spending a token:

```text
✎ nobots: this file trips 4 AI-writing tells
   · vocabulary   "delve", "leverage", "seamless", "underscores"
   · burstiness    0.21  (human prose usually clears ~0.35)
   · punctuation   6 em dashes in 380 words
   · phrasing      "in today's rapidly evolving landscape"
   → run the humanize-writing pass before you ship this.
```

Write it like a person and the same hook stays quiet. That's the whole contract: nudge the prose that reads as machine-made, touch nothing else.

## Model cost, on purpose

Only agents can pin themselves to a model tier, so detection is split in two: `ai-tell-reviewer` runs on Sonnet for real multi-file audits, `ai-tell-quickcheck` runs on Haiku for short passages and is skipped entirely when the parent is already on Haiku (nothing to save by hopping Haiku to Haiku). The `check_ai_tells.py` hook has no model at all. It's a self-executing `uv` script (PEP 723 inline deps: `lexicalrichness`, `textstat`, plus stdlib `lzma` and `statistics`), so the automatic per-write scan costs zero LLM tokens no matter what the conversation is running.

## The field guide

Two reference docs at the repo root are the source of truth the rest cites:

- **`ai-writing-guide.md`** maps the vocabulary, statistical, and content signatures of AI text, with a practical playbook for avoiding them.
- **`ai-detection-tools.md`** catalogs open-source and offline detectors, free-tier commercial APIs, and benchmark pointers.

Edit the guide and every skill, agent, and the hook inherit the change.

## Host caveat (Claude Code)

> [!IMPORTANT]
> The enforcement hook is a Claude Code `PostToolUse` hook, the only artifact that can react to a file write. Open Plugins hosts without an equivalent post-write hook won't get the automatic scan. On those hosts the `humanize-writing` and `detect-ai-writing` skills still work, since skills are portable. Only the ambient nudge is host-specific.

## Under the hood

<details markdown="1">
<summary><strong>Project layout</strong></summary>

<br>

```
nobots/
├── .claude-plugin/plugin.json      # Claude Code manifest
├── ai-writing-guide.md             # the field guide (source of truth)
├── ai-detection-tools.md           # detector / API catalog
├── skills/
│   ├── humanize-writing/SKILL.md   # write-side rules, applied while drafting
│   └── detect-ai-writing/SKILL.md  # on-demand scoring + confidence tiers
├── agents/
│   ├── ai-tell-reviewer.md         # Sonnet, document/PR-wide audit
│   └── ai-tell-quickcheck.md       # Haiku, single-passage score
├── hooks/
│   ├── hooks.json                  # registers the PostToolUse scan
│   └── scripts/check_ai_tells.py   # zero-cost uv script, the ambient nudge
├── scripts/deep_stylometry.py      # on-demand deep analysis, no verdict
└── README.md
```

The `deep_stylometry.py` script deliberately drops textdescriptives' own `perplexity` fields: they compute `exp()` of an entropy sum rather than a per-token average, so they explode to `1e+86`-scale nonsense on anything past a short paragraph (confirmed by reading the installed library, not assumed). It substitutes a length-normalized `entropy_per_token`, which is still a static-unigram proxy, not the contextual perplexity an LLM detector uses. Treat it as a weak signal, not a verdict.

</details>

## Try the hook by hand

Run the scanner on any prose file without a session:

```bash
echo '{"tool_input":{"file_path":"README.md"}}' | ./hooks/scripts/check_ai_tells.py
```

It reads the file, prints any tells to stderr, and exits without touching the file.
<!-- site:body:end -->

---

Full disclosure: this is a personal project, built for fun. Bug reports, ideas, and roasts of its own prose all welcome.

<div align="center"><sub>Written by a human. Allegedly.</sub></div>
