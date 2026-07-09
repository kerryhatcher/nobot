# nobots: CLI + plugin + TUI + optional MCP — Design

**Date:** 2026-07-09
**Status:** Approved (design), pending implementation plan

## Problem

`nobots` is currently a Claude Code plugin: a PostToolUse hook (`check_ai_tells.py`),
a deeper stylometry script (`deep_stylometry.py`), two skills, two agents, and a
research field guide. The detection logic lives inside standalone `uv run` scripts
that only the plugin can invoke.

Refactor into a proper Python **CLI tool** that owns the detection/analysis/humanize
logic, with a **Textual TUI** and an **optional MCP server** as additional surfaces.
The Claude plugin becomes a thin layer that calls the installed CLI via `uvx`, so
there is one engine and no duplicated logic.

## Goals

- One canonical Python package (`nobots`) with importable, tested core functions.
- CLI surface: `detect`, `analyze`, `score`, `humanize`, `tui`, `mcp`.
- Plugin (hooks/skills/agents) invokes the CLI through `uvx` — no bundled code copy.
- Light core install; TUI/MCP/humanize behind optional extras plus an `[all]` extra.
- Humanize uses Pydantic AI with a pluggable model, defaulting to a local LLM (Ollama).

## Non-goals (YAGNI)

- `watch DIR`, a dedicated `config` subcommand, multi-provider humanize fallback chains,
  and splitting into separate PyPI distributions. Revisit only if a real need appears.

## Architecture

Single repo, `src` layout. Core logic is extracted from the existing scripts into
pure, importable functions; every surface (CLI, TUI, MCP, hook shim) calls those
functions rather than re-implementing them.

```
nobots/
  pyproject.toml               # extras: [analyze] [tui] [mcp] [humanize] [all]
  src/nobots/
    __init__.py
    cli.py                     # Typer app: detect / analyze / score / humanize / tui / mcp
    config.py                  # ~/.config/nobots/config.toml loader
    core/
      prose.py                 # clean_prose + prose_windows — shared prep for all detectors
      detect.py                # from check_ai_tells.py — quorum engine, pure functions
      stylometry.py            # from deep_stylometry.py — deep analysis, pure functions
      models.py                # from local-ai-detectors/detect.py — 4 model-based detectors
      guide.py                 # loads packaged field-guide text
    humanize/
      agent.py                 # Pydantic AI agent, pluggable model
    tui/
      app.py                   # Textual app
    mcp/
      server.py                # MCP server exposing detect/analyze/score/humanize
    data/
      ai-writing-guide.md
      ai-detection-tools.md
  plugin/
    .claude-plugin/plugin.json
    hooks/hooks.json
    hooks/scripts/hook_detect.py   # thin stdin shim -> uvx nobots detect
    skills/detect-ai-writing/SKILL.md
    skills/humanize-writing/SKILL.md
    agents/ai-tell-quickcheck.md
    agents/ai-tell-reviewer.md
  tests/
    test_prose.py
    test_detect.py
    test_stylometry.py
    test_models.py
    test_humanize.py
```

CLI framework: **Typer**.

### Components (units, each independently testable)

- **`core/prose.py`** — What: `clean_prose(text)` strips YAML frontmatter, fenced code,
  HTML comments, tables, images/links/inline-code, and markdown markers down to plain
  prose; `prose_windows(text, words=300)` splits into fixed-word windows. How used: every
  detector runs on cleaned prose so markdown noise doesn't skew signals; `score` averages
  per-window for long inputs that exceed model token caps. Pure, stdlib-only. Folded in
  from `local-ai-detectors/detect.py`.
- **`core/detect.py`** — What: takes prose text, returns a structured result
  (per-family votes, quorum decision, stylometric context: MTLD, Flesch-Kincaid,
  LZMA ratio). How used: `detect_text(text) -> DetectResult`. Depends on:
  `lexicalrichness`, `textstat`, stdlib. Pure — no I/O, no `sys.exit`, no stdin.
- **`core/stylometry.py`** — What: deep spaCy/textdescriptives/pybiber report as raw
  numbers, no verdict. How used: `analyze_text(text) -> dict`. Depends on the heavy
  `[analyze]` extra (spaCy + `en_core_web_sm`, pinned to Python 3.12 range).
- **`core/models.py`** — What: 4 fully-local model-based detectors — Binoculars
  (cross-perplexity of a Qwen2.5-0.5B base/instruct pair, lower=AI), Fast-DetectGPT
  (analytic curvature on gpt2, higher=AI), GLTR (top-k rank fractions + mean rank on
  gpt2), RoBERTa (openai-community detector, p(AI)). How used: `score_text(text) -> dict`;
  each detector isolated so one failing returns an `ERR` string, not a crash. Depends on
  the heavy `[models]` extra (`torch`, `transformers`; ~5GB HF weights cached in
  `~/.cache/huggingface`; Python 3.12 range for torch wheels). No verdict — raw numbers
  plus a documented AI-direction per detector; scores are relative, not calibrated cutoffs.
  Folded in from `local-ai-detectors/detect.py`.
- **`core/guide.py`** — What: returns packaged guide markdown. Used by MCP/skills/`--guide`.
- **`humanize/agent.py`** — What: Pydantic AI agent that rewrites prose to remove tells,
  grounded in the guide. How used: `humanize_text(text, model) -> str`. Default model
  = Ollama; raises a clear error if Ollama unreachable. Depends on `[humanize]` extra.
- **`cli.py`** — thin Typer wiring over the above; owns exit codes, `--json`, flags.
- **`tui/app.py`**, **`mcp/server.py`** — thin surfaces over core functions.

## Commands

| Command | Behavior |
|---|---|
| `nobots detect FILE [--json]` | Quorum tell-scan. Exit **0** clean / **2** tells found (preserves the hook contract). Human summary on stderr by default; `--json` emits families + scores to stdout. |
| `nobots analyze FILE [--json]` | Deep stylometry report (raw numbers). Requires `[analyze]` extra. |
| `nobots score FILE [--json] [--chunk] [--words N]` | Model-based detector scores (Binoculars, Fast-DetectGPT, GLTR, RoBERTa). `--chunk` averages over prose windows for long inputs. First run downloads ~5GB models. Requires `[models]` extra. |
| `nobots humanize FILE [--model M] [--in-place]` | Pydantic AI rewrite. Default Ollama; hard-errors if Ollama down. Model/provider via flag or config. Requires `[humanize]` extra. |
| `nobots tui` | Textual UI: pick/paste text, live detect + analyze + score, humanize view. Requires `[tui]`. |
| `nobots mcp` | Start MCP server. Tools: `detect`, `analyze`, `score`, `humanize`. Requires `[mcp]`. |

A subcommand whose extra is missing prints a one-line install hint (e.g.
`humanize needs the humanize extra: uvx --from 'nobots[humanize]' nobots humanize`).

## Packaging

- Core install (`nobots`) = `detect` only: `typer`, `lexicalrichness`, `textstat`.
  Keeps `uvx nobots detect` fast — this is the hot path for the hook.
- Extras: `[analyze]` (spaCy stack), `[models]` (torch + transformers),
  `[tui]` (textual), `[mcp]` (mcp sdk), `[humanize]` (pydantic-ai), and
  `[all]` = union of the above.
- **Python version tension:** both the stylometry stack and the torch/transformers
  models stack pin Python `==3.12.*` (spaCy model wheel; torch wheels), while the
  detect path allows `>=3.11`. The package declares `requires-python = ">=3.11"`; the
  `[analyze]` and `[models]` extras document the 3.12 constraint. `uvx` resolves the
  right interpreter per invocation, so `detect` is unaffected.

## Plugin ↔ CLI

- Plugin lives in `plugin/` in this repo.
- **Hook**: `hooks/hooks.json` points at `hook_detect.py`, a tiny shim that reads the
  tool payload JSON from stdin, extracts `file_path`, runs
  `uvx --from <source> nobots detect FILE`, and propagates the exit code (2 → nudge,
  0 → silent). Fails open on any error, exactly like today.
- **Skills / agents**: instruct the agent to call `uvx nobots detect|analyze|score|humanize`.
- `<source>` = the `nobots` PyPI name (`uvx nobots detect ...`). Name confirmed
  available on PyPI (2026-07-09). During pre-publish dev, hooks/skills may use
  `uvx --from git+<repo-url> nobots` until the first release is cut.

## Config

`~/.config/nobots/config.toml`:

```toml
[humanize]
provider = "ollama"          # pydantic-ai provider id
model = "llama3.1"
base_url = "http://localhost:11434/v1"
```

Precedence: CLI flag > config file > built-in default. Missing config = Ollama defaults.

## Housekeeping

- **Repo rename:** the git remote/repo is currently named `nobot` (singular); rename to
  `nobots` to match the package and PyPI name. Update `project_urls` and any
  `uvx --from git+<repo-url>` dev references after the rename.

## Error handling

- `detect` fails open (exit 0) on any unexpected error — a hook bug must never block a Write/Edit.
- `analyze`/`humanize`/`tui`/`mcp` are explicit user actions: they surface errors with
  clear, actionable messages (missing extra, Ollama unreachable, file not found) and a
  non-zero exit.

## Testing

`pytest` unit tests over the pure core:

- `test_prose.py` — `clean_prose` strips frontmatter/code/tables/markdown and keeps real
  sentences; `prose_windows` splits at the requested word count (ported from the folded-in
  script's self-test asserts).
- `test_detect.py` — a known AI-ish sample crosses the quorum (exit-2 semantics via the
  result object); a known human sample does not; single-family input abstains.
- `test_stylometry.py` — analysis returns expected keys and sane ranges on a fixture.
- `test_models.py` — `score_text` on the canned HUMAN/AI samples: each detector finite and
  in range (GLTR top-k monotonic, roberta prob in [0,1]), and a failing detector yields an
  `ERR` string without killing the rest. Marked slow (downloads models); skipped unless the
  `[models]` extra + a `NOBOTS_MODEL_TESTS=1` env are present.
- `test_humanize.py` — agent wired against a Pydantic AI stub/test model (no network),
  asserts it invokes the model and returns rewritten text.

No frameworks beyond pytest; no fixtures beyond small inline samples.

## Migration

1. `check_ai_tells.py` → `core/detect.py` (split pure logic from stdin/exit shim).
2. `deep_stylometry.py` → `core/stylometry.py`.
3. `local-ai-detectors/detect.py` (external research folder) → split into `core/models.py`
   (the 4 detectors + `score_text`) and `core/prose.py` (`clean_prose`, `prose_windows`);
   its `--selftest` asserts become `test_models.py`/`test_prose.py`. Wire `clean_prose`
   into `detect`/`analyze` so all detectors share prose prep.
4. `ai-writing-guide.md`, `ai-detection-tools.md` → `src/nobots/data/`.
5. Move plugin assets under `plugin/`; add `hook_detect.py` shim; repoint `hooks.json`.
6. Delete the old standalone scripts once the hook shim is proven end-to-end.

## Open decisions resolved

- Commands: detect + analyze + score + humanize (+ tui, mcp).
- Plugin invokes CLI via `uvx`.
- Humanize: Pydantic AI, pluggable, default local Ollama, error if down.
- Packaging: optional extras + `[all]`.
- Fold in `local-ai-detectors`: model-based `score` command behind `[models]` extra;
  adopt `clean_prose`/`prose_windows` as shared prose prep for every detector.
