# 6. Humanize uses Pydantic AI, pluggable model, default local Ollama, hard-error if down

Date: 2026-07-09

## Status

Accepted

## Context

The humanize feature needs an LLM-backed agent to rewrite prose and strip AI
tells, grounded in the packaged field guide (`nobots.core.guide.load_guide`).
We need a provider-agnostic agent framework rather than hand-rolled HTTP
calls, and a default that works out of the box without an API key or
network egress, since this is a writing tool developers may run on
sensitive text.

## Decision

Use Pydantic AI (`pydantic-ai`) for the humanize agent, gated behind the
optional `[humanize]` extra. The default model is a local Ollama instance
reached via its OpenAI-compatible endpoint (`OpenAIChatModel` +
`OpenAIProvider` pointed at `http://localhost:11434/v1`), so no API key or
external network call is required by default.

`build_default_model(settings)` builds this model and is overridable via
`model`/`base_url` keys (later sourced from `--model`/config in Task 8).
If Ollama is unreachable, we raise a clear `RuntimeError` instead of
silently falling back to another provider — there is deliberately **no**
multi-provider fallback chain (YAGNI); a hard error with actionable text
("Is Ollama running? Start it with `ollama serve`...") is simpler to reason
about and debug than a chain of silent fallbacks.

`humanize_text(text, model=None)` accepts an already-built model so callers
(and tests) can inject a stub (`pydantic_ai.models.test.TestModel`) without
touching the network; when `model is None` it calls `build_default_model()`.

## Consequences

Easier: swapping models/providers is a one-line change to `build_default_model`
or an injected `model`; tests run fully offline with `TestModel`; the default
experience is private and free (local Ollama, no key).

Harder: users without Ollama running get a hard error rather than automatic
fallback to a hosted provider — this is intentional, but means "it just
works" requires Ollama to be installed and running locally.