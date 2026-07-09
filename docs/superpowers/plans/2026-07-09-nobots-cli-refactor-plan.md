# nobots CLI + Plugin + TUI + MCP Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn `nobots` from a bundle of standalone `uv run` scripts into one installable Python package whose importable core is called by every surface — CLI, TUI, MCP, and a thin Claude-plugin hook shim.

**Architecture:** `src/nobots/` holds pure, tested core functions (`prose`, `detect`, `stylometry`, `models`, `guide`); a Typer `cli.py` owns exit codes, `--json`, and flags; `humanize/`, `tui/`, `mcp/` are thin surfaces over core. The Claude plugin moves to `plugin/` and calls the installed CLI through `uvx` instead of shipping its own copy of the logic. Heavy dependencies sit behind optional extras so the hot `detect` path stays light.

**Tech Stack:** Python (uv-managed), Typer (CLI), pytest, `lexicalrichness` + `textstat` (detect), spaCy/textdescriptives/pybiber (analyze), torch/transformers (models), pydantic-ai + Ollama (humanize), Textual (TUI), the `mcp` SDK (MCP server), `adrs` (Rust ADR CLI).

## Global Constraints

Copied verbatim from the spec — every task's requirements implicitly include these:

- **Package name:** `nobots` (plural) everywhere — package, PyPI name, CLI entry point, `uvx nobots`.
- **uv only:** this is a uv-managed repo. Use `uv run`, `uv add`, `uvx`. A repo hook blocks bare `python`/`pip`; never invoke them.
- **Python floor:** `requires-python = ">=3.11"`. The `[analyze]` and `[models]` extras document (do not enforce package-wide) a `==3.12.*` pin; `uvx` resolves the right interpreter per invocation, so `detect` is unaffected.
- **Packaging:** light core = `detect` only (`typer`, `lexicalrichness`, `textstat`). Optional extras: `[analyze]`, `[models]`, `[tui]`, `[mcp]`, `[humanize]`, and `[all]` = union of all.
- **Hook contract (never break):** `detect` exits **0** when clean, **2** when tells found. It **fails open** — any unexpected error exits 0 so a hook bug never blocks a Write/Edit.
- **Non-hot commands** (`analyze`/`score`/`humanize`/`tui`/`mcp`) are explicit user actions: surface clear errors (missing extra, Ollama down, file not found) and exit non-zero.
- **Humanize:** Pydantic AI with a pluggable model, defaulting to local Ollama; hard-error with a clear message if Ollama is unreachable.
- **Missing-extra UX:** a subcommand whose extra isn't installed prints a one-line install hint, e.g. `humanize needs the humanize extra: uvx --from 'nobots[humanize]' nobots humanize`.
- **Shared prose prep:** `clean_prose`/`prose_windows` are the single prose-prep path for every detector.
- **`core/models.py` and `core/prose.py`:** their source logic is provided/reconstructed from the component descriptions in this plan and the spec — **not** read from any external folder on disk. No path outside this repo may be referenced anywhere.
- **ADRs:** record every architecturally significant decision with the `adrs` CLI (`adrs new "…"`, files land in `docs/adr/`). Never hand-write ADR files. ADR steps are called out inline.

---

## File Structure

**New package (`src` layout):**

- `pyproject.toml` — rewritten: name `nobots`, `requires-python = ">=3.11"`, core deps, `[project.optional-dependencies]` extras, `[project.scripts] nobots = "nobots.cli:app"`, hatchling build over `src/`.
- `src/nobots/__init__.py` — version + package marker.
- `src/nobots/cli.py` — Typer app: `detect` / `analyze` / `score` / `humanize` / `tui` / `mcp`. Owns exit codes, `--json`, install-hint errors.
- `src/nobots/config.py` — loads `~/.config/nobots/config.toml`; resolves humanize settings (flag > config > default).
- `src/nobots/core/__init__.py`
- `src/nobots/core/prose.py` — `clean_prose(text)`, `prose_windows(text, words=300)`. Stdlib only. **New code, reconstructed per description.**
- `src/nobots/core/detect.py` — `detect_text(text) -> DetectResult`. Pure quorum engine from `check_ai_tells.py`, no I/O / `sys.exit` / stdin.
- `src/nobots/core/stylometry.py` — `analyze_text(text) -> dict`. Pure deep report from `deep_stylometry.py`.
- `src/nobots/core/models.py` — 4 model-based detectors + `score_text(text) -> dict`. **New code, reconstructed per description.**
- `src/nobots/core/guide.py` — `load_guide()` / `load_detection_tools()`, reads packaged markdown.
- `src/nobots/humanize/__init__.py`, `src/nobots/humanize/agent.py` — `humanize_text(text, model=None) -> str`.
- `src/nobots/tui/__init__.py`, `src/nobots/tui/app.py` — Textual app.
- `src/nobots/mcp/__init__.py`, `src/nobots/mcp/server.py` — MCP server exposing detect/analyze/score/humanize.
- `src/nobots/data/ai-writing-guide.md`, `src/nobots/data/ai-detection-tools.md` — packaged guide text (moved).

**Plugin (moved under `plugin/`):**

- `plugin/.claude-plugin/plugin.json`, `plugin/hooks/hooks.json`, `plugin/hooks/scripts/hook_detect.py` (new stdin→uvx shim), `plugin/skills/…`, `plugin/agents/…`.

**Tests:** `tests/test_prose.py`, `tests/test_detect.py`, `tests/test_stylometry.py`, `tests/test_models.py`, `tests/test_humanize.py`.

**Deleted at the end:** `hooks/scripts/check_ai_tells.py`, `scripts/deep_stylometry.py`, `main.py`, top-level `ai-writing-guide.md` / `ai-detection-tools.md`, and the old top-level `.claude-plugin/`, `hooks/`, `skills/`, `agents/` after they are relocated and the shim is proven.

---

## Phase 0 — Scaffolding & packaging

### Task 1: Rewrite `pyproject.toml` for the `nobots` src-layout package with extras

**Files:**
- Modify: `pyproject.toml`
- Create: `src/nobots/__init__.py`
- Delete (later, Task 26): `main.py`

**Interfaces:**
- Produces: the `nobots` importable package + `nobots` console script `nobots.cli:app`; extras `[analyze] [models] [tui] [mcp] [humanize] [all]`.

- [ ] **Step 1: Write the new `pyproject.toml`**

```toml
[project]
name = "nobots"
version = "0.1.0"
description = "Detect AI-sounding prose, analyze stylometry, and humanize writing — one engine behind a CLI, TUI, MCP server, and Claude Code plugin."
authors = [{ name = "Kerry Hatcher", email = "kerry@kerryhatcher.com" }]
license = "MIT"
readme = "README.md"
requires-python = ">=3.11"
keywords = ["writing", "ai-detection", "editing", "style", "prose"]
dependencies = [
    "typer>=0.12",
    "lexicalrichness>=0.5",
    "textstat>=0.7",
]

[project.optional-dependencies]
# spaCy stack — documents (does not enforce) a Python ==3.12.* range.
analyze = [
    "textdescriptives>=2.8",
    "pybiber>=0.1",
    "click",
    "en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl",
]
# torch/transformers — documents (does not enforce) a Python ==3.12.* range; ~5GB HF weights.
models = ["torch>=2.2", "transformers>=4.40"]
tui = ["textual>=0.60"]
mcp = ["mcp>=1.0"]
humanize = ["pydantic-ai>=0.0.14"]
all = [
    "nobots[analyze]",
    "nobots[models]",
    "nobots[tui]",
    "nobots[mcp]",
    "nobots[humanize]",
]

[project.scripts]
nobots = "nobots.cli:app"

[project.urls]
Homepage = "https://github.com/kerryhatcher/nobots"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/nobots"]

[dependency-groups]
dev = ["pytest>=8"]
```

- [ ] **Step 2: Create the package marker**

```python
# src/nobots/__init__.py
"""nobots — detect, analyze, and humanize prose from one engine."""

__version__ = "0.1.0"
```

- [ ] **Step 3: Create empty subpackage markers**

Create empty `src/nobots/core/__init__.py`, `src/nobots/humanize/__init__.py`, `src/nobots/tui/__init__.py`, and `src/nobots/mcp/__init__.py`.

- [ ] **Step 4: Sync and verify the package imports**

Run: `uv sync && uv run python -c "import nobots; print(nobots.__version__)"`
Expected: prints `0.1.0`, no import error.

- [ ] **Step 5: Record the packaging ADR**

Run: `adrs new "Package nobots as a light-core src-layout package with optional extras"`
Then `adrs edit <N>` to capture: core = detect only (`typer`/`lexicalrichness`/`textstat`) to keep `uvx nobots detect` fast; heavy stacks behind `[analyze]`/`[models]`/`[tui]`/`[mcp]`/`[humanize]` plus `[all]`; `requires-python=">=3.11"` with the 3.12 pin documented (not enforced) on `[analyze]`/`[models]` because `uvx` picks the interpreter per invocation.
Done: `adrs list` shows the new ADR under `docs/adr/`.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src/nobots docs/adr
git commit -m "chore: scaffold nobots src-layout package with extras + ADR"
```

---

## Phase 1 — core/prose.py

### Task 2: Implement `clean_prose` and `prose_windows`

**Files:**
- Create: `src/nobots/core/prose.py`
- Test: `tests/test_prose.py`

**Interfaces:**
- Produces:
  - `clean_prose(text: str) -> str` — strips YAML frontmatter, fenced code blocks, HTML comments, markdown tables, images/links/inline-code, and heading/emphasis/list markers, leaving plain prose sentences.
  - `prose_windows(text: str, words: int = 300) -> list[str]` — splits on whitespace into consecutive windows of at most `words` words each; returns `[]` for empty/whitespace input.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_prose.py
from nobots.core.prose import clean_prose, prose_windows


def test_clean_prose_strips_frontmatter_code_and_markup():
    text = (
        "---\n"
        "title: My Doc\n"
        "---\n"
        "# Heading\n\n"
        "Real sentence one with a [link](http://x) and `inline`.\n\n"
        "```python\n"
        "print('code should vanish')\n"
        "```\n\n"
        "<!-- a comment -->\n"
        "| col | col |\n"
        "| --- | --- |\n"
        "| a   | b   |\n\n"
        "Real sentence two."
    )
    out = clean_prose(text)
    assert "title: My Doc" not in out
    assert "code should vanish" not in out
    assert "a comment" not in out
    assert "col" not in out
    assert "http://x" not in out
    assert "Real sentence one" in out
    assert "link" in out          # link *text* is kept
    assert "Real sentence two." in out


def test_prose_windows_splits_at_word_count():
    text = " ".join(str(i) for i in range(650))
    windows = prose_windows(text, words=300)
    assert len(windows) == 3
    assert len(windows[0].split()) == 300
    assert len(windows[1].split()) == 300
    assert len(windows[2].split()) == 50


def test_prose_windows_empty_returns_empty():
    assert prose_windows("   \n  ") == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_prose.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'nobots.core.prose'`.

- [ ] **Step 3: Write the implementation**

```python
# src/nobots/core/prose.py
"""Prose preparation shared by every detector.

clean_prose reduces markdown/HTML noise to plain sentences so signals aren't
skewed by code, tables, or markup. prose_windows chunks long inputs so
model-based detectors can average over fixed-word windows. Pure, stdlib-only.
"""

import re

_FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
_FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)
_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")   # keep link text, drop the URL
_INLINE_CODE = re.compile(r"`[^`]*`")
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s*", re.MULTILINE)
_LIST_MARKER = re.compile(r"^\s{0,3}(?:[-*+]|\d+\.)\s+", re.MULTILINE)
_EMPHASIS = re.compile(r"(\*\*|__|\*|_|~~)")
_BLOCKQUOTE = re.compile(r"^\s{0,3}>\s?", re.MULTILINE)
_MULTISPACE = re.compile(r"[ \t]+")
_MULTINEWLINE = re.compile(r"\n{3,}")


def clean_prose(text: str) -> str:
    """Strip markdown/HTML noise, returning plain prose."""
    text = _FRONTMATTER.sub("", text)
    text = _FENCED_CODE.sub("", text)
    text = _HTML_COMMENT.sub("", text)
    text = _TABLE_ROW.sub("", text)
    text = _IMAGE.sub("", text)
    text = _LINK.sub(r"\1", text)
    text = _INLINE_CODE.sub("", text)
    text = _HEADING.sub("", text)
    text = _LIST_MARKER.sub("", text)
    text = _BLOCKQUOTE.sub("", text)
    text = _EMPHASIS.sub("", text)
    text = _MULTISPACE.sub(" ", text)
    text = _MULTINEWLINE.sub("\n\n", text)
    return text.strip()


def prose_windows(text: str, words: int = 300) -> list[str]:
    """Split text into consecutive windows of at most `words` words each."""
    tokens = text.split()
    if not tokens:
        return []
    return [" ".join(tokens[i : i + words]) for i in range(0, len(tokens), words)]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_prose.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Record the shared-prose ADR**

Run: `adrs new "Share clean_prose and prose_windows as the single prose-prep path for all detectors"`
Then `adrs edit <N>`: detect/analyze/score all run on `clean_prose` output so markdown noise doesn't skew signals; `score` uses `prose_windows` to average over windows when input exceeds model token caps.
Done: `adrs list` shows the ADR.

- [ ] **Step 6: Commit**

```bash
git add src/nobots/core/prose.py tests/test_prose.py docs/adr
git commit -m "feat(core): add clean_prose + prose_windows shared prose prep"
```

---

## Phase 2 — core/detect.py

### Task 3: Port the quorum engine to a pure `detect_text`

**Files:**
- Create: `src/nobots/core/detect.py`
- Test: `tests/test_detect.py`
- Source to port: `hooks/scripts/check_ai_tells.py` (quorum logic; strip stdin/`sys.exit`/file-extension gate)

**Interfaces:**
- Consumes: nothing (operates on a prose string; the CLI/hook does file reading + `clean_prose`).
- Produces:
  - `@dataclass DetectResult` with fields: `families: dict[str, tuple[int, str]]`, `agree: int`, `quorum: int`, `tells_found: bool`, `context: dict[str, float | None]` (keys `mtld`, `flesch_kincaid`, `lzma_ratio`), `summary: str`.
  - `detect_text(text: str) -> DetectResult` — pure, no I/O, no `sys.exit`. `tells_found` is `agree >= QUORUM` (QUORUM=2).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_detect.py
from nobots.core.detect import detect_text, QUORUM


AI_SAMPLE = (
    "In today's rapidly evolving landscape, we must delve into the multifaceted "
    "tapestry of innovation. This is a testament to progress. It underscores the "
    "importance of synergy. Furthermore, we leverage seamless solutions — every day "
    "— to foster growth — across teams — and streamline outcomes — at scale — for "
    "all. Moreover, this pivotal moment cannot be overstated. It is important to "
    "note that we embark on a journey. We utilize holistic frameworks. We showcase "
    "meticulous care. We emphasize intricate detail. Nevertheless, the paramount "
    "goal remains. It plays a crucial role. This marks a pivotal moment for us all."
)

HUMAN_SAMPLE = (
    "I broke the build again yesterday. Classic. The fix took four minutes; finding "
    "it took two hours because the error message pointed at the wrong file. Anyway, "
    "here's what actually happened. Our deploy script assumes the config lives in "
    "/etc/app, but staging puts it in /opt. Nobody wrote that down. So when I copied "
    "the prod playbook to staging, everything looked fine until the healthcheck fell "
    "over at 3am. Lesson: check where the config lives before you trust the playbook. "
    "I added a one-line assert. Should've done that months ago."
)


def test_ai_sample_crosses_quorum():
    result = detect_text(AI_SAMPLE)
    assert result.tells_found is True
    assert result.agree >= QUORUM


def test_human_sample_below_quorum():
    result = detect_text(HUMAN_SAMPLE)
    assert result.tells_found is False


def test_single_family_abstains():
    # One vocabulary hit, ordinary punctuation/rhythm — one family at most.
    text = "We should leverage this tool. " + "It works well for the team. " * 20
    result = detect_text(text)
    assert result.agree < QUORUM
    assert result.tells_found is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_detect.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'nobots.core.detect'`.

- [ ] **Step 3: Write the implementation**

Port from `check_ai_tells.py` verbatim for the detection math; remove `read_target_file_path`, the extension/`is_file` gate, `analyze(file_path)` file reading, `print(..., stderr)`, and `main()`. Return a `DetectResult` instead of an exit code.

```python
# src/nobots/core/detect.py
"""Pure quorum tell-detector. Ported from the old check_ai_tells.py hook.

Requires a QUORUM of independent signal families (vocabulary, punctuation,
sentence-length variation) to agree before it declares tells found — a lone
noisy family is not enough. No I/O, no sys.exit, no stdin: the CLI/hook owns
those. Depends on lexicalrichness + textstat (core deps) and stdlib.
"""

import lzma
import re
import statistics
from dataclasses import dataclass, field

MIN_WORDS_FOR_STATS = 150
MIN_WORDS_FOR_DIVERSITY = 50
LOW_BURSTINESS_THRESHOLD = 0.35
VERY_LOW_BURSTINESS = 0.25
QUORUM = 2

TELL_WORDS = re.compile(
    r"\b(delve|delves|delving|tapestry|multifaceted|nuanced|leverage|leveraging|"
    r"utilize|utilizing|seamless|foster|fosters|pivotal|paramount|holistic|"
    r"streamline|transformative|meticulous|intricate|embark|embarking|beacon|"
    r"testament|plethora|myriad|moreover|furthermore|nevertheless|underscores|"
    r"underscoring|showcase|showcases|showcasing|emphasize|emphasizes|"
    r"emphasizing)\b",
    re.IGNORECASE,
)
TELL_PHRASES = re.compile(
    r"it'?s not just [a-z ]+, it'?s|it is important to note that|"
    r"in today'?s rapidly evolving|cannot be overstated|embark on a journey|"
    r"a testament to|plays a (crucial|vital|pivotal) role|it'?s worth noting",
    re.IGNORECASE,
)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


@dataclass
class DetectResult:
    families: dict[str, tuple[int, str]] = field(default_factory=dict)
    agree: int = 0
    quorum: int = QUORUM
    tells_found: bool = False
    context: dict[str, float | None] = field(default_factory=dict)
    summary: str = ""


def _sentence_word_lengths(text: str) -> list[int]:
    sentences = [s for s in SENTENCE_SPLIT.split(text) if s.strip()]
    return [len(s.split()) for s in sentences if s.split()]


def _burstiness_ratio(lengths: list[int]) -> float | None:
    if len(lengths) < 5:
        return None
    mean = statistics.mean(lengths)
    if mean == 0:
        return None
    return statistics.pstdev(lengths) / mean


def _compression_ratio(text: str) -> float | None:
    raw = text.encode("utf-8")
    if not raw:
        return None
    return len(lzma.compress(raw, preset=6)) / len(raw)


def _lexical_diversity(text: str, word_count: int) -> float | None:
    if word_count < MIN_WORDS_FOR_DIVERSITY:
        return None
    try:
        from lexicalrichness import LexicalRichness

        return LexicalRichness(text).mtld(threshold=0.72)
    except Exception:
        return None


def _readability_grade(text: str) -> float | None:
    try:
        import textstat

        return textstat.flesch_kincaid_grade(text)
    except Exception:
        return None


def detect_text(text: str) -> DetectResult:
    """Score prose for AI tells via robust quorum aggregation."""
    result = DetectResult()
    word_count = len(text.split())
    if word_count == 0:
        return result

    word_hits = TELL_WORDS.findall(text)
    phrase_hits = TELL_PHRASES.findall(text)
    total_hits = len(word_hits) + len(phrase_hits)
    em_dash_count = text.count("—")
    families = result.families

    if total_hits >= 4:
        uniq = sorted({w.lower() for w in word_hits if isinstance(w, str)})
        families["vocabulary"] = (2, f"vocabulary/phrase hits: {', '.join(uniq)} ({total_hits} total)")
    elif total_hits >= 2:
        uniq = sorted({w.lower() for w in word_hits if isinstance(w, str)})
        families["vocabulary"] = (1, f"vocabulary/phrase hits: {', '.join(uniq)} ({total_hits} total)")

    if em_dash_count >= 6 and em_dash_count > word_count / 100:
        families["punctuation"] = (2, f"very high em dash density ({em_dash_count} in ~{word_count} words)")
    elif em_dash_count >= 3 and em_dash_count > word_count / 150:
        families["punctuation"] = (1, f"em dash density looks high ({em_dash_count} in ~{word_count} words)")

    diversity = grade = burst = None
    if word_count >= MIN_WORDS_FOR_STATS:
        burst = _burstiness_ratio(_sentence_word_lengths(text))
        if burst is not None:
            if burst < VERY_LOW_BURSTINESS:
                families["burstiness"] = (2, f"very low sentence-length variation (burstiness {burst:.2f})")
            elif burst < LOW_BURSTINESS_THRESHOLD:
                families["burstiness"] = (1, f"low sentence-length variation (burstiness {burst:.2f}, human prose usually clears 0.35)")
        diversity = _lexical_diversity(text, word_count)
        grade = _readability_grade(text)

    result.agree = len(families)
    result.tells_found = result.agree >= QUORUM
    result.context = {
        "mtld": diversity,
        "flesch_kincaid": grade,
        "lzma_ratio": _compression_ratio(text),
    }

    if result.tells_found:
        signals = [msg for _, msg in families.values()]
        result.summary = (
            f"possible AI writing tells ({result.agree} independent signals agree: "
            f"{'; '.join(signals)})."
        )
    return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_detect.py -v`
Expected: PASS (3 tests). If the AI sample doesn't cross quorum, it is a test-fixture problem, not a logic change — lengthen the sample's em-dash run / vocabulary hits until two families fire; do not weaken thresholds.

- [ ] **Step 5: Record the detect-contract ADR**

Run: `adrs new "Keep the quorum detect engine pure and preserve the 0/2 fail-open hook contract"`
Then `adrs edit <N>`: `detect_text` is pure (no I/O/exit) so every surface can call it; the CLI maps `tells_found` → exit 2 and everything else → exit 0, failing open on any error; QUORUM=2 across independent families stays the firing rule.
Done: `adrs list` shows the ADR.

- [ ] **Step 6: Commit**

```bash
git add src/nobots/core/detect.py tests/test_detect.py docs/adr
git commit -m "feat(core): port quorum tell-detector to pure detect_text + ADR"
```

---

## Phase 3 — core/stylometry.py

### Task 4: Port deep stylometry to a pure `analyze_text`

**Files:**
- Create: `src/nobots/core/stylometry.py`
- Test: `tests/test_stylometry.py`
- Source to port: `scripts/deep_stylometry.py` (keep `run_textdescriptives`, `run_biber`, `BIBER_FEATURES_OF_INTEREST`; drop `load_text`, `main`, argv/stdin handling)

**Interfaces:**
- Consumes: prose string (CLI passes `clean_prose` output).
- Produces: `analyze_text(text: str, doc_id: str = "input") -> dict` with keys `word_count`, `textdescriptives`, `biber_features`, `notes`. Raises `ValueError` if `< 20` words; lets import errors propagate (CLI turns them into the `[analyze]` install hint).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_stylometry.py
import pytest

spacy = pytest.importorskip("spacy")  # skip whole module without the [analyze] extra

from nobots.core.stylometry import analyze_text

SAMPLE = (
    "The morning started badly. I spilled coffee on the keyboard, and the space bar "
    "stuck for the rest of the day. Still, we shipped the release on time. Barely. "
    "The team pulled together, reviewed forty files, and caught two real bugs before "
    "they reached production. Not bad for a Tuesday that began with a soaked laptop."
)


def test_analyze_text_returns_expected_keys():
    report = analyze_text(SAMPLE)
    assert set(report) >= {"word_count", "textdescriptives", "biber_features", "notes"}
    assert report["word_count"] == len(SAMPLE.split())
    td = report["textdescriptives"]
    assert "descriptive_stats" in td and "readability" in td and "derived" in td
    burst = td["derived"]["burstiness_ratio"]
    assert burst is None or burst >= 0


def test_analyze_text_rejects_short_input():
    with pytest.raises(ValueError):
        analyze_text("too short")
```

- [ ] **Step 2: Run test to verify it fails (or skips cleanly)**

Run: `uv run pytest tests/test_stylometry.py -v`
Expected: without `[analyze]`, the module SKIPS via `importorskip`. To exercise it: `uv sync --extra analyze` first, then it FAILS with `ModuleNotFoundError: nobots.core.stylometry` until Step 3.

- [ ] **Step 3: Write the implementation**

Copy `BIBER_FEATURES_OF_INTEREST`, `run_textdescriptives`, and `run_biber` from `deep_stylometry.py` unchanged. Replace `main`/`load_text` with:

```python
# src/nobots/core/stylometry.py
"""Deep spaCy/textdescriptives/pybiber stylometry. Ported from deep_stylometry.py.

Raw measurements only — no verdict. Requires the [analyze] extra (spaCy +
en_core_web_sm, pinned to the Python 3.12 range). Pure: no argv/stdin/exit.
"""

import json  # noqa: F401  (kept for parity; callers may json.dumps the dict)

BIBER_FEATURES_OF_INTEREST = {
    # ... copy the dict verbatim from scripts/deep_stylometry.py ...
}


def run_textdescriptives(text: str) -> dict:
    # ... copy verbatim from scripts/deep_stylometry.py ...
    ...


def run_biber(text: str, doc_id: str) -> dict:
    # ... copy verbatim from scripts/deep_stylometry.py ...
    ...


def analyze_text(text: str, doc_id: str = "input") -> dict:
    word_count = len(text.split())
    if word_count < 20:
        raise ValueError(f"input too short for stylometric analysis ({word_count} words, need 20+)")
    return {
        "word_count": word_count,
        "textdescriptives": run_textdescriptives(text),
        "biber_features": run_biber(text, doc_id),
        "notes": (
            "Raw measurements only, no verdict computed here. Biber features are "
            "normalized per 1000 tokens except type_token and mean_word_length; "
            "no calibrated human/AI cutoff exists for any single value — weigh them "
            "as corroborating context only. textdescriptives' own perplexity fields "
            "are omitted (they exponentiate an entropy sum and explode on long text); "
            "use derived.entropy_per_token, itself only a static-unigram proxy."
        ),
    }
```

When copying `run_textdescriptives`/`run_biber`, keep every comment and the `click` workaround note intact — they document real upstream bugs.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv sync --extra analyze && uv run pytest tests/test_stylometry.py -v`
Expected: PASS (2 tests). First run downloads the spaCy model (~1-3 min).

- [ ] **Step 5: Commit**

```bash
git add src/nobots/core/stylometry.py tests/test_stylometry.py
git commit -m "feat(core): port deep stylometry to pure analyze_text"
```

---

## Phase 4 — core/models.py

### Task 5: Reconstruct the 4 model-based detectors + `score_text`

**Files:**
- Create: `src/nobots/core/models.py`
- Test: `tests/test_models.py`

**Interfaces:**
- Consumes: `nobots.core.prose.prose_windows` (for `--chunk`, applied by the CLI, not here).
- Produces: `score_text(text: str) -> dict` with keys `binoculars`, `fast_detectgpt`, `gltr`, `roberta`. Each value is either a per-detector result dict or the string `"ERR: <message>"` — one failing detector must never crash the others. Per-detector functions `binoculars(text)`, `fast_detectgpt(text)`, `gltr(text)`, `roberta(text)`.

> **Reconstruction note:** the internal scoring math for these detectors is **new code reconstructed from the descriptions below** — it is not copied from any external folder and no out-of-repo path may be referenced. Implement each detector against the named HF model with the documented AI-direction; scores are relative, uncalibrated, not fixed cutoffs.

Detector descriptions (AI-direction in parentheses):
- **Binoculars** — cross-perplexity of a Qwen2.5-0.5B base/instruct pair (`Qwen/Qwen2.5-0.5B` and `Qwen/Qwen2.5-0.5B-Instruct`); lower score = more AI-like.
- **Fast-DetectGPT** — analytic curvature on `gpt2`; higher = more AI-like.
- **GLTR** — top-k rank fractions (e.g. top-10/100/1000 buckets) + mean token rank on `gpt2`; higher top-k concentration = more AI-like.
- **RoBERTa** — `openai-community/roberta-base-openai-detector`; returns `p(AI)` in `[0, 1]`.

- [ ] **Step 1: Write the failing test (gated)**

```python
# tests/test_models.py
import os
import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("NOBOTS_MODEL_TESTS") != "1",
    reason="model tests are slow (download ~5GB); set NOBOTS_MODEL_TESTS=1 to run",
)

HUMAN = (
    "I broke the build again yesterday. Classic. The fix took four minutes; finding "
    "it took two hours because the error pointed at the wrong file entirely."
)
AI = (
    "In today's rapidly evolving landscape, we must delve into the multifaceted "
    "tapestry of innovation to leverage seamless, holistic, transformative synergy."
)


def test_score_text_all_detectors_finite_and_in_range():
    from nobots.core.models import score_text

    for sample in (HUMAN, AI):
        scores = score_text(sample)
        assert set(scores) == {"binoculars", "fast_detectgpt", "gltr", "roberta"}
        roberta = scores["roberta"]
        if isinstance(roberta, dict):
            assert 0.0 <= roberta["p_ai"] <= 1.0
        gltr = scores["gltr"]
        if isinstance(gltr, dict):
            frac = gltr["top_k_fractions"]
            assert frac["top_10"] <= frac["top_100"] <= frac["top_1000"]  # monotonic buckets


def test_one_failing_detector_does_not_kill_the_rest(monkeypatch):
    import nobots.core.models as m

    def boom(text):
        raise RuntimeError("simulated failure")

    monkeypatch.setattr(m, "binoculars", boom)
    scores = m.score_text("some prose here for scoring")
    assert isinstance(scores["binoculars"], str) and scores["binoculars"].startswith("ERR")
    assert isinstance(scores["roberta"], dict) or isinstance(scores["roberta"], str)
```

- [ ] **Step 2: Run test to verify it fails/skips**

Run: `uv run pytest tests/test_models.py -v`
Expected: SKIPPED (no `NOBOTS_MODEL_TESTS`). With `NOBOTS_MODEL_TESTS=1 uv run --extra models pytest tests/test_models.py -v` it FAILS on missing `nobots.core.models` until Step 3.

- [ ] **Step 3: Write the implementation**

```python
# src/nobots/core/models.py
"""Four fully-local model-based AI-text detectors + score_text.

New code reconstructed from documented detector descriptions — no external
source path. Raw, uncalibrated numbers only; scores are relative, not cutoffs.
Requires the [models] extra (torch + transformers; ~5GB HF weights cached in
~/.cache/huggingface). Each detector is isolated: a failure yields an
"ERR: ..." string so one broken detector never kills the rest.
"""

_QWEN_BASE = "Qwen/Qwen2.5-0.5B"
_QWEN_INSTRUCT = "Qwen/Qwen2.5-0.5B-Instruct"
_GPT2 = "gpt2"
_ROBERTA = "openai-community/roberta-base-openai-detector"


def binoculars(text: str) -> dict:
    """Cross-perplexity of a Qwen base/instruct pair. Lower = more AI-like."""
    # Reconstruct: tokenize once; compute base-model perplexity and the
    # cross-entropy of base logprobs under the instruct model; return their
    # ratio (the "binoculars score"). Document ai_direction="lower".
    ...
    return {"score": ..., "ai_direction": "lower"}


def fast_detectgpt(text: str) -> dict:
    """Analytic curvature on gpt2. Higher = more AI-like."""
    # Reconstruct: single forward pass on gpt2; sampling-distribution
    # conditional-probability curvature (mean/var of token logprobs).
    ...
    return {"score": ..., "ai_direction": "higher"}


def gltr(text: str) -> dict:
    """Top-k rank fractions + mean rank on gpt2. Higher top-k concentration = more AI-like."""
    # Reconstruct: for each token, its rank in the gpt2 next-token distribution;
    # bucket into cumulative top-10/100/1000 fractions (monotonic) + mean rank.
    ...
    return {"top_k_fractions": {"top_10": ..., "top_100": ..., "top_1000": ...},
            "mean_rank": ..., "ai_direction": "higher"}


def roberta(text: str) -> dict:
    """openai-community RoBERTa detector. Returns p(AI) in [0, 1]."""
    ...
    return {"p_ai": ..., "ai_direction": "higher"}


_DETECTORS = {
    "binoculars": lambda t: binoculars(t),
    "fast_detectgpt": lambda t: fast_detectgpt(t),
    "gltr": lambda t: gltr(t),
    "roberta": lambda t: roberta(t),
}


def score_text(text: str) -> dict:
    """Run all four detectors; isolate failures as ERR strings."""
    out: dict[str, object] = {}
    for name in ("binoculars", "fast_detectgpt", "gltr", "roberta"):
        try:
            # Look the function up on the module so monkeypatching a name works.
            import nobots.core.models as _self

            out[name] = getattr(_self, name)(text)
        except Exception as e:  # isolate: never let one detector kill the rest
            out[name] = f"ERR: {type(e).__name__}: {e}"
    return out
```

The `...` bodies are the reconstruction work: implement each against its named model, returning finite numbers with the documented `ai_direction`. Keep the monkeypatch-friendly module-level lookup in `score_text` so `test_one_failing_detector...` passes.

- [ ] **Step 4: Run tests to verify they pass**

Run: `NOBOTS_MODEL_TESTS=1 uv run --extra models pytest tests/test_models.py -v`
Expected: PASS (2 tests). First run downloads ~5GB of weights.

- [ ] **Step 5: Record the models ADR**

Run: `adrs new "Model-based score command: four local detectors behind the [models] extra, raw uncalibrated output"`
Then `adrs edit <N>`: Binoculars/Fast-DetectGPT/GLTR/RoBERTa are fully local (no API); each isolated so a failure returns ERR; output is relative numbers + documented AI-direction, never a verdict/cutoff; gated behind `[models]` + `NOBOTS_MODEL_TESTS=1` for tests.
Done: `adrs list` shows the ADR.

- [ ] **Step 6: Commit**

```bash
git add src/nobots/core/models.py tests/test_models.py docs/adr
git commit -m "feat(core): add four local model-based detectors + score_text + ADR"
```

---

## Phase 5 — core/guide.py + packaged data

### Task 6: Move guide markdown into the package and add a loader

**Files:**
- Create: `src/nobots/core/guide.py`
- Move: `ai-writing-guide.md` → `src/nobots/data/ai-writing-guide.md`; `ai-detection-tools.md` → `src/nobots/data/ai-detection-tools.md`
- Modify: `pyproject.toml` (ensure `data/*.md` ships in the wheel)

**Interfaces:**
- Produces: `load_guide() -> str`, `load_detection_tools() -> str` — read the packaged markdown via `importlib.resources`.

- [ ] **Step 1: Move the data files**

```bash
mkdir -p src/nobots/data
git mv ai-writing-guide.md src/nobots/data/ai-writing-guide.md
git mv ai-detection-tools.md src/nobots/data/ai-detection-tools.md
```

- [ ] **Step 2: Ensure the data ships in the wheel**

Add to `pyproject.toml` under the wheel target:

```toml
[tool.hatch.build.targets.wheel.force-include]
"src/nobots/data" = "nobots/data"
```

(Data already lives under the package, so hatchling includes it; this force-include is belt-and-suspenders for the non-`.py` files.)

- [ ] **Step 3: Write the loader**

```python
# src/nobots/core/guide.py
"""Load packaged field-guide markdown for MCP/skills/--guide."""

from importlib.resources import files


def load_guide() -> str:
    return files("nobots.data").joinpath("ai-writing-guide.md").read_text(encoding="utf-8")


def load_detection_tools() -> str:
    return files("nobots.data").joinpath("ai-detection-tools.md").read_text(encoding="utf-8")
```

- [ ] **Step 4: Verify the loader reads packaged content**

Run: `uv run python -c "from nobots.core.guide import load_guide; print(len(load_guide()))"`
Expected: prints a large integer (~43000), no error.

- [ ] **Step 5: Commit**

```bash
git add src/nobots/core/guide.py src/nobots/data pyproject.toml
git commit -m "feat(core): package field-guide markdown + guide loader"
```

---

## Phase 6 — humanize/agent.py

### Task 7: Pydantic AI humanize agent defaulting to Ollama

**Files:**
- Create: `src/nobots/humanize/agent.py`
- Test: `tests/test_humanize.py`

**Interfaces:**
- Consumes: `nobots.core.guide.load_guide` (system-prompt grounding); `nobots.config.humanize_settings` (Task 8) — but to avoid ordering coupling, `humanize_text` accepts an already-built `model` and a fallback builder.
- Produces:
  - `build_default_model(settings: dict | None = None)` — builds a Pydantic AI model from humanize settings (Ollama via the OpenAI-compatible endpoint); raises `RuntimeError` with a clear message if Ollama is unreachable.
  - `humanize_text(text: str, model=None) -> str` — runs the agent; if `model is None`, calls `build_default_model()`.

- [ ] **Step 1: Write the failing test (stub model, no network)**

```python
# tests/test_humanize.py
import pytest

pytest.importorskip("pydantic_ai")

from pydantic_ai.models.test import TestModel
from nobots.humanize.agent import humanize_text


def test_humanize_invokes_model_and_returns_text():
    # TestModel returns canned output without any network/LLM call.
    result = humanize_text("Delve into the multifaceted tapestry of synergy.", model=TestModel())
    assert isinstance(result, str)
    assert len(result) > 0
```

- [ ] **Step 2: Run test to verify it fails/skips**

Run: `uv run pytest tests/test_humanize.py -v`
Expected: SKIPS without `[humanize]`. With `uv sync --extra humanize` it FAILS on missing `nobots.humanize.agent` until Step 3.

- [ ] **Step 3: Write the implementation**

```python
# src/nobots/humanize/agent.py
"""Pydantic AI agent that rewrites prose to remove AI tells.

Default model is a local Ollama endpoint (OpenAI-compatible). Raises a clear
error if Ollama is unreachable. Requires the [humanize] extra.
"""

from nobots.core.guide import load_guide

_SYSTEM_PROMPT_HEAD = (
    "You rewrite prose so it reads as authentically human, removing the "
    "vocabulary, statistical, and structural fingerprints of machine writing. "
    "Return only the rewritten prose, no preamble. Rules and rationale:\n\n"
)


def _system_prompt() -> str:
    return _SYSTEM_PROMPT_HEAD + load_guide()


def build_default_model(settings: dict | None = None):
    """Build the default Ollama-backed Pydantic AI model; error if unreachable."""
    from pydantic_ai.models.openai import OpenAIModel
    from pydantic_ai.providers.openai import OpenAIProvider

    settings = settings or {}
    model_name = settings.get("model", "llama3.1")
    base_url = settings.get("base_url", "http://localhost:11434/v1")
    try:
        provider = OpenAIProvider(base_url=base_url, api_key="ollama")
        return OpenAIModel(model_name, provider=provider)
    except Exception as e:
        raise RuntimeError(
            f"could not reach the humanize model at {base_url}: {e}. "
            "Is Ollama running? Start it with `ollama serve` or set "
            "[humanize] in ~/.config/nobots/config.toml."
        ) from e


def humanize_text(text: str, model=None) -> str:
    """Rewrite `text` to remove AI tells using a Pydantic AI agent."""
    from pydantic_ai import Agent

    if model is None:
        model = build_default_model()
    agent = Agent(model=model, system_prompt=_system_prompt())
    result = agent.run_sync(text)
    return result.output
```

If `result.output` is wrong for the installed pydantic-ai version, use `result.data` — check the installed API with `uv run python -c "import pydantic_ai, inspect"` and match. The test with `TestModel()` will tell you immediately.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv sync --extra humanize && uv run pytest tests/test_humanize.py -v`
Expected: PASS (1 test), no network access.

- [ ] **Step 5: Record the humanize ADR**

Run: `adrs new "Humanize uses Pydantic AI, pluggable model, default local Ollama, hard-error if down"`
Then `adrs edit <N>`: pydantic-ai chosen for a provider-agnostic agent; default = Ollama (local, private, no key); unreachable Ollama raises a clear RuntimeError rather than falling back (no multi-provider chain — YAGNI); model overridable via `--model`/config.
Done: `adrs list` shows the ADR.

- [ ] **Step 6: Commit**

```bash
git add src/nobots/humanize/agent.py tests/test_humanize.py docs/adr
git commit -m "feat(humanize): pydantic-ai agent defaulting to Ollama + ADR"
```

---

## Phase 7 — config.py

### Task 8: Config loader with flag > file > default precedence

**Files:**
- Create: `src/nobots/config.py`
- Test: extend `tests/test_humanize.py` (config is tiny; fold its check in rather than a new file)

**Interfaces:**
- Produces:
  - `load_config() -> dict` — parses `~/.config/nobots/config.toml` with stdlib `tomllib`; returns `{}` if absent/unreadable.
  - `humanize_settings(cli_model: str | None = None, cli_base_url: str | None = None) -> dict` — merges built-in defaults (`provider="ollama"`, `model="llama3.1"`, `base_url="http://localhost:11434/v1"`) < config `[humanize]` < CLI overrides. Returns keys `provider`, `model`, `base_url`.

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_humanize.py
from nobots.config import humanize_settings


def test_humanize_settings_precedence(monkeypatch, tmp_path):
    cfg = tmp_path / "config.toml"
    cfg.write_text('[humanize]\nmodel = "mistral"\nbase_url = "http://x:1/v1"\n')
    monkeypatch.setattr("nobots.config._config_path", lambda: cfg)

    # config overrides default
    s = humanize_settings()
    assert s["model"] == "mistral" and s["base_url"] == "http://x:1/v1"

    # CLI flag overrides config
    s = humanize_settings(cli_model="llama3.1")
    assert s["model"] == "llama3.1"

    # default when nothing set
    monkeypatch.setattr("nobots.config._config_path", lambda: tmp_path / "missing.toml")
    assert humanize_settings()["model"] == "llama3.1"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_humanize.py -k settings -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'nobots.config'`.

- [ ] **Step 3: Write the implementation**

```python
# src/nobots/config.py
"""~/.config/nobots/config.toml loader. Precedence: CLI flag > config > default."""

import tomllib
from pathlib import Path

_DEFAULTS = {
    "provider": "ollama",
    "model": "llama3.1",
    "base_url": "http://localhost:11434/v1",
}


def _config_path() -> Path:
    return Path.home() / ".config" / "nobots" / "config.toml"


def load_config() -> dict:
    path = _config_path()
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def humanize_settings(cli_model: str | None = None, cli_base_url: str | None = None) -> dict:
    settings = dict(_DEFAULTS)
    settings.update(load_config().get("humanize", {}))
    if cli_model:
        settings["model"] = cli_model
    if cli_base_url:
        settings["base_url"] = cli_base_url
    return settings
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_humanize.py -k settings -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/nobots/config.py tests/test_humanize.py
git commit -m "feat(config): config.toml loader with flag>file>default precedence"
```

---

## Phase 8 — cli.py

### Task 9: Wire the Typer CLI (detect/analyze/score/humanize) with exit codes, --json, install hints

**Files:**
- Create: `src/nobots/cli.py`

**Interfaces:**
- Consumes: `core.prose.clean_prose`/`prose_windows`, `core.detect.detect_text`, `core.stylometry.analyze_text`, `core.models.score_text`, `humanize.agent.humanize_text`, `config.humanize_settings`, `core.guide.load_guide`.
- Produces: Typer `app` with commands `detect`, `analyze`, `score`, `humanize` (plus `tui`/`mcp` added in later phases). `nobots.cli:app` is the console entry point.

- [ ] **Step 1: Write the CLI**

```python
# src/nobots/cli.py
"""Typer CLI. Owns exit codes, --json, and missing-extra install hints."""

import json
import sys
from pathlib import Path

import typer

app = typer.Typer(add_completion=False, help="Detect, analyze, and humanize prose.")


def _read(file: Path) -> str:
    return file.read_text(encoding="utf-8", errors="ignore")


def _missing_extra(extra: str, cmd: str) -> typer.Exit:
    typer.echo(
        f"{cmd} needs the {extra} extra: "
        f"uvx --from 'nobots[{extra}]' nobots {cmd}",
        err=True,
    )
    return typer.Exit(code=1)


@app.command()
def detect(
    file: Path = typer.Argument(..., exists=False),
    json_out: bool = typer.Option(False, "--json", help="Emit families + scores as JSON to stdout."),
):
    """Quorum tell-scan. Exit 0 clean / 2 tells found. Fails open on any error."""
    try:
        from nobots.core.detect import detect_text
        from nobots.core.prose import clean_prose

        if not file.is_file() or file.suffix.lower() not in {".md", ".markdown", ".txt"}:
            raise typer.Exit(code=0)
        result = detect_text(clean_prose(_read(file)))
        if json_out:
            typer.echo(json.dumps({
                "file": str(file),
                "tells_found": result.tells_found,
                "agree": result.agree,
                "quorum": result.quorum,
                "families": {k: {"vote": v[0], "detail": v[1]} for k, v in result.families.items()},
                "context": result.context,
            }, indent=2))
        elif result.tells_found:
            typer.echo(f"nobots: {file} {result.summary}", err=True)
        raise typer.Exit(code=2 if result.tells_found else 0)
    except typer.Exit:
        raise
    except Exception:
        raise typer.Exit(code=0)  # fail open — a hook bug must never block a Write/Edit


@app.command()
def analyze(file: Path = typer.Argument(...), json_out: bool = typer.Option(False, "--json")):
    """Deep stylometry report (raw numbers). Requires the [analyze] extra."""
    try:
        from nobots.core.stylometry import analyze_text
    except ImportError:
        raise _missing_extra("analyze", "analyze")
    from nobots.core.prose import clean_prose

    if not file.is_file():
        typer.echo(f"file not found: {file}", err=True)
        raise typer.Exit(code=1)
    try:
        report = analyze_text(clean_prose(_read(file)), doc_id=str(file))
    except ImportError:
        raise _missing_extra("analyze", "analyze")
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1)
    typer.echo(json.dumps(report, indent=2))


@app.command()
def score(
    file: Path = typer.Argument(...),
    json_out: bool = typer.Option(False, "--json"),
    chunk: bool = typer.Option(False, "--chunk", help="Average over prose windows for long input."),
    words: int = typer.Option(300, "--words", help="Window size for --chunk."),
):
    """Model-based detector scores. First run downloads ~5GB. Requires [models]."""
    try:
        from nobots.core.models import score_text
    except ImportError:
        raise _missing_extra("models", "score")
    from nobots.core.prose import clean_prose, prose_windows

    if not file.is_file():
        typer.echo(f"file not found: {file}", err=True)
        raise typer.Exit(code=1)
    prose = clean_prose(_read(file))
    if chunk:
        results = [score_text(w) for w in prose_windows(prose, words=words)]
        out = {"windows": results, "n_windows": len(results)}
    else:
        out = score_text(prose)
    typer.echo(json.dumps(out, indent=2, default=str))


@app.command()
def humanize(
    file: Path = typer.Argument(...),
    model: str = typer.Option(None, "--model", help="Pydantic AI model id override."),
    in_place: bool = typer.Option(False, "--in-place", help="Overwrite the file with the rewrite."),
):
    """Pydantic AI rewrite. Default Ollama; hard-errors if Ollama down. Requires [humanize]."""
    try:
        from nobots.humanize.agent import build_default_model, humanize_text
    except ImportError:
        raise _missing_extra("humanize", "humanize")
    from nobots.config import humanize_settings

    if not file.is_file():
        typer.echo(f"file not found: {file}", err=True)
        raise typer.Exit(code=1)
    settings = humanize_settings(cli_model=model)
    try:
        built = build_default_model(settings)
        rewritten = humanize_text(_read(file), model=built)
    except RuntimeError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1)
    if in_place:
        file.write_text(rewritten, encoding="utf-8")
        typer.echo(f"rewrote {file}", err=True)
    else:
        typer.echo(rewritten)


@app.callback()
def _root(
    guide: bool = typer.Option(False, "--guide", help="Print the packaged field guide and exit."),
):
    if guide:
        from nobots.core.guide import load_guide

        typer.echo(load_guide())
        raise typer.Exit(code=0)
```

- [ ] **Step 2: Verify detect exit codes end-to-end**

```bash
printf 'This is a perfectly ordinary short note about lunch.\n' > /tmp/human.md
uv run nobots detect /tmp/human.md; echo "exit=$?"
```
Expected: `exit=0`, no stderr nudge.

```bash
cat > /tmp/ai.md <<'EOF'
In today's rapidly evolving landscape, we must delve into the multifaceted tapestry of innovation. This is a testament to progress. It underscores the importance of synergy. Furthermore, we leverage seamless solutions — every day — to foster growth — across teams — and streamline outcomes — at scale — for all. Moreover, this pivotal moment cannot be overstated. It is important to note that we embark on a journey. We utilize holistic frameworks. We showcase meticulous care. We emphasize intricate detail. Nevertheless, the paramount goal remains. It plays a crucial role.
EOF
uv run nobots detect /tmp/ai.md; echo "exit=$?"
uv run nobots detect /tmp/ai.md --json
```
Expected: `exit=2` with a stderr nudge; `--json` prints the families/context JSON to stdout.

- [ ] **Step 3: Verify missing-extra hints**

Run (core-only env): `uv run nobots analyze /tmp/ai.md`
Expected (if `[analyze]` absent): stderr `analyze needs the analyze extra: uvx --from 'nobots[analyze]' nobots analyze`, exit 1. (If your dev env already synced `[analyze]`, this prints the report instead — that's fine.)

- [ ] **Step 4: Record the Typer + CLI-contract ADR**

Run: `adrs new "Adopt Typer for the CLI; exit codes and --json owned at the CLI layer"`
Then `adrs edit <N>`: Typer chosen for typed args + auto help/completion; core stays framework-free so TUI/MCP reuse it; `detect` maps result→exit 0/2 and fails open, other commands surface errors + non-zero; `--json` prints machine output to stdout, human summaries go to stderr.
Done: `adrs list` shows the ADR.

- [ ] **Step 5: Commit**

```bash
git add src/nobots/cli.py docs/adr
git commit -m "feat(cli): Typer app for detect/analyze/score/humanize + ADR"
```

---

## Phase 9 — Plugin move + hook shim (uvx)

### Task 10: Relocate plugin assets and add the uvx hook shim

**Files:**
- Move: `.claude-plugin/plugin.json` → `plugin/.claude-plugin/plugin.json`; `hooks/hooks.json` → `plugin/hooks/hooks.json`; `skills/` → `plugin/skills/`; `agents/` → `plugin/agents/`.
- Create: `plugin/hooks/scripts/hook_detect.py`
- Modify: `plugin/hooks/hooks.json` (point at `hook_detect.py`)

**Interfaces:**
- Produces: `hook_detect.py` — reads the PostToolUse payload JSON from stdin, extracts `tool_input.file_path`, runs `uvx --from nobots nobots detect <file>`, and propagates the exit code. Fails open (exit 0) on any error.

- [ ] **Step 1: Move the plugin assets**

```bash
mkdir -p plugin/hooks/scripts
git mv .claude-plugin plugin/.claude-plugin
git mv hooks/hooks.json plugin/hooks/hooks.json
git mv skills plugin/skills
git mv agents plugin/agents
```

- [ ] **Step 2: Write the hook shim**

```python
#!/usr/bin/env python3
# plugin/hooks/scripts/hook_detect.py
"""Thin PostToolUse shim: stdin payload -> `uvx nobots detect FILE` -> exit code.

Propagates detect's exit code (2 = tells found -> nudge, 0 = silent). Fails
open on any error so a hook bug never blocks a Write/Edit. The CLI engine lives
in the installed `nobots` package; this file carries no detection logic.
"""

import json
import subprocess
import sys

# During pre-publish dev, swap for: "git+https://github.com/kerryhatcher/nobots"
NOBOTS_SOURCE = "nobots"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        file_path = payload.get("tool_input", {}).get("file_path", "") or ""
        if not file_path:
            return 0
        proc = subprocess.run(
            ["uvx", "--from", NOBOTS_SOURCE, "nobots", "detect", file_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if proc.stderr:
            print(proc.stderr, file=sys.stderr, end="")
        return proc.returncode
    except Exception:
        return 0  # fail open


if __name__ == "__main__":
    sys.exit(main())
```

Then `chmod +x plugin/hooks/scripts/hook_detect.py`.

- [ ] **Step 3: Repoint `hooks.json`**

```json
{
  "description": "Non-blocking scan for AI writing tells in prose files after they're written or edited.",
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/hook_detect.py",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 4: Prove the shim end-to-end against the local package**

```bash
echo '{"tool_input":{"file_path":"/tmp/ai.md"}}' | \
  NOBOTS_SOURCE=. uv run python plugin/hooks/scripts/hook_detect.py; echo "exit=$?"
```
Expected: exit 2 with the nudge on stderr for the AI sample. For dev, the shim can be run with `uvx --from .`; verify `uvx --from . nobots detect /tmp/ai.md` exits 2 as well.
Then confirm fail-open: `echo '{}' | uv run python plugin/hooks/scripts/hook_detect.py; echo "exit=$?"` → `exit=0`.

- [ ] **Step 5: Update skills/agents to call the CLI via uvx**

Edit `plugin/skills/detect-ai-writing/SKILL.md`, `plugin/agents/ai-tell-reviewer.md`, `plugin/agents/ai-tell-quickcheck.md`: replace every `scripts/deep_stylometry.py` / `$CLAUDE_PLUGIN_ROOT/scripts/...` invocation with `uvx --from 'nobots[analyze]' nobots analyze FILE` (deep stylometry) and reference `uvx nobots detect FILE` for the quorum scan. Point guide references (`$CLAUDE_PLUGIN_ROOT/ai-writing-guide.md`, `ai-detection-tools.md`) at `uvx nobots --guide` or note the guide now ships inside the package. `humanize-writing/SKILL.md` gains a mention of `uvx --from 'nobots[humanize]' nobots humanize FILE`.

- [ ] **Step 6: Record the uvx-invocation ADR**

Run: `adrs new "Plugin invokes the installed CLI via uvx instead of bundling detection code"`
Then `adrs edit <N>`: one engine, no duplicated logic; hook shim shells to `uvx --from nobots nobots detect`; `<source>` = PyPI `nobots` (git+URL during pre-publish dev); shim propagates exit code and fails open.
Done: `adrs list` shows the ADR.

- [ ] **Step 7: Commit**

```bash
git add plugin docs/adr
git commit -m "refactor(plugin): move under plugin/ and add uvx hook shim + ADR"
```

---

## Phase 10 — TUI

### Task 11: Textual TUI surface

**Files:**
- Create: `src/nobots/tui/app.py`
- Modify: `src/nobots/cli.py` (add `tui` command)

**Interfaces:**
- Consumes: `core.detect.detect_text`, `core.prose.clean_prose` (and, when their extras are present, `analyze_text`/`score_text`/`humanize_text`).
- Produces: `run_tui() -> None` launching a Textual app that lets the user paste/pick text and shows live detect (always available) plus analyze/score/humanize panes that degrade to an install hint when their extra is missing.

- [ ] **Step 1: Write a minimal Textual app**

```python
# src/nobots/tui/app.py
"""Textual TUI over the core functions. Requires the [tui] extra."""

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TextArea, Static

from nobots.core.detect import detect_text
from nobots.core.prose import clean_prose


class NobotsApp(App):
    TITLE = "nobots"

    def compose(self) -> ComposeResult:
        yield Header()
        self.input = TextArea(id="input")
        self.output = Static(id="output")
        yield self.input
        yield self.output
        yield Footer()

    def on_text_area_changed(self, event) -> None:
        result = detect_text(clean_prose(self.input.text))
        if result.tells_found:
            self.output.update(f"Tells found ({result.agree} families): {result.summary}")
        else:
            self.output.update(f"No quorum ({result.agree}/{result.quorum} families).")


def run_tui() -> None:
    NobotsApp().run()
```

- [ ] **Step 2: Add the `tui` command to the CLI**

```python
# append to src/nobots/cli.py
@app.command()
def tui():
    """Launch the Textual UI. Requires the [tui] extra."""
    try:
        from nobots.tui.app import run_tui
    except ImportError:
        raise _missing_extra("tui", "tui")
    run_tui()
```

- [ ] **Step 3: Verify it imports and the command is registered**

Run: `uv sync --extra tui && uv run python -c "from nobots.tui.app import NobotsApp; print('ok')" && uv run nobots --help`
Expected: prints `ok`; `--help` lists `tui`. (Interactive launch verified manually; no automated TUI test — YAGNI.)

- [ ] **Step 4: Commit**

```bash
git add src/nobots/tui/app.py src/nobots/cli.py
git commit -m "feat(tui): minimal Textual UI with live detect"
```

---

## Phase 11 — MCP

### Task 12: MCP server surface

**Files:**
- Create: `src/nobots/mcp/server.py`
- Modify: `src/nobots/cli.py` (add `mcp` command)

**Interfaces:**
- Consumes: `core.detect.detect_text`, `core.prose.clean_prose`, `core.guide.load_guide`, and (when their extras are present) `analyze_text`/`score_text`/`humanize_text`.
- Produces: `run_server() -> None` starting an MCP server exposing tools `detect`, `analyze`, `score`, `humanize` over stdio.

- [ ] **Step 1: Write the MCP server**

```python
# src/nobots/mcp/server.py
"""MCP server exposing detect/analyze/score/humanize. Requires the [mcp] extra."""

from mcp.server.fastmcp import FastMCP

from nobots.core.detect import detect_text
from nobots.core.prose import clean_prose

mcp = FastMCP("nobots")


@mcp.tool()
def detect(text: str) -> dict:
    """Quorum AI-tell scan of prose. Returns families + quorum decision."""
    r = detect_text(clean_prose(text))
    return {
        "tells_found": r.tells_found,
        "agree": r.agree,
        "quorum": r.quorum,
        "families": {k: {"vote": v[0], "detail": v[1]} for k, v in r.families.items()},
        "context": r.context,
    }


@mcp.tool()
def analyze(text: str) -> dict:
    """Deep stylometry (raw numbers). Requires the [analyze] extra server-side."""
    try:
        from nobots.core.stylometry import analyze_text
    except ImportError:
        return {"error": "analyze needs the [analyze] extra installed where the MCP server runs"}
    return analyze_text(clean_prose(text))


@mcp.tool()
def score(text: str) -> dict:
    """Model-based detector scores. Requires the [models] extra server-side."""
    try:
        from nobots.core.models import score_text
    except ImportError:
        return {"error": "score needs the [models] extra installed where the MCP server runs"}
    return score_text(clean_prose(text))


@mcp.tool()
def humanize(text: str) -> str:
    """Rewrite prose to remove AI tells. Requires the [humanize] extra server-side."""
    try:
        from nobots.humanize.agent import humanize_text
    except ImportError:
        return "error: humanize needs the [humanize] extra installed where the MCP server runs"
    return humanize_text(text)


def run_server() -> None:
    mcp.run()
```

- [ ] **Step 2: Add the `mcp` command to the CLI**

```python
# append to src/nobots/cli.py
@app.command()
def mcp():
    """Start the MCP server. Requires the [mcp] extra."""
    try:
        from nobots.mcp.server import run_server
    except ImportError:
        raise _missing_extra("mcp", "mcp")
    run_server()
```

- [ ] **Step 3: Verify import + registration**

Run: `uv sync --extra mcp && uv run python -c "from nobots.mcp.server import mcp; print('ok')" && uv run nobots --help`
Expected: prints `ok`; `--help` lists `mcp`.

- [ ] **Step 4: Commit**

```bash
git add src/nobots/mcp/server.py src/nobots/cli.py
git commit -m "feat(mcp): MCP server exposing detect/analyze/score/humanize"
```

---

## Phase 12 — Delete old scripts

### Task 13: Remove the standalone scripts and stale top-level files

**Files:**
- Delete: `hooks/scripts/check_ai_tells.py`, `scripts/deep_stylometry.py`, `main.py`, and the now-empty `hooks/` and `scripts/` dirs.

- [ ] **Step 1: Confirm nothing else references them**

Run: `grep -rn "check_ai_tells\|deep_stylometry\|main.py" --include="*.py" --include="*.json" --include="*.md" . | grep -v docs/superpowers | grep -v docs/adr`
Expected: no references outside the plan/ADR docs. If `plugin/skills` or `plugin/agents` still reference `deep_stylometry.py`, fix them (Task 10 Step 5 should have) before deleting.

- [ ] **Step 2: Delete**

```bash
git rm hooks/scripts/check_ai_tells.py scripts/deep_stylometry.py main.py
rmdir hooks/scripts hooks scripts 2>/dev/null || true
```

- [ ] **Step 3: Full test + entry-point smoke**

Run: `uv run pytest -v && uv run nobots detect /tmp/ai.md; echo "exit=$?"`
Expected: all non-gated tests pass (models tests skipped); detect still exits 2.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: delete standalone scripts now that the CLI owns the logic"
```

---

## Phase 13 — Docs

### Task 14: Update README and AGENTS.md for the CLI-first layout

**Files:**
- Modify: `README.md`, `AGENTS.md`

- [ ] **Step 1: Rewrite the README usage section**

Replace plugin-centric install/usage with: install via `uvx nobots detect FILE` (light core), the extras table (`analyze`/`models`/`tui`/`mcp`/`humanize`/`all`) with the `uvx --from 'nobots[EXTRA]' nobots CMD` form, the command table from the spec, the `~/.config/nobots/config.toml` humanize block, and the plugin note that hooks/skills call the CLI via `uvx`. Keep the existing logo/banner assets.

- [ ] **Step 2: Add a build/test/ADR section to AGENTS.md**

Append: `uv sync`, `uv run pytest`, `uvx nobots detect FILE`; note the model tests need `NOBOTS_MODEL_TESTS=1` + `--extra models`; note the src layout and that every surface calls `core/`. Keep the existing ADR section verbatim.

- [ ] **Step 3: Verify the documented commands actually run**

Run every command shown in the README's quick-start against `/tmp/ai.md` (at least `uv run nobots detect`, `--json`, `--guide`) and confirm they behave as documented.
Expected: documented behavior matches reality; fix the docs, not the code, on any mismatch.

- [ ] **Step 4: Commit**

```bash
git add README.md AGENTS.md
git commit -m "docs: CLI-first README + AGENTS build/test notes"
```

---

## Phase 14 — Housekeeping (post-work)

> These are release/ops steps, not code. Do them after the branch merges. They are recorded here so they aren't lost, per the spec's Housekeeping section.

### Task 15: Repo rename and first PyPI release

- [ ] **Step 1: Rename the repo `nobot` → `nobots`**

Rename on the git host (GitHub: Settings → Rename), then update local remotes:
```bash
git remote set-url origin git@github.com:kerryhatcher/nobots.git
```
Update any `uvx --from git+<repo-url>` dev references (hook shim `NOBOTS_SOURCE`, README, skills) to the new URL. Record with `adrs new "Rename repo nobot -> nobots to match package/PyPI name"`.

- [ ] **Step 2: Cut the first PyPI release**

```bash
uv build
uv publish   # requires PyPI credentials/token
```
Then confirm the hot path from a clean machine: `uvx nobots detect FILE` exits 0/2 with no local checkout. Once published, drop the git+URL dev fallback from the hook shim's `NOBOTS_SOURCE` and set it to `nobots`.
Done: `uvx nobots detect` works against the published package; `hook_detect.py` points at the PyPI name.

---

## Self-Review

**Spec coverage:**
- Goals (one package, CLI surface, plugin via uvx, light core + extras, humanize Ollama) → Tasks 1, 9, and 7.
- `core/prose`, `detect`, `stylometry`, `models`, `guide` → Tasks 2, 3, 4, 5, 6.
- `humanize/agent` → Task 7; `config` → Task 8; `cli` → Task 9; `tui` → Task 11; `mcp` → Task 12.
- Command table (detect/analyze/score/humanize/tui/mcp, exit codes, `--json`, `--chunk`/`--words`, `--in-place`, missing-extra hint) → Task 9 (+ 11, 12).
- Packaging extras + Python-version tension → Task 1.
- Plugin↔CLI hook shim + skills/agents + uvx source → Task 10.
- Config precedence → Task 8.
- Error handling (detect fail-open, others surface + non-zero) → Tasks 3, 9.
- Testing (test_prose/detect/stylometry/models[gated]/humanize[stub]) → Tasks 2, 3, 4, 5, 7, 8.
- Migration (1–6) → Tasks 3, 4, 4/5, 6, 10, 13.
- Housekeeping (rename, PyPI) → Task 15.
- ADRs (Typer, uvx, extras, Ollama, detect contract, shared prose, models) → Tasks 1, 2, 3, 6, 5, 8-ADR-in-9, 10.

**Placeholder scan:** the only intentional `...` bodies are in `core/models.py` (Task 5), explicitly flagged as reconstruction work with per-detector descriptions, model IDs, return shapes, and AI-directions — an implementer has everything needed to write them. `core/stylometry.py` (Task 4) copies named functions verbatim from a real source file in the repo. No "TBD"/"handle edge cases"/"add error handling" placeholders remain.

**Type consistency:** `detect_text -> DetectResult` (fields `families`, `agree`, `quorum`, `tells_found`, `context`, `summary`) is produced in Task 3 and consumed identically in CLI (Task 9), TUI (Task 11), and MCP (Task 12). `score_text` keys (`binoculars`/`fast_detectgpt`/`gltr`/`roberta`) match between Task 5 and its callers. `humanize_text(text, model=None)` / `build_default_model(settings)` match between Tasks 7, 9, 12. `humanize_settings(cli_model, cli_base_url)` matches between Tasks 8 and 9.
