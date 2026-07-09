# 8. Plugin invokes the installed CLI via uvx instead of bundling detection code

Date: 2026-07-09

## Status

Accepted

## Context

The Claude Code plugin (now under `plugin/`) originally carried its own copy of the
AI-tell detection logic in `hooks/scripts/check_ai_tells.py`, invoked directly by the
PostToolUse hook. The `nobots` package (`src/nobots`) now owns that same quorum
detection engine (`nobots.core.detect`) plus analyze/score/humanize/tui/mcp, exposed
through the `nobots` CLI. Keeping a second, duplicated implementation inside the
plugin risks drift: a fix or tuning change to the detector would need to land in two
places, and the two copies would silently diverge over time.

## Decision

One engine, no duplicated logic. The plugin's hook shim
(`plugin/hooks/scripts/hook_detect.py`) carries zero detection code. On each
PostToolUse Write/Edit event it:

1. Reads the hook payload JSON from stdin and extracts `tool_input.file_path`.
2. Shells out to `uvx --from <source> nobots detect <file>` via `subprocess.run`.
3. Propagates `nobots detect`'s exit code unchanged: `0` = no tells, `2` = quorum of
   tell families agreed, and the CLI's own stderr nudge is forwarded.
4. Fails open (`return 0`) on any exception — a hook bug, missing `uvx`, network
   failure, or timeout must never block the underlying Write/Edit.

`<source>` is read from the `NOBOTS_SOURCE` environment variable, defaulting to the
plain PyPI package name `"nobots"`. Pre-publish (before `nobots` exists on PyPI),
`NOBOTS_SOURCE` can be pointed at a local checkout (`.`) or a `git+https://...` URL
so the shim still works without a real release. `plugin/skills/*` and
`plugin/agents/*` were updated the same way: every reference to the old bundled
`scripts/deep_stylometry.py` and the bundled guide files
(`ai-writing-guide.md`, `ai-detection-tools.md`) now calls the installed CLI instead
(`uvx nobots detect FILE`, `uvx --from 'nobots[analyze]' nobots analyze FILE`,
`uvx --from 'nobots[humanize]' nobots humanize FILE`, `uvx nobots --guide` for the
field guide, which now ships packaged inside `src/nobots/data`).

## Consequences

Easier: a single source of truth for detection/analysis/humanization logic; fixing or
tuning the engine only requires touching `nobots`, and every consumer (plugin hook,
skills, agents, direct CLI use) picks up the change on its next `uvx` invocation
(cached after first run). The plugin's own footprint shrinks to JSON config, prose
guidance, and one thin shim script.

Harder: the hook now depends on `uv`/`uvx` being installed and on network access (or
a `uv` cache) for the first invocation on a machine, whereas the old bundled script
had no external dependency beyond the Python stdlib. This is accepted because the
project's toolchain is already uv-managed end to end, and the fail-open design means
a missing/broken `uvx` degrades to "hook does nothing" rather than blocking edits.
Pre-publish, the `NOBOTS_SOURCE` override adds one moving part (env var vs. hardcoded
source) that must be remembered when `nobots` finally ships to PyPI and the default
takes over.
