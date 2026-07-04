# AI detection tools: open-source options, free APIs, and benchmarks

A companion reference to `ai-writing-guide.md`, covering the practical side of detection: tools you can run yourself, free tiers for programmatic testing, and where the actual benchmark data comes from.

---

## Detecting locally: open-source and offline tools

Every commercial tool discussed in the main guide is a black box. A parallel open-source ecosystem exists for readers who want to run detection locally, organized by how much compute each approach demands.

**Zero-shot detectors** (require a local LLM for log-probabilities):
- **Binoculars** (ICML 2024) — computes a two-model perplexity ratio; claims 90%+ detection at a 0.01% false positive rate, and needs roughly 16GB of VRAM to run a Falcon-7B model pair. Licensed **BSD-3-Clause** — the "MIT" license sometimes listed for it is outdated.
- **Fast-DetectGPT** (ICLR 2024) — roughly 340x faster than the original DetectGPT with a 0.9887 AUROC; MIT-licensed.
- **local-AI-detection** — a llama.cpp-based, fully offline tool released under GPL-3.0; its own author cautions that "AI detection remains inherently unreliable."

**Fine-tuned classifiers** (CPU-viable):
- **desklib/ai-text-detector-v1.01** — a DeBERTa-v3-large model trained on the RAID dataset; MIT-licensed, and led the RAID leaderboard at the time of submission.
- **MAGE** (ACL 2024) — a Longformer-based classifier trained across 27 different LLMs; strong in-distribution performance (0.99 AUROC) that drops sharply to 0.75 AUROC on paraphrased text, making it a useful illustration of how badly paraphrasing degrades even well-trained classifiers.
- Avoid the various **roberta-openai-detector** forks for modern text: they hit roughly 95% accuracy, but only against GPT-2-era output specifically — a genuinely different (and now obsolete) target, not a contradiction of the paraphrase-robustness numbers above.

**No-LLM, CPU-only approaches:**
- **ZipPy** (Thinkst) — a roughly 200-line detector that scores text by its LZMA compression ratio; MIT-licensed, with secondary sources reporting around 82% accuracy that isn't directly confirmed against the repo itself.
- The **NEULIF** approach extracts around 68 stylometric features via TextDescriptives and feeds them to a compact, 25MB CNN that runs entirely on CPU, reporting 97% accuracy — the strongest evidence available that feature-based detection without any LLM in the loop remains genuinely competitive.
- A cluster of actively maintained stylometric libraries do the underlying feature extraction: LexicalRichness, TextDescriptives, pystylometry, faststylometry (implementing Burrows' Delta), and pybiber (67 Biber features) — all MIT- or Apache-licensed. GLTR, the historic GPT-2-era visualization tool, is licensed **Apache-2.0**, not the "MIT" sometimes listed for it.

None of these tools should be run in isolation. The verified consensus across this research is to combine perplexity, burstiness, a classifier score, and stylometric features into a single ensemble, and to treat the result as a probabilistic signal rather than a verdict — the same caution the main guide applies to every commercial tool.

---

## Free detection APIs for programmatic testing

Several services offer free API tiers for programmatic testing:

- **Sapling** — **50,000 chars/day** free via API key; best free tier of the majors.
- **GPTZero** — limited free API testing without an account (the "10,000 words/month" figure often cited is unverified).
- **Copyleaks** — **25,000 free chars/month**, with SDKs in **6 languages**.
- **Winston AI** — **2,000 free credits** (**1 credit/word**).
- **ZeroGPT** — free tier with character limits reported inconsistently (**2,000–15,000** range); the accuracy caveats discussed in the main guide still apply.
- **Hugging Face Inference API** — roughly **300 free requests/hour**, but only for obsolete GPT-2-era detector models; not useful for modern text.
- **Pangram — explicitly not free** (**4 web checks/day**; API **~$0.05 per 1,000 words**). Worth noting since it's the accuracy leader discussed in the main guide.

---

## Where to find the benchmarks

**RAID** is the standard benchmark for evaluating AI text detectors; its official home is **raid-bench.xyz** and the **liamdugan/raid** GitHub repository. Critically, **its-ai.org** presents itself as the "RAID Benchmark Official" page but is actually a competing vendor's marketing page — a distinction worth knowing before citing benchmark figures from it. For paraphrase-attack evaluation specifically, consult **PADBen**; for multilingual detector evaluation, consult **DetectRL-X**.
