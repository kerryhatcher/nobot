# 7. Adopt Typer for the CLI; exit codes and --json owned at the CLI layer

Date: 2026-07-09

## Status

Accepted

## Context

`nobots` needs one CLI entry point (`nobots.cli:app`) exposing `detect`,
`analyze`, `score`, and `humanize`, plus `tui`/`mcp` in later phases. The
`detect` command doubles as a Claude Code hook: it must be fast, must fail
open (never block a Write/Edit on a bug), and must map cleanly onto the 0/2
exit-code contract other tooling already depends on. The other commands are
not hot paths and should surface real errors instead of swallowing them.
Several commands depend on optional extras (`[analyze]`, `[models]`,
`[humanize]`) that a given install may not have.

## Decision

Use Typer for the CLI: typed arguments/options, automatic `--help`, and no
hand-rolled `argparse` boilerplate. All framework code lives in `cli.py`;
`core.*` and `humanize.agent` stay import-clean of Typer so the future TUI
and MCP server can call the same functions directly.

- `detect` wraps its whole body in `try/except typer.Exit: raise` then
  `except Exception: raise typer.Exit(code=0)` — any unexpected error fails
  open (exit 0) so a detector bug can never block an editor hook. On success
  it exits 0 (clean) or 2 (`result.tells_found`), matching the existing hook
  contract exactly.
- `analyze`, `score`, `humanize` are not fail-open: file-not-found, missing
  extras, and domain errors (`ValueError`/`RuntimeError`) all surface a
  one-line message on stderr and exit 1.
- A missing optional extra is caught as `ImportError` at the point of import
  and turned into a single-line install hint via `_missing_extra`, e.g.
  `analyze needs the analyze extra: uvx --from 'nobots[analyze]' nobots analyze`,
  exit 1 — no stack trace, no silent partial run.
- `--json` output (machine-readable) always goes to stdout; human-readable
  summaries and all error/nudge text go to stderr, so `--json` output stays
  pipeable even when a summary is also printed.

## Consequences

Easier: the CLI is the only place that knows about exit codes, `--json`, and
extras — core modules stay reusable by the TUI/MCP server without dragging
in Typer or CLI-specific error formatting. Adding a new command extra just
means one more `try/except ImportError: raise _missing_extra(...)` block.

Harder: the fail-open behavior in `detect` is easy to accidentally break if
someone adds code after the outer `try` block, or narrows the bare
`except Exception` — this must stay broad and stay last.
