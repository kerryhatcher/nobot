# 4. Keep the quorum detect engine pure and preserve the 0/2 fail-open hook contract

Date: 2026-07-09

## Status

Accepted

## Context

The quorum tell-detector (ported from `hooks/scripts/check_ai_tells.py`) combines vocabulary/phrase matching with stylometric proxies (burstiness, lexical diversity, readability, compression ratio) to detect AI writing patterns. A single noisy signal family (e.g., a few vocabulary hits without supporting context) produces false positives. The robust-aggregation lesson from detector ensembles shows that agreement across independent channels carries signal; trusting one is not enough.

The CLI, TUI, MCP, and hook all need to call the detection engine. Each wraps it with its own I/O semantics (file reading, stdin, MCP transport) and exit behavior.

## Decision

Keep `detect_text(text: str) -> DetectResult` pure:
- No file I/O (caller reads the file, cleans it with `clean_prose`, and passes the string)
- No `sys.exit`, no stderr printing (caller decides messaging and exit code)
- No stdin or other I/O sources
- Returns a `DetectResult` dataclass with `families` (independent signal votes), `agree` (count of voting families), `tells_found` (bool: `agree >= QUORUM`), `context` (informational metrics), and `summary` (if tells_found)

Preserve the fail-open hook contract:
- QUORUM = 2: requires at least 2 independent signal families to agree before declaring tells found
- CLI/hook maps `tells_found=True` → exit 2 (nonzero, feedback to Claude); everything else → exit 0 (silent)
- Hook fails open on any error: a bug in detect_text never blocks or breaks a Write/Edit

## Consequences

Easier:
- Every surface (CLI, TUI, MCP, hook) calls the same pure function; no logic duplication
- Tests isolate the detection engine from I/O and transport
- Future detector implementations (Rule-based, LLM-based) can be composed the same way

More difficult:
- Callers must handle file reading, prose cleaning, and output formatting themselves (but that's correct distribution of concerns; detect_text is not a file processor, it's a text analyzer)