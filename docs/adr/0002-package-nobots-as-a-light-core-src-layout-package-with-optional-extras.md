# 2. Package nobots as a light-core src-layout package with optional extras

Date: 2026-07-09

## Status

Proposed

## Context

`nobots` is evolving from standalone `uv run` scripts into one installable Python package (`src/nobots/`) whose core engine powers a CLI, TUI, MCP server, and Claude Code plugin hook shim. Dependencies vary widely across these interfaces, from minimal prose detection (CLI) to heavy ML stacks (humanize, analyze), requiring careful separation into optional extras to avoid bloat when users only need core functionality.

## Decision

Package `nobots` as a light-core src-layout package with the following dependency strategy:

1. **Core dependencies** (always installed): `typer>=0.12`, `lexicalrichness>=0.5`, `textstat>=0.7` — sufficient for prose detection only (`uv nobots detect` stays fast).
2. **Optional extras** for specialized workloads:
   - `[analyze]`: spaCy stack (`textdescriptives`, `pybiber`, `click`, `en_core_web_sm` wheel) — documents Python 3.12 requirement.
   - `[models]`: PyTorch/Transformers (`torch>=2.2`, `transformers>=4.40`) — documents Python 3.12 requirement (~5GB HF weights).
   - `[tui]`: Textual (`textual>=0.60`).
   - `[mcp]`: MCP server (`mcp>=1.0`).
   - `[humanize]`: Pydantic AI agent (`pydantic-ai>=0.0.14`).
   - `[all]`: all extras combined.
3. **Python version**: `requires-python = ">=3.11"` (enforced). Heavy extras (`[analyze]`, `[models]`) document a Python 3.12 requirement in comments but do not enforce it, because `uv` picks the interpreter per invocation (e.g., `uvx nobots humanize` can auto-select Python 3.12 even if your system default is 3.11).
4. **Build layout**: src-layout (`src/nobots/`), hatchling build backend, with `allow-direct-references = true` to support direct wheel URLs (spaCy model).

## Consequences

**Easier:**
- Fast core install for users who only need detection: `pip install nobots` pulls ~5 dependencies.
- Heavy dependencies optional: users don't pay for unused stacks (torch, spaCy, textual).
- `uv` interop: `uv run nobots detect` remains lightweight; specialized workflows (humanize, analyze) can request 3.12 without blocking adoption on 3.11 systems.
- Standard Python packaging: src-layout + hatchling follows PyPA best practices.

**Harder:**
- First-time setup for `[all]` includes ~200 dependencies and multi-gigabyte downloads (torch + spaCy + models).
- Users must understand extras (e.g., `pip install 'nobots[humanize]'`) to unlock humanize features.
- Python 3.12 expectation for heavy stacks is documented, not enforced — troubleshooting requires clarifying interpreter version.