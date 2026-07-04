# The fingerprints of artificial prose: a complete field guide

**AI-generated text leaves detectable traces across vocabulary, structure, statistics, and content depth** — and understanding these patterns is the single most important step toward both identifying machine writing and producing text that reads as genuinely human. Despite rapid improvements in large language models from GPT-3.5 through GPT-5 and Claude, research from Carnegie Mellon, Stanford, MIT, and dozens of detection companies confirms that AI prose still carries measurable signatures: predictable word choices, uniform sentence rhythms, shallow content, and an unmistakable emotional flatness. This report synthesizes findings from peer-reviewed studies, detection tool documentation, writing communities, and adversarial research published between 2023 and early 2026 to map every known marker, explain the tools built to catch them, and provide actionable instructions for producing text that avoids these tells entirely.

---

## The vocabulary fingerprint: words AI can't stop using

The most immediately recognizable sign of AI writing is its vocabulary. LLMs draw from probability distributions that favor certain words far beyond their frequency in natural human writing, creating what researchers at Pangram Labs call an **"aidiolect"** — a model-specific vocabulary fingerprint.

Yet these vocabulary markers prove **time-bound and model-specific**, with roughly one model-generation's worth of half-life. As new models emerge and writers adapt to blocklists, today's collection of AI tells partially decays; the 2023–24 vocabulary list, frequently cited throughout this guide, remains useful for **dating** a text but is now a comparatively weak **detection** signal on its own. Research on the erosion of LLM signatures under paraphrasing explains why: surface vocabulary erodes fastest, while **nominalization density, clause hierarchy, and metadiscourse structure** remain markedly more robust to rewording — supporting this guide's broader thesis that structural tells outlast vocabulary tells.

The single most cited AI tell is the word **"delve,"** which ChatGPT used at several times the human baseline rate — independent corpus analyses suggest roughly **3–5x** — throughout 2023–2024. A 2025 peer-reviewed study of 4,820 undergraduate reports (17.2 million tokens, 2016–2025) found that **7 of 8 ChatGPT-marker words** (**"delve," "underscore," "intricate," "pivotal,"** and others) surged in 2023–24, then declined in 2025 as writers became aware of the pattern. Notably, **"delve" and "underscore" co-appeared in 96.5% of flagged Scopus articles in 2023–24**. While frequency dropped after widespread mockery, the crucial caveat is that **absence of these marker words no longer clears a text as human-written** — these words remain detectable signals when present, but their absence cannot be taken as proof of human authorship. Other high-confidence single-word tells include **"tapestry," "landscape," "multifaceted," "nuanced," "robust," "leverage," "utilize," "seamless," "foster," "pivotal," "paramount," "holistic," "innovative," "streamline,"** and **"transformative."** An Embryo.com analysis from March 2025 cross-referenced outputs from ChatGPT, Claude, Gemini, Qwen, and DeepSeek and catalogued over **250 overused words and phrases**, including corporate favorites like "synergy," "stakeholders," "paradigm shift," "scalable," and "state-of-the-art."

AI phrase tells are equally distinctive. The constructions **"It's important to note that," "In today's rapidly evolving landscape," "A testament to," "Navigate the complexities of," "Cannot be overstated,"** and **"Embark on a journey"** appear across AI outputs with mechanical regularity. The structural pattern **"It's not just X, it's Y"** — identified by Futurism, Slate, and Reddit communities as one of the most recognizable AI constructions — has become so pervasive that it's now entering human speech, a phenomenon documented in a 2025 Max Planck Institute study that found podcasters and YouTubers parroting AI-favorite words in unscripted conversation.

Different models produce different fingerprints, though the patterns keep shifting. ChatGPT favored "Certainly!" as an opener, heavy em-dash usage, and words like "intricate"; Claude tended toward longer hedged sentences and "I'd be happy to help"; Gemini produced shorter paragraphs and occasionally used emoji — markers that have partly faded as writers grew aware of them. Among current models, **Claude 4.5+** produces notably less formulaic prose and remains consistently the hardest to detect, per practitioner-grade testing across multiple independent assessments. **Gemini 3** exhibits a structured-output bias, favoring lists where flowing prose would naturally fit, alongside elevated use of booster words at roughly 6.1 per 1,000 words — also a practitioner-grade observation rather than a peer-reviewed figure. **DeepSeek R1** presents an idiosyncratic voice that diverges from the increasing convergence among OpenAI, Anthropic, and Google models, while **Llama 4** shows formal vocabulary paired with comparatively weak narrative cohesion. These model-specific signatures are more than anecdotal: a 2025 stylometric study achieved **97.56% accuracy** distinguishing GPT-4.1 from GPT-4o code purely from comment density and naming conventions, confirming that model fingerprints are real and measurable even as individual vocabulary tells rotate out of fashion with each update.

Beyond individual words, AI exhibits a systematic **Latinate bias**, preferring longer Latin-derived words over shorter Anglo-Saxon equivalents: "utilize" instead of "use," "facilitate" instead of "help," "commence" instead of "start," "demonstrate" instead of "show." This creates an overly formal register that clashes with natural communication. AI also avoids contractions — writing "it is" rather than "it's," "do not" rather than "don't" — which instantly elevates formality beyond what most human writers produce outside legal documents.

Transition words deserve special mention. AI leans heavily on **"Moreover," "Furthermore," "Additionally," "Nevertheless," "Consequently,"** and **"Accordingly"** — formal connectors that human writers typically replace with casual alternatives like "plus," "also," "but," "still," or no connector at all. The mechanical regularity of these transitions, deployed at predictable intervals, creates a cadence that trained readers recognize immediately.

---

## Statistical signatures: perplexity, burstiness, and the math of machine prose

Beneath vocabulary lies a deeper statistical layer that detection tools exploit. Two metrics dominate the field: **perplexity** and **burstiness**.

**Perplexity** measures how predictable text is — technically, how "surprised" a language model would be by each successive word. AI-generated text exhibits characteristically **low perplexity** because LLMs are trained to select high-probability tokens. A study comparing human-written and AI-generated medical abstracts found original abstracts had perplexity scores nearly **2x higher** than AI versions (mean 165.57 vs. 47.70 for unstructured abstracts). In stylometric comparisons, the autoregressive LLaMA model achieved perplexity of just **18.37** compared to **43.03** for human text. When you can guess the next word without effort, that's low perplexity — and that's AI.

**Burstiness** measures variation in sentence structure and length across a document, calculated as the ratio of standard deviation to mean sentence length. Human writing exhibits **high burstiness**: a five-word fragment followed by a 40-word sprawl, a technical paragraph followed by a one-line aside. AI maintains **low burstiness** — sentences averaging **15–20 words** with minimal variation, creating what researchers describe as a "steady, monotonous tempo." One academic study found human-written structured abstracts had a mean burstiness of **83.14** versus **64.31** for AI-generated versions.

**Entropy** — the mathematical measure of randomness in word sequences — tells a similar story. AI text has lower entropy because models generate probable sequences, while human writing introduces unpredictability through creative choices, idioms, and domain-specific language.

At the token level, AI text gravitates toward **high-probability token sequences** with uniform probability distributions. Human writing produces erratic probability jumps — moments where a writer chooses an unusual word, deploys sarcasm, or references something unexpected. This uniformity extends to n-gram frequency analysis: research shows GPT-4 "strikingly tends to abuse words like 'significant,' 'notable,' or 'despite,'" and its grammatical feature usage is strongly frequency-standardized compared to human text. Function words (prepositions, conjunctions) account for over 50% of words used but less than 0.04% of vocabulary, and AI systems favor certain verbs with remarkable consistency across topics: "including" (0.1203%), "leading" (0.0834%), "making" (0.0641%).

Newer models have narrowed some gaps. Diffusion-based models like LLaDA achieve perplexity nearly identical to human text (44.62 vs. 43.03) but still show lower burstiness (0.184 vs. 0.334). Claude reportedly produces text with naturally higher perplexity than OpenAI's GPT series. Grok shows higher burstiness due to training on real-time Twitter data. But no model yet fully replicates the statistical texture of human writing across all metrics simultaneously.

---

## Content tells: the emptiness beneath polished prose

Perhaps the most damning markers of AI writing exist at the content level — not how text sounds but what it actually says.

**Superficiality disguised as depth** is the defining content-level tell. AI presents mundane observations as profound insights using participial constructions: "...highlighting its lasting influence," "...underscoring the importance of," "...showcasing the potential for." A PNAS study found instruction-tuned models use these participial constructions at **2–5x the rate** of human text. The result is prose that attributes cosmic significance to ordinary facts while never providing the granular detail that actual expertise produces. A barista writing about coffee specifies water temperature and extraction time; AI gives generic overviews about "the art of crafting the perfect cup."

**Absence of authentic voice** is equally telling. AI generates text representing what University College Cork researchers (2025, published in Nature) described as a "statistical average of millions of voices" — no distinctive personality, no lived experience, no emotional texture. You won't find AI writing something like "Honestly, I screwed up my first three tries and almost rage-quit the whole thing." When AI attempts personal touches, it defaults to generic names — Pangram Labs found that **60–70% of names** in ChatGPT and Claude outputs are either "Emily" or "Sarah."

**Excessive even-handedness** reflects the RLHF training that optimizes for being "helpful and harmless." AI presents all sides of every issue even when inappropriate, creating what critics call **"emotionally beige"** prose — inoffensive but intellectually vacant. Asked a direct question, AI hedges: "There are various perspectives on this matter, and each has its merits." It summarizes rather than argues, describes rather than persuades, and circles the same idea without adding information — the "treadmill effect."

Other content tells include over-reliance on lists and bullet points (often with markdown formatting bleeding into what should be flowing prose), generic examples rather than specific ones ("Imagine a company that implements AI tools" rather than naming an actual company with actual results), and **ghost citations** — writing "studies show" or "research suggests" without naming specific papers, authors, or dates. AI also exhibits consistent **importance inflation**, using phrases like "marking a pivotal moment" or "a significant shift toward" to dress up routine observations, and defaults to **optimistic framing** regardless of subject matter, with challenges always ending in vague hope and conclusions wrapping up with motivational platitudes.

---

## How detection tools actually work — and where they fail

The detection tool landscape splits into three broad approaches: **statistical methods**, **deep learning classifiers**, and **watermarking systems**. Each has distinct strengths and serious limitations.

**GPTZero**, the most widely validated tool, uses a seven-component system combining perplexity and burstiness calculations, deep learning models trained on AI vs. human text, text search capabilities, and sentence-level detection with color-coded highlights. Its numbers are a case study in why source type matters: vendor self-reporting claims **99.39% accuracy with a 0.00% false positive rate**, and a transparent self-submission to the RAID benchmark (the largest standardized test, with 6+ million generations across 11 models) showed **95.7% detection at a 1% false positive rate**. Independent testing tells a less flattering story — roughly **87% accuracy with a ~10% false positive rate** — and accuracy drops further, to 80–85%, on heavily edited or paraphrased content, with performance degrading on text under 300 words. A GPTZero blog post claiming it beats Pangram "on the Chicago Booth benchmark" is GPTZero's own re-run of that benchmark, not the independent study itself. GPTZero was acquired by Superhuman/Grammarly in June 2026.

**Originality.ai** uses NLP-based algorithms with entropy analysis and deep learning models retrained frequently on outputs from major LLMs. The vendor's own meta-analysis of 13 studies claims **97–100% average accuracy**; independent testing by the University of Chicago Booth School found substantially lower real-world performance, **roughly 83–89% accuracy**. It claims strong performance (95–97%) on paraphrased content, though that figure has not been independently replicated.

**Turnitin's AI detection**, integrated into the plagiarism infrastructure used by thousands of universities, produces sentence-level and document-level predictions. It correctly identifies 77% of fully AI-generated texts and 93% of fully human texts (86% overall), but **deliberately misses approximately 15%** of AI text to keep its false positive rate low. Turnitin reports under 1% false positive rate at the document level; that figure and the "2–5% real-world" figure describe different units — document-level vs. sentence-level vs. field testing — rather than actually contradicting each other, so check which metric a given number describes before comparing tools. Accuracy on heavily edited AI text drops to just **20–63%**. Vanderbilt University disabled Turnitin's AI detector in August 2023, citing concerns about false positives and bias against non-native English speakers — the first in a wave of institutional pullback (see below). Turnitin expanded model coverage to GPT-5, Gemini 2.5, and Claude 4.5 output, and added Spanish-language detection, in February 2026.

**ZeroGPT** claims 98%+ accuracy but independent testing found **67–85% real-world accuracy with a 14.6–33% false positive rate** — rising to a **62.5% false positive rate on non-native English text specifically**. It remains free and popular but is the least reliable major tool.

**Pangram Labs**, by contrast, is the one tool that has held up under independent scrutiny. A University of Chicago Booth School / Becker Friedman Institute study (WP 2025-116) found roughly **100% detection with an essentially-zero false positive rate** — the paper reports an FPR policy cap of ≤0.005, not the "1-in-10,000" figure commonly repeated online, which appears nowhere in the underlying data — and an error rate roughly **38x lower** than competing tools. Pangram's own figures claim 99.98% accuracy, including 97% detection of QuillBot-paraphrased output (Pangram 3.0, December 2025), and the tool now offers a four-tier AI-assistance classification rather than a binary AI/human verdict.

Two newer entrants are worth tracking. **Winston AI** posted roughly a **4% false positive rate** in 2026 independent testing. **Sapling** claims 97%+ accuracy with under 3% false positives, but an independent 2026 benchmark of 2,400 samples measured just **76% accuracy** — its most attractive feature is a generous free API tier, not necessarily its accuracy.

**OpenAI's own text classifier**, launched January 2023, correctly identified only **26% of AI-written text** while incorrectly flagging 9% of human text. It was discontinued after six months. OpenAI acknowledged "it is impossible to reliably detect all AI-written text."

**Watermarking** represents the proactive alternative. Google DeepMind's **SynthID** modifies the token sampling process during generation, embedding an invisible statistical pattern. Published in Nature and tested on approximately 20 million Gemini responses, it showed no quality degradation. As of 2025, SynthID has watermarked over **10 billion pieces of content** and was open-sourced in October 2024. However, it remains vulnerable to paraphrasing attacks: re-translation drops detection to 67.5–76%, the SIRA attack (targeting high-entropy tokens) achieves nearly **100% evasion** at just $0.88 per million tokens, a 2026 **"layer inflation" attack** targets SynthID-Text's mean-score calculation specifically, and distillation techniques can strip watermarks from a model entirely.

OpenAI developed a watermark reportedly **99.9% effective** but shelved it, citing false-positive-at-scale concerns alongside internal surveys showing nearly 30% of ChatGPT users would reduce usage if it were implemented. Rather than shipping text watermarking, OpenAI has instead committed to the **C2PA (Coalition for Content Provenance and Authenticity)** content-provenance standard. Anthropic has not deployed a text watermark as of 2026. C2PA itself now counts over **6,000 members** (January 2026), with its v2.2 specification covering text embedded in PDFs; adopters include Cloudflare, Google Pixel 10, and Sony.

Regulation is emerging as the biggest forcing function in this space: the **EU AI Act's Article 50 becomes enforceable August 2, 2026**, requiring AI-generated text to be machine-readably marked, with an implementing Code of Practice finalizing in mid-2026 — a concrete, globally visible requirement with no direct parallel yet in North America or Asia.

In 2025, researchers at Rumi Technologies discovered GPT-o3 and o4 mini models embedding Narrow No-Break Space characters — OpenAI called these "a quirk of large-scale reinforcement learning," not intentional watermarks.

**Stylometric analysis** — measuring features like type-token ratio, hapax legomena, syntactic complexity, and function word distributions across 74+ features — achieved up to **0.98 accuracy** in binary classification between Wikipedia and GPT-4 text using LGBM classifiers. Intriguingly, paraphrased text was sometimes *more* detectable than the original, not less.

| Tool | Independent figures | Vendor claims | Notes |
|---|---|---|---|
| Pangram | ~100% detection, FPR "essentially 0" (≤0.005 policy cap); error rate ~38x lower than other tools | 99.98%, incl. 97% on QuillBot-paraphrased output (Pangram 3.0, Dec 2025) | Only tool meeting the study's policy constraint; four-tier AI-assistance classification |
| GPTZero | ~87% acc., ~10% FPR; 95.7% at 1% FPR on RAID (transparent self-submission) | 99.39% acc., 0.00% FPR | Acquired by Superhuman/Grammarly, June 2026 |
| Originality.ai | ~83–89% (Chicago Booth) | 97–100% (vendor meta-analysis) | |
| Turnitin | 77–98% pure AI; 20–63% on heavily edited AI | <1% doc-level FPR (see note above on units) | GPT-5/Gemini 2.5/Claude 4.5 coverage + Spanish detection added Feb 2026 |
| ZeroGPT | 67–85% real-world; 14.6–33% FPR (62.5% FPR on non-native English) | 98% | Weakest major tool |
| Winston AI | ~4% FPR (2026 testing) | — | New entrant |
| Sapling | 76% (independent, 2026) | 97%+, <3% FPR | Free tier is generous |
| OpenAI Classifier | 26% | N/A | Discontinued 2023 |

---

## Detecting locally: open-source and offline tools

Every tool discussed so far is commercial. A parallel open-source ecosystem exists for readers who want to run detection locally rather than trust a vendor's black box, organized by how much compute each approach demands.

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

None of these tools should be run in isolation. The verified consensus across this research is to combine perplexity, burstiness, a classifier score, and stylometric features into a single ensemble, and to treat the result as a probabilistic signal rather than a verdict — the same caution this guide applies to every commercial tool above.

---

## Free detection APIs for programmatic testing

Several services offer free API tiers for programmatic testing:

- **Sapling** — **50,000 chars/day** free via API key; best free tier of the majors.
- **GPTZero** — limited free API testing without an account (the "10,000 words/month" figure often cited is unverified).
- **Copyleaks** — **25,000 free chars/month**, with SDKs in **6 languages**.
- **Winston AI** — **2,000 free credits** (**1 credit/word**).
- **ZeroGPT** — free tier with character limits reported inconsistently (**2,000–15,000** range); the accuracy caveats discussed above still apply.
- **Hugging Face Inference API** — roughly **300 free requests/hour**, but only for obsolete GPT-2-era detector models; not useful for modern text.
- **Pangram — explicitly not free** (**4 web checks/day**; API **~$0.05 per 1,000 words**). Worth noting since it's the accuracy leader discussed above.

---

## Where to find the benchmarks

**RAID** is the standard benchmark for evaluating AI text detectors; its official home is **raid-bench.xyz** and the **liamdugan/raid** GitHub repository. Critically, **its-ai.org** presents itself as the "RAID Benchmark Official" page but is actually a competing vendor's marketing page — a distinction worth knowing before citing benchmark figures from it. For paraphrase-attack evaluation specifically, consult **PADBen**; for multilingual detector evaluation, consult **DetectRL-X**.

---

## Institutional pullback and the legal backlash

Mounting concerns over false positives and demographic bias have prompted a wave of institutional pullback that extends well beyond Vanderbilt's early 2023 decision to disable detection technology. **Australian Catholic University** abandoned its AI detector in 2024 after approximately **6,000 misconduct referrals** triggered by detection flags proved to be false positives, with roughly 90 percent of flagged cases exonerating the accused under human review. The University of Waterloo disabled its detector in September 2025 following internal testing that exposed a critical failure: text confirmed to be entirely human-written scored a **100 percent AI likelihood** in their system. Similar disablements followed at the University of Cape Town in October 2025 and Curtin University in January 2026, with the latter explicitly citing equity and bias concerns affecting non-native English speakers. Advocacy-adjacent reporting has circulated figures of "50+ universities" globally or "31 in the U.S." having disabled detection tools; these should be treated as indicative counts rather than independently verified tallies.

The legal system has begun imposing concrete consequences for institutional reliance on flawed detection verdicts. Five U.S. federal lawsuits have been filed since September 2024 challenging false-positive accusations issued through AI detectors: proceedings at Yale, the University of Minnesota (which seeks **$1.335 million** in damages), the University of Michigan, Hingham, and Adelphi, with the last of these cases dismissed. Among the identified plaintiffs, three are non-native English speakers, underscoring the demographic dimensions of detection failure documented above. Meanwhile, the publishing industry has adopted a cautious middle position: major academic publishers including Elsevier, Springer Nature, and Science now require authors to disclose AI tool use in their submissions but have explicitly declined to screen manuscripts with AI detectors as of 2026.

---

## What the research literature actually says

The academic consensus from 2023–2026 is sobering for anyone relying on detection tools for high-stakes decisions.

The landmark benchmark study by **Weber-Wulff et al. (2023)** in the International Journal for Educational Integrity tested 14 detection tools and concluded flatly: "The available detection tools for AI-generated text are neither accurate nor reliable." In one referenced test, overall detection accuracy reached only **27.9%** for AI-generated text. Conversely, **Desaire et al. (2023)** at the University of Kansas achieved over 99% accuracy distinguishing human from ChatGPT-written scientific abstracts — but using purpose-built custom models under controlled conditions, not commercial tools.

The most consequential finding concerns **bias against non-native English speakers**. The Stanford study by **Liang, Yuksekgonul, Mao, Wu, and Zou (2023)**, published in Patterns, evaluated seven detectors on TOEFL essays and found a **61.3% average false positive rate** for non-native English speakers (2023 study; detector landscape has since changed, but the bias mechanism — lower lexical diversity in NNES writing mimicking AI signatures — is unchanged and confirmed by 2025–26 studies). Nearly 20% of TOEFL essays were unanimously classified as AI-generated by all seven detectors, and 97.8% were flagged by at least one. The causal mechanism is clear: non-native speakers produce text with lower lexical diversity and syntactic complexity — the same features detectors associate with AI output. Subsequent research from 2025–26 documents this bias persisting across different metrics — not competing numbers, but different studies measuring different things: a PeerJ Computer Science study found roughly a **30% relative increase** in flag rates for non-native English essays (some secondary coverage misattributes this study to an institution that did not conduct it), a 2025 follow-up measured **32% misclassification** for NNES submissions, and testing of the ZeroGPT tool specifically found a **62.5% false positive rate** on non-native English text. The Markup documented real cases where international students at Johns Hopkins and NYU faced academic misconduct charges and threats to their visa status based on unreliable detector scores.

**Human detection ability is barely above chance.** A landmark PNAS study by **Jakesch, Hancock, and Naaman (2023)** across six experiments with 4,600 participants found people were unable to detect AI text beyond chance — **50–52% accuracy**, where random guessing achieves 50%. A German university study (2025) found lecturers achieved just 57% accuracy on AI texts. Orthopedic residents and professors in a medical study correctly identified only **31.7–34.9%** of AI-generated abstracts. Penn State's Dongwon Lee Lab confirmed humans distinguish AI text only about **53% of the time**. One exception: Russell et al. (2025) found that people who frequently use ChatGPT for writing are meaningfully better at detecting it, suggesting familiarity helps.

The theoretical picture is equally challenging. **Sadasivan et al. (2023)** at the University of Maryland, later published in Transactions on Machine Learning Research (2025), provided a formal proof connecting detection AUROC to the total variation distance between human and AI text distributions. As models improve, this distance decreases, making detection **fundamentally harder** — approaching theoretical impossibility for sufficiently advanced models.

Adversarial research confirms the vulnerability — though the picture has moved well past 2023-era baselines. **Krishna et al. (2023)** at UMass Amherst built DIPPER, an 11-billion-parameter paraphrasing model that dropped DetectGPT accuracy from **70.3% to 4.6%** without meaningfully altering content; by 2025–26 standards, DIPPER is now a weak baseline next to newer detector-guided attacks. **Cheng et al. (2025)**, presented at NeurIPS 2025, showed that training-free, detector-guided adversarial paraphrasing reduces detection by **64.49% (against RADAR) to 98.96% (against Fast-DetectGPT)**, averaging **87.88%** across detector types — the range matters more than the average, since resistance varies enormously by detector architecture. Critically, *simple* paraphrasing without detector guidance had the opposite effect, *increasing* detection by 8.6–15%; only paraphrasing deliberately guided by a detector's own scoring function reliably evades it. A 2025 benchmark called **PADBen** revealed a narrower and more precise asymmetry than headlines suggest: detectors remain good at catching plagiarism-evasion (AI text paraphrased to look human) but fail at authorship obfuscation (human text paraphrased to look AI-generated) — a real but specific weakness, not the wholesale collapse to near-random performance sometimes attributed to this line of research. Separately, a 2026 Carnegie Mellon study found that unmodified base language models are classified as human by GPTZero and Pangram, while their instruction-tuned counterparts are reliably caught — direct evidence that detectors track RLHF and instruction-tuning artifacts rather than machine generation itself, reinforcing this guide's central claim that most detectable "AI-ness" is really detectable "RLHF-ness." The arms race isn't purely one-sided, though: Pangram's DAMAGE detector reported 89% accuracy across 19 different humanizer tools in 2025 testing. A Frontiers in AI study by **Perkins et al. (2024)** tested GPT-5, Claude, and Gemini content across six detectors and found just **39.5% baseline accuracy**, dropping to **17.4%** against adversarial humanization. The comprehensive survey by **Wu et al. (2025)** in MIT Press's Computational Linguistics concluded: "The issue of AI-generated text detection remains an unresolved challenge. As LLMs become increasingly powerful, it is even less likely to detect AI text in the future."

NIST's GenAI Pilot Study (NIST AI 700-1, June 2025) offered a slightly more optimistic note, finding detection models "remain reasonably effective" and that discriminator systems improved over multiple testing rounds. But the overall research trajectory points toward a detection arms race that favors the generators.

Recent benchmark work continues this cautionary pattern. **DetectRL-X** (ACL 2026) tested over **3.46 million samples across 8 languages**, revealing that detector performance varies sharply by language — a reminder that universal accuracy claims obscure real regional gaps. A **Sultan Qaboos University study** (International Journal for Educational Integrity, February 2026) found leading detectors scoring only **69% and 61%** overall, with hybrid human-AI text detection dropping to near 0%; its precise figures are partially verified due to a paywall, but the study itself is real, and its conclusion — that no detector tested possessed sufficient reliability for academic misconduct determinations — echoes Weber-Wulff's earlier assessment. On the more promising side, **DivEye** (TMLR 2026, IBM) demonstrated that diversity- and surprisal-based detection can achieve a **33.2% improvement** over zero-shot baselines while remaining comparatively robust to paraphrasing.

The stakes behind these numbers are already visible in practice. NeurIPS's own 2026 disclosure found that **28.2% of position-paper-track submissions** scored **100% on Pangram**, with the share scoring **90% or higher** rising **10x year-over-year**. Separately, across the conference's **4,841 accepted papers**, reviewers found more than **100 hallucinated citations** spread across 51 papers — fabricated, plausible-sounding sources that a human author would be far less likely to invent. These are two distinct findings from two different parts of the same conference, not one statistic.

---

## Why AI writing fails: the structural weaknesses

Beyond vocabulary and statistics, AI writing betrays itself through deeper structural and tonal patterns that accumulate across paragraphs.

Rhetorical patterns get cited constantly as top-tier structural tells: **negative parallelism** ("It's not just X, it's Y" — also flagged in the vocabulary section above), the **rule of three**, unwarranted **significance inflation** ("marking a pivotal moment"), and **vague attribution** ("studies show"). An honest caveat is due here: the academic literature specifically validating these named rhetorical patterns is thinner than their internet-famous status implies — the most detailed catalog of them is a Wikipedia editors' advice essay written to help volunteer editors spot machine-written submissions, not a peer-reviewed study, and widely repeated claims of "~95% accuracy when these patterns are clustered together" are unvalidated blog assertions, not measured results. What *is* peer-reviewed and confirmed: AI text shows measurably lower **interactional metadiscourse** — rhetorical questions appear at roughly 2.60 per 1,000 words in human writing versus near-zero in AI text — along with higher grade-level scores and lower readability, a higher dependent-clause ratio (0.75 in AI text vs. 0.57 in human text), and a template-like pattern of lexical substitution: higher vocabulary diversity *across* different AI documents but lower diversity *within* any single one — the opposite of how a human writer's vocabulary typically behaves. These primary signals should carry more weight than any individual rhetorical-pattern checklist.

**Repetitive sentence openers** are pervasive. AI frequently begins consecutive sentences with "The," "This," or the subject being discussed, creating a drone-like rhythm that human writers instinctively break. The related phenomenon of **synonym cycling** — where repetition-penalty algorithms force AI to use different words for the same concept ("protagonist," "key player," "eponymous character") — itself becomes a tell, since human writers naturally repeat terms when consistency aids clarity.

**The absence of humor, sarcasm, and irony** is near-universal. AI text is earnest and sincere by default, lacking the unexpected jokes, irreverent asides, self-deprecation, and understatement that characterize human communication. As one Reddit user observed: "GPT is always going to sound polished. It's a machine that rewards coherence, which is why incoherence has never been more precious." Human writing has "rough edges, voice cracks, unexpected pauses, half-formed metaphors that never quite land."

**Formulaic structure** at the paragraph and document level creates a sense of mechanical inevitability. Every AI paragraph follows the same recipe: claim, elaboration, example, transition, repeat. Individual paragraphs are competent; the problem is accumulation. Human writing varies because humans explore, digress, double back, zoom in unexpectedly. AI is "linear, mechanical, goal-oriented — start to finish, no side quests allowed."

**The em dash problem** deserves its own mention. Dubbed the "ChatGPT dash," AI uses em dashes as a universal connector where commas, colons, semicolons, or parentheses would be more appropriate. Since keyboards lack a dedicated em dash key, most humans use hyphens or avoid them entirely. AI always produces properly formatted em dashes (—), and uses them far more frequently than human writers — a pattern traceable to **markdown-saturated training data**. Corpus analysis measured em dashes appearing roughly every 50–80 words in AI-generated text versus roughly every 500 words in human writing, a 10–50x difference; the disparity sharpens in scientific abstracts, where em-dash usage more than doubled between 2021 and 2025. Combined with AI's consistent use of Oxford commas, curly quotation marks, and perfect spelling, this frequency becomes part of a distinctive fingerprint of machine generation.

That signal is weakening, though. GPT-5-era models show markedly lower em-dash usage than their predecessors, human em-dash adoption is itself rising as AI-generated text normalizes the style, and em-dash frequency alone is a comparatively weak signal — it carries real diagnostic weight only in aggregate with other tells, never as a standalone giveaway.

**Low lexical diversity** is documented across virtually every study. Research by André, Culda, Guo, Liao, Liu, Muñoz-Ortiz, Seals, and others between 2023 and 2025 unanimously reports AI text uses significantly fewer unique words than human writing. The content-to-function word ratio differs too: humans maintain a balanced ratio around **0.98**, while AI shows a higher proportion of content words at approximately **1.37**.

---

## Practical instructions for producing genuinely human text

The following techniques, synthesized from AI research, writing communities, detection tool documentation, and adversarial studies, form an actionable system for producing text that reads as authentically human.

### Eliminate the vocabulary fingerprint

Maintain and enforce a banned-word list. At minimum, exclude: delve, tapestry, landscape, multifaceted, nuanced, robust, leverage, utilize, seamless, foster, pivotal, paramount, holistic, innovative, streamline, transformative, vibrant, meticulous, intricate, compelling, embark, navigate, beacon, testament, plethora, myriad, moreover, furthermore, additionally, nevertheless, consequently, accordingly. Replace Latinate words with Anglo-Saxon equivalents: "use" not "utilize," "help" not "facilitate," "start" not "commence," "show" not "demonstrate," "improve" not "enhance." Replace formal connectors with natural ones: "but," "and," "also," "plus," "still," "so" — or drop connectors entirely and let logical flow do the work. A useful technique: before writing on a topic, list the 20 words an AI would most likely use, then ban all of them.

### Engineer burstiness into every paragraph

Never allow three consecutive sentences of similar length. Mix aggressively: a three-word sentence, then a sprawling 35-word thought, then a medium one, then a fragment. Use sentence fragments for emphasis ("Exactly." "Not even close." "The point being."). Allow occasional run-ons that mimic how people actually think when excited. Read every paragraph aloud — if it sounds monotone, restructure until the rhythm varies.

### Use contractions and break grammar rules deliberately

Write "don't" not "do not," "can't" not "cannot," "it's" not "it is" — except when the formal version creates emphasis. Start sentences with "And," "But," "So," "Because." End sentences with prepositions. Split infinitives. Use comma splices occasionally for rhythm. Drop subjects in casual contexts ("Went to the store. Grabbed milk."). Perfect grammar is an AI tell; strategic imperfection is a human signature.

### Build a specific, consistent voice

The most effective anti-detection technique across all sources is writing from a **specific persona with lived experience**. Define: years of experience, communication style (blunt, warm, irreverent), relationship to reader (mentor, peer, skeptic), specific expertise domain, and emotional range. Take strong positions: "I think this approach is mostly wrong, and here's why" instead of "There are various perspectives on this matter." Show real frustration, genuine enthusiasm, self-doubt, and humor. Reference specific personal experiences with dates, places, and concrete details that only a real person would know.

### Add radical specificity

Replace every generic claim with a concrete one. Not "a local farm" but "Henderson's place off Route 9." Not "improved efficiency" but "cut processing time from 14 minutes to 90 seconds." Not "studies show" but "Liang et al. at Stanford found in their July 2023 Patterns paper." Use domain-specific jargon naturally, without defining terms insiders already know. Reference specific tools, version numbers, prices, dates, and people. Specificity is the single hardest thing for AI to fake and the single most effective differentiator.

### Destroy formulaic structure

Never open with "In this article, we will explore." Start with a hook — an anecdote, a provocative claim, a question, or straight into the argument with no preamble. Vary paragraph length wildly: one sentence, then five, then two, then a single line for emphasis. Digress intentionally, then circle back ("But I'm getting ahead of myself"). Don't resolve every thread neatly. Avoid "In conclusion" — just end when you're done, or end with a new thought that the conclusion prompted. Eliminate markdown formatting (bold, headers, bullet points) in contexts where flowing prose is expected.

### Address the em dash problem

Replace every em dash with a comma, period, semicolon, or sentence restructure. This single change eliminates one of the most discussed formatting tells. Similarly, avoid curly quotation marks in contexts where straight quotes are standard, and allow occasional minor imperfections rather than perfect typography throughout.

### Prompting and post-processing

When using AI as a writing tool, provide detailed persona definitions, explicit banned-word lists, and style instructions that demand burstiness, contractions, active voice, and specificity. Set temperature to maximum for vocabulary variety. After generation, edit line by line: read aloud, replace anything that sounds like a press release, insert personal touches, add concrete details, and break any remaining patterns. The most reliable approach is the **two-pass method**: generate with constraints, then manually rewrite every sentence you wouldn't actually say yourself.

---

## Conclusion: an arms race the detectors are losing

The research paints a clear picture: AI text detection works reasonably well against raw, unedited output from known models, but accuracy collapses against paraphrased, edited, or adversarially crafted text — Perkins et al. (2024) measured a drop from 39.5% baseline accuracy to as low as **17.4%** against adversarial humanization, and detector-guided paraphrasing attacks reduce detection by 64.49–98.96% depending on architecture. The theoretical ceiling for detection falls as models improve, and the commercial ecosystem of "humanizer" tools continues to erode whatever advantage detectors temporarily gain. False positive rates disproportionately harm non-native English speakers (61.3% in the 2023 Stanford study; the mechanism is confirmed by 2025–26 follow-ups even as the exact figure ages), and human judges perform barely above coin-flip accuracy.

The most durable insight from this research isn't about tricking detectors — it's that genuinely good writing naturally possesses the properties that evade detection. High perplexity comes from unexpected word choices and authentic expertise. High burstiness comes from a writer who thinks in varied rhythms. Specific details come from lived experience. Strong positions come from actual convictions. The gap between AI and human writing is narrowing, but it hasn't closed — and the residual gap lives not in vocabulary or grammar but in the texture of genuine thought, the willingness to be wrong, and the irreducible specificity of having actually been somewhere, done something, and formed an opinion about it.