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

`nobots` is a Python package with a Typer CLI. Run it straight from PyPI with `uv` — no clone, no install step:

```bash
uvx nobots detect some-draft.md
```

That's the light core: `typer`, `lexicalrichness`, `textstat`. Exit code `0` means clean, `2` means it found tells (details on stderr, or `--json` for structured output). Heavier surfaces live behind extras — pull one in with `uvx --from`:

```bash
uvx --from 'nobots[analyze]' nobots analyze some-draft.md
uvx --from 'nobots[models]'  nobots score some-draft.md
uvx --from 'nobots[tui]'     nobots tui
```

| Extra | Unlocks | Notes |
|---|---|---|
| `analyze` | `nobots analyze` — deep stylometry (spaCy, textdescriptives, pybiber) | first run installs a language model; documents (doesn't enforce) a Python 3.12 pin |
| `models` | `nobots score` — Binoculars / Fast-DetectGPT / GLTR / RoBERTa detectors | first run downloads ~5GB of weights; documents a Python 3.12 pin |
| `humanize` | `nobots humanize` — pydantic-ai rewrite | defaults to a local Ollama server; hard-errors if it's not running |
| `tui` | `nobots tui` — Textual live-scan UI | |
| `mcp` | `nobots mcp` — MCP server exposing detect/analyze/score/humanize as tools | |
| `all` | every extra above | |

`requires-python >=3.11` for the core package.

**Working on the CLI itself?** Clone and run from source with `uv`:

```bash
git clone https://github.com/kerryhatcher/nobot.git
cd nobot
uv sync
uv run nobots detect some-draft.md
```

**Using the Claude Code plugin?** It ships separately under `plugin/` through the [hatch-plugins marketplace](https://github.com/kerryhatcher/hatch-plugins):

```
/plugin marketplace add kerryhatcher/hatch-plugins
/plugin install nobots@hatch-plugins
```

Restart the session afterward so the hook loads. The plugin's hook and skills don't carry any detection logic of their own — they shell out to `uvx nobots detect` (see `plugin/hooks/scripts/hook_detect.py`). The hook needs `uv` on `PATH`; without it the background scan quietly no-ops instead of blocking your edit.

## Commands

| Command | What it does |
|---|---|
| `nobots detect FILE [--json]` | Quorum tell-scan (vocabulary + punctuation + stylometric proxies). This is the engine behind the hook. Exit `0` clean / `2` tells found. Fails open on any internal error — never blocks a write. |
| `nobots analyze FILE [--json]` | Deep stylometry report: raw numbers, no verdict. Extra: `analyze`. |
| `nobots score FILE [--json] [--chunk] [--words N]` | Runs four local model-based detectors (Binoculars, Fast-DetectGPT, GLTR, RoBERTa). `--chunk` averages over `--words`-sized windows for long input. Extra: `models`. |
| `nobots humanize FILE [--model M] [--in-place]` | Rewrites the file through a pydantic-ai agent, local Ollama by default. `--in-place` overwrites; otherwise prints to stdout. Extra: `humanize`. |
| `nobots tui` | Launches the Textual live-scan UI. Extra: `tui`. |
| `nobots mcp` | Launches an MCP server exposing detect/analyze/score/humanize as tools. Extra: `mcp`. |
| `nobots --guide` | Prints the packaged field guide and exits. (Typer quirk: a subcommand token is still required syntactically, so invoke it as e.g. `nobots --guide detect .` — the callback exits before that subcommand ever runs.) |

Missing an extra? Every gated command prints the exact `uvx --from 'nobots[extra]' nobots CMD` install line to stderr and exits non-zero instead of stack-tracing.

### Configuring `humanize`

`nobots humanize` reads `~/.config/nobots/config.toml`:

```toml
[humanize]
provider = "ollama"
model = "llama3.1"
base_url = "http://localhost:11434/v1"
```

CLI flags (`--model`) override the config file, which overrides these built-in defaults.

## Use it

Nothing to configure for the plugin path. Once it's installed:

- **Writing.** Ask Claude for anything long-form (a README, docs, a post) and `humanize-writing` shapes the prose as it drafts. No command needed.
- **Checking.** Ask "is this AI-written?" or run `/nobots:detect-ai-writing path/to/file.md`. You get a confidence tier with reasons, never a bare yes or no.
- **Auditing.** After a big document, ask for an `ai-tell-reviewer` pass for a line-anchored, file-wide report.
- **Ambient.** Every `.md` / `.txt` you write is scanned in the background via `uvx nobots detect`. If the prose drifts toward boilerplate, Claude gets a nudge to run a humanizing pass. It never blocks you.


## What it does

| Piece | Role |
|---|---|
| **`humanize-writing`** skill | Fires automatically while Claude drafts prose meant for people (READMEs, docs, posts, guides, articles, emails). Kills the vocabulary fingerprint, engineers sentence-length variation, breaks a rule or two on purpose, writes from a real voice, adds radical specificity, and cuts em dashes. Leaves commit messages and one-line summaries alone. |
| **`detect-ai-writing`** skill | Run it directly (`/nobots:detect-ai-writing path/to/file.md`) or just ask "is this AI-generated?". Scores text against vocabulary, structural, and content tells, weights structure and content over vocabulary, and returns a confidence tier with evidence. Points you at a specific external tool when the read is borderline. Never calls an API itself. |
| **`ai-tell-reviewer`** agent (Sonnet) | The heavyweight. A document-wide or PR-wide audit that reads every file in scope and returns a line-anchored, evidence-backed report. Run it proactively after a big deliverable, the way a code reviewer runs after code. |
| **`ai-tell-quickcheck`** agent (Haiku) | The cheap sibling. A fast single-passage score, dispatched by `detect-ai-writing` only when the parent conversation is on a pricier model than haiku, so the rote pattern-matching doesn't burn expensive tokens. |
| **`nobots detect`** CLI command | Non-blocking quorum scan the plugin's PostToolUse hook calls via `uvx` after any `.md` / `.markdown` / `.txt` write or edit. Flags exact vocabulary and phrase tells plus stylometric proxies (sentence-length burstiness, MTLD lexical diversity, Flesch-Kincaid grade, LZMA compression ratio as a perplexity stand-in). If enough signals cross threshold, it nudges Claude to run a humanizing pass. The file is never blocked or reverted. |
| **`nobots analyze`** CLI command | On-demand deep analysis (extra: `analyze`): dependency-parse complexity, POS proportions, semantic coherence, entropy-per-token, and a curated set of Biber register features (spaCy + textdescriptives + pybiber). Emits labeled numbers, no verdict. `ai-tell-reviewer` always uses it; `quickcheck` never does, to stay cheap. |

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

Only agents can pin themselves to a model tier, so detection is split in two: `ai-tell-reviewer` runs on Sonnet for real multi-file audits, `ai-tell-quickcheck` runs on Haiku for short passages and is skipped entirely when the parent is already on Haiku (nothing to save by hopping Haiku to Haiku). The PostToolUse hook has no model at all — it's a thin shim (`plugin/hooks/scripts/hook_detect.py`) that shells out to `uvx nobots detect`, whose core dependencies are just `lexicalrichness` and `textstat` plus stdlib `lzma` and `statistics`. The automatic per-write scan costs zero LLM tokens no matter what the conversation is running.

## The field guide

Two reference docs, packaged with the CLI under `src/nobots/data/`, are the source of truth the rest cites. Print them any time with `nobots --guide` (see the quirk noted in the command table above):

- **`ai-writing-guide.md`** maps the vocabulary, statistical, and content signatures of AI text, with a practical playbook for avoiding them.
- **`ai-detection-tools.md`** catalogs open-source and offline detectors, free-tier commercial APIs, and benchmark pointers.

Edit the guide and every skill, agent, the hook, and `nobots --guide` inherit the change.

## Host caveat (Claude Code)

> [!IMPORTANT]
> The enforcement hook is a Claude Code `PostToolUse` hook, the only artifact that can react to a file write. Open Plugins hosts without an equivalent post-write hook won't get the automatic scan. On those hosts the `humanize-writing` and `detect-ai-writing` skills still work, since skills are portable. Only the ambient nudge is host-specific.

## Under the hood

<details markdown="1">
<summary><strong>Project layout</strong></summary>

<br>

```
nobot/
├── src/nobots/                     # the package — every surface below calls into this
│   ├── cli.py                      # Typer app: detect/analyze/score/humanize/tui/mcp/--guide
│   ├── core/
│   │   ├── detect.py               # quorum tell-scan (the hook's engine)
│   │   ├── stylometry.py           # deep analysis: spaCy/textdescriptives/pybiber
│   │   ├── models.py               # Binoculars/Fast-DetectGPT/GLTR/RoBERTa detectors
│   │   ├── prose.py                # shared text cleanup / windowing
│   │   └── guide.py                # loads the packaged field guide
│   ├── data/                       # ai-writing-guide.md, ai-detection-tools.md (packaged)
│   ├── humanize/                   # pydantic-ai rewrite agent
│   ├── tui/                        # Textual live-scan app
│   └── mcp/                        # MCP server exposing the same four verbs
├── plugin/                         # the Claude Code plugin — calls the CLI via uvx
│   ├── .claude-plugin/plugin.json
│   ├── skills/
│   │   ├── humanize-writing/SKILL.md
│   │   └── detect-ai-writing/SKILL.md
│   ├── agents/
│   │   ├── ai-tell-reviewer.md     # Sonnet, document/PR-wide audit
│   │   └── ai-tell-quickcheck.md   # Haiku, single-passage score
│   └── hooks/
│       ├── hooks.json              # registers the PostToolUse scan
│       └── scripts/hook_detect.py  # thin shim: stdin -> `uvx nobots detect` -> exit code
├── tests/
└── pyproject.toml
```

`core/stylometry.py` deliberately drops textdescriptives' own `perplexity` fields: they compute `exp()` of an entropy sum rather than a per-token average, so they explode to `1e+86`-scale nonsense on anything past a short paragraph (confirmed by reading the installed library, not assumed). It substitutes a length-normalized `entropy_per_token`, which is still a static-unigram proxy, not the contextual perplexity an LLM detector uses. Treat it as a weak signal, not a verdict.

</details>

## Try the hook by hand

Run the same scan the hook runs, without a Claude Code session:

```bash
uvx nobots detect README.md
```

It reads the file, prints any tells to stderr, exits `2` if it found tells or `0` if clean, and never touches the file. To exercise the plugin's shim exactly as the hook invokes it:

```bash
echo '{"tool_input":{"file_path":"README.md"}}' | plugin/hooks/scripts/hook_detect.py
```
<!-- site:body:end -->

---

Full disclosure: this is a personal project, built for fun. Bug reports, ideas, and roasts of its own prose all welcome.

<div align="center"><sub>Written by a human. Allegedly.</sub></div>
