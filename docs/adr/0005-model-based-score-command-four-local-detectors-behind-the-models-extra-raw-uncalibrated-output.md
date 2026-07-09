# 5. Model-based score command: four local detectors behind the [models] extra, raw uncalibrated output

Date: 2026-07-09

## Status

Accepted

## Context

Beyond the pure stdlib quorum detector (ADR 4) and the spaCy stylometry (analyze extra), we want stronger per-token statistical signals from language models. Four well-known AI-text detection approaches — Binoculars, Fast-DetectGPT, GLTR, and the OpenAI RoBERTa detector — each score text against a language model. They pull in torch + transformers and ~5GB of Hugging Face weights, which most users of the light CLI never need.

These detectors are heuristics over small models on short text. Their raw numbers are relative and uncalibrated; there is no trustworthy fixed cutoff that separates human from AI, and pretending otherwise would produce confident false verdicts.

## Decision

- `src/nobots/core/models.py` implements `binoculars`, `fast_detectgpt`, `gltr`, `roberta`, and `score_text`, all **fully local** (no network API at scoring time; weights are cached under `~/.cache/huggingface`).
- Reconstructed scoring math from published descriptions — no external source path is referenced:
  - **Binoculars**: performer perplexity / cross-perplexity over a shared-tokenizer Qwen2.5-0.5B base (observer) + instruct (performer) pair. Lower = more AI-like.
  - **Fast-DetectGPT**: single-forward analytic conditional-probability curvature on gpt2. Higher = more AI-like.
  - **GLTR**: cumulative top-10/100/1000 next-token rank fractions + mean rank on gpt2. Higher concentration = more AI-like.
  - **RoBERTa**: `openai-community/roberta-base-openai-detector` softmax p(AI). Higher = more AI-like.
- Output is **relative numbers plus a documented `ai_direction`, never a verdict or cutoff**.
- Each detector is **isolated**: `score_text` looks functions up on the module via `getattr` (monkeypatch-friendly) and catches any exception, returning `"ERR: <type>: <msg>"` so one broken/uninstalled detector never kills the rest.
- Models/tokenizers are cached at module level so repeated calls don't reload. Device is MPS when available, else CPU. Inputs are truncated to each model's context (gpt2/qwen 1024, roberta 512) under `torch.no_grad()`.
- Gated behind the `[models]` optional extra; its tests run only when `NOBOTS_MODEL_TESTS=1` (they download ~5GB and are slow), and skip cleanly otherwise.

## Consequences

- The default install stays light; heavy ML deps are opt-in.
- Callers get four independent signals to combine, but must treat them as relative evidence, not classifications.
- A missing extra, an unavailable model, or a too-short input degrades to one ERR string rather than crashing the score.
- CI without the env var skips the model tests, so they don't gate ordinary runs; correctness on real weights is verified only when explicitly enabled.
