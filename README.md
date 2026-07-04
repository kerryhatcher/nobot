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
| **Hook** — `PostToolUse` on `Write`/`Edit` | Non-blocking. After a `.md`/`.markdown`/`.txt` file is written or edited, `hooks/scripts/check-ai-tells.sh` scans it for high-confidence vocabulary/phrase tells and em-dash density. If it clears a threshold, it nudges Claude via stderr to run a humanizing pass — the file is never blocked or reverted. |

## Model cost tiering

Agents are the lever for pinning a component to a specific model tier (frontmatter `model: haiku|sonnet|opus|inherit`); skills and prompt-based hooks don't expose that field, so they just run on whatever model the parent conversation is already using. This plugin splits detection into two agents rather than one:

- `ai-tell-reviewer` — `model: sonnet`, for real multi-file/PR-wide audits.
- `ai-tell-quickcheck` — `model: haiku`, for a single short passage, dispatched by `detect-ai-writing` only when doing so actually saves cost (parent conversation on a model above haiku).

The `check-ai-tells.sh` hook is a plain bash/grep script with no model involved at all — the cheapest option available, which is why the automatic per-write scan uses that instead of a prompt-based hook.

## Installation

Test locally without publishing:

```bash
cc --plugin-dir /home/kwhatcher/projects/nobots
```

Or copy/symlink this directory into a project's `.claude-plugin/` for project-scoped testing.

**Note:** hooks load at session start. After editing `hooks/hooks.json` or `hooks/scripts/check-ai-tells.sh`, restart the Claude Code session for changes to take effect.

## Verifying it works

- [ ] Ask Claude to "write a README for X" or "draft a blog post about Y" in a session with this plugin loaded — the output should avoid banned vocabulary, vary sentence length, and skip em dashes.
- [ ] Run `/nobots:detect-ai-writing` against a pasted paragraph, or ask "is this AI-generated?" with text attached — expect a confidence tier plus quoted evidence, not a flat verdict.
- [ ] Ask Claude to review a long doc or PR for AI-sounding writing, or finish writing a long README/spec and watch whether the `ai-tell-reviewer` agent gets suggested proactively.
- [ ] In a session running on Sonnet or Opus, run `/nobots:detect-ai-writing` against a short pasted paragraph and confirm (via the transcript or `claude --debug`) that it dispatches to `ai-tell-quickcheck` rather than scoring inline.
- [ ] Write or edit a `.md` file containing several banned words (e.g. "delve," "moreover," heavy em-dash use) and confirm the hook nudges toward a revision without blocking the write. `claude --debug` shows hook execution in the transcript.

## License

MIT — see `LICENSE`.
