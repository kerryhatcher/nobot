# 3. Share clean_prose and prose_windows as the single prose-prep path for all detectors

Date: 2026-07-09

## Status

Accepted

## Context

Each detector (detect, analyze, score) processes markdown/HTML-rich prose from user input. Without a shared prep step, each detector must independently strip noise (frontmatter, code blocks, tables, markup) or risk skewed signals from non-prose content. Additionally, model-based detectors need to handle variable input lengths; long texts may exceed token caps.

## Decision

Define `clean_prose` (stdlib regex) as the single shared prep path for all detectors: strips YAML frontmatter, fenced code blocks, HTML comments, markdown tables, images/links/inline-code, and heading/emphasis/list markers, leaving plain prose sentences. Define `prose_windows` to chunk long prose into consecutive fixed-word windows (default 300 words) for averaging signals over windows when input exceeds model token caps. Both are pure, stdlib-only, and live in `src/nobots/core/prose.py`.

All detect/analyze/score paths call `clean_prose` on input; `score` uses `prose_windows` to average over windows.

## Consequences

**Easier:**
- All detectors see consistent, markup-free prose; signals are not skewed by code or table structure.
- Long inputs are handled uniformly via fixed windows; no detector duplicates chunking logic.
- Pure stdlib means no new dependencies; works in any Python 3.10+ environment.

**Harder:**
- Detectors lose access to raw markup (headings, code language hints, table structure). Design assumes that is noise for prose signals; revisit if a detector needs structural info.
- Fixed window size is opinionated; revisit if averaging over windows doesn't match the detector's semantic model.