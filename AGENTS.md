# Agent instructions

## Context

For an overview of this app's architecture, read `docs/research/nobots-architecture-map.md`. If a `graphify-out/` folder exists, consult it too for a queryable knowledge graph of the codebase.

## Architecture Decision Records (ADRs)

Use the `adrs` CLI (a Rust tool) to create, manage, search, and edit ADRs in this repo. Do not hand-write ADR files.

- Initialize once (creates `docs/adr/`): `adrs init`
- Create: `adrs new "Title of the decision"`
- Supersede an old one: `adrs new -s <N> "New decision"`
- Edit: `adrs edit <N>`
- List: `adrs list`
- Search: `adrs search "<query>"`
- Change status: `adrs status <N>`
- Link two ADRs: `adrs link <src> <target>`
- Quick reference: `adrs cheatsheet`

**Record every architecturally significant decision as an ADR.** Do this before or alongside the code change, using `adrs new`. Significant = anything a future maintainer would want the reasoning for: dependency choice, detector design, hook contract, data/format change, or reversing a prior decision (use `adrs new -s <N>` to supersede).

## Build & test

This is a `uv`-managed Python package (src layout, `src/nobots/`). Never call bare `python`/`pip` — always `uv run` / `uv sync` / `uvx`.

- Install deps: `uv sync`
- Run the test suite: `uv run pytest`
- Exercise the CLI directly: `uvx nobots detect FILE` (or `uv run nobots detect FILE` from a checkout)

Model-backed tests (`tests/test_models.py`, the Binoculars/Fast-DetectGPT/GLTR/RoBERTa detectors) are skipped by default because they download ~5GB of weights on first run. Run them explicitly:

```bash
NOBOTS_MODEL_TESTS=1 uv run --extra models pytest tests/test_models.py
```

`[analyze]` and `[models]` are the two heavy extras (spaCy stack; torch/transformers) and document, without enforcing, a Python 3.12 pin — the core package itself supports `>=3.11`.

**Architecture:** every surface — the Typer CLI (`src/nobots/cli.py`), the Textual TUI (`src/nobots/tui/`), the MCP server (`src/nobots/mcp/`), and the Claude Code plugin's hook/skills/agents under `plugin/` (which call the CLI via `uvx`, carrying no detection logic of their own) — routes through the same `src/nobots/core/` engine (`detect.py`, `stylometry.py`, `models.py`, `prose.py`, `guide.py`). Add new detection logic there, once, not per-surface.
