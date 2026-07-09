"""Four fully-local model-based AI-text detectors + score_text.

New code reconstructed from documented detector descriptions — no external
source path. Raw, uncalibrated numbers only; scores are relative, not cutoffs.
Requires the [models] extra (torch + transformers; ~5GB HF weights cached in
~/.cache/huggingface). Each detector is isolated: a failure yields an
"ERR: ..." string so one broken detector never kills the rest.
"""

_QWEN_OBSERVER = "Qwen/Qwen2.5-0.5B"          # base
_QWEN_PERFORMER = "Qwen/Qwen2.5-0.5B-Instruct"  # instruct (shares tokenizer with base)
_GPT2 = "gpt2"
_ROBERTA = "openai-community/roberta-base-openai-detector"

# Module-level caches so repeated calls never reload weights.
_MODELS: dict = {}
_TOKENIZERS: dict = {}


def _device():
    import torch

    return "mps" if torch.backends.mps.is_available() else "cpu"


def _tokenizer(name: str):
    if name not in _TOKENIZERS:
        from transformers import AutoTokenizer

        _TOKENIZERS[name] = AutoTokenizer.from_pretrained(name)
    return _TOKENIZERS[name]


def _causal_lm(name: str):
    if name not in _MODELS:
        from transformers import AutoModelForCausalLM

        _MODELS[name] = AutoModelForCausalLM.from_pretrained(name).to(_device()).eval()
    return _MODELS[name]


def _causal_input_ids(name: str, text: str, cap: int = 1024):
    """Tokenize `text` for a causal LM, truncated to the context cap."""
    import torch

    tok = _tokenizer(name)
    ids = tok(text, return_tensors="pt", truncation=True, max_length=cap)["input_ids"]
    if ids.shape[1] < 2:
        raise ValueError("text too short to score (need at least 2 tokens)")
    return ids.to(_device())


def binoculars(text: str) -> dict:
    """Cross-perplexity of a Qwen base/instruct pair. Lower = more AI-like.

    performer perplexity = mean per-token NLL under the instruct model.
    cross-perplexity = mean over positions of E_observer[-log performer].
    score = performer_ppl / cross_ppl.
    """
    import torch

    # Base and instruct share a tokenizer, so one tokenization serves both.
    ids = _causal_input_ids(_QWEN_OBSERVER, text, cap=1024)
    obs = _causal_lm(_QWEN_OBSERVER)
    perf = _causal_lm(_QWEN_PERFORMER)

    with torch.no_grad():
        obs_logits = obs(ids).logits[0, :-1]   # predictions for tokens 1..n-1
        perf_logits = perf(ids).logits[0, :-1]
    targets = ids[0, 1:]

    perf_logprobs = torch.log_softmax(perf_logits, dim=-1)
    obs_probs = torch.softmax(obs_logits, dim=-1)

    performer_ppl = (-perf_logprobs[range(len(targets)), targets]).mean()
    cross_ppl = (-(obs_probs * perf_logprobs).sum(dim=-1)).mean()

    return {"score": float(performer_ppl / cross_ppl), "ai_direction": "lower"}


def fast_detectgpt(text: str) -> dict:
    """Analytic conditional-probability curvature on gpt2. Higher = more AI-like.

    Single forward pass. Per position, over the vocab logprobs lp and probs p:
    mu = sum(p*lp), var = sum(p*lp^2) - mu^2. Summed over positions,
    d = (observed_logprob_sum - mu_sum) / sqrt(var_sum).
    """
    import torch

    ids = _causal_input_ids(_GPT2, text, cap=1024)
    with torch.no_grad():
        logits = _causal_lm(_GPT2)(ids).logits[0, :-1]
    targets = ids[0, 1:]

    lp = torch.log_softmax(logits, dim=-1)
    p = lp.exp()

    obs_sum = lp[range(len(targets)), targets].sum()
    mu = (p * lp).sum(dim=-1)                      # per-position E[logp]
    var = (p * lp * lp).sum(dim=-1) - mu * mu      # per-position variance
    d = (obs_sum - mu.sum()) / torch.sqrt(var.sum())

    return {"score": float(d), "ai_direction": "higher"}


def gltr(text: str) -> dict:
    """gpt2 next-token rank buckets + mean rank. Higher top-k concentration = more AI-like."""
    import torch

    ids = _causal_input_ids(_GPT2, text, cap=1024)
    with torch.no_grad():
        logits = _causal_lm(_GPT2)(ids).logits[0, :-1]
    targets = ids[0, 1:]

    # rank(actual) = number of tokens the model scored strictly higher (0 = top-1).
    actual_logits = logits[range(len(targets)), targets].unsqueeze(-1)
    ranks = (logits > actual_logits).sum(dim=-1)

    n = len(targets)
    return {
        "top_k_fractions": {
            "top_10": float((ranks < 10).sum() / n),
            "top_100": float((ranks < 100).sum() / n),
            "top_1000": float((ranks < 1000).sum() / n),
        },
        "mean_rank": float(ranks.float().mean()),
        "ai_direction": "higher",
    }


def roberta(text: str) -> dict:
    """openai-community RoBERTa detector. Returns p(AI) in [0, 1]. Higher = more AI-like."""
    import torch

    if _ROBERTA not in _MODELS:
        from transformers import AutoModelForSequenceClassification

        _MODELS[_ROBERTA] = (
            AutoModelForSequenceClassification.from_pretrained(_ROBERTA).to(_device()).eval()
        )
    model = _MODELS[_ROBERTA]
    tok = _tokenizer(_ROBERTA)

    enc = tok(text, return_tensors="pt", truncation=True, max_length=512).to(_device())
    with torch.no_grad():
        probs = torch.softmax(model(**enc).logits[0], dim=-1)

    # Pick the "fake"/AI class by label name; fall back to index 1.
    id2label = getattr(model.config, "id2label", {}) or {}
    ai_idx = next((i for i, name in id2label.items() if "fake" in str(name).lower()), 1)
    return {"p_ai": float(probs[int(ai_idx)]), "ai_direction": "higher"}


def score_text(text: str) -> dict:
    """Run all four detectors; isolate each failure as an ERR string."""
    import nobots.core.models as _self

    out: dict[str, object] = {}
    for name in ("binoculars", "fast_detectgpt", "gltr", "roberta"):
        try:
            # Look the function up on the module so monkeypatching a name works.
            out[name] = getattr(_self, name)(text)
        except Exception as e:  # isolate: never let one detector kill the rest
            out[name] = f"ERR: {type(e).__name__}: {e}"
    return out
