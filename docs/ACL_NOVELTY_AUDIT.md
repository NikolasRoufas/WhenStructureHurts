# ACL novelty audit (revision-2, 2026-10-13)

**Basis.**
- Nishida et al. (2026) was re-checked on 2026-10-13 at its official page (https://aclanthology.org/2026.tacl-1.29/, metadata) and in the full text (§4.3–5.8).
- The other entries were verified in revision-1 on their publisher, Anthology, arXiv or proceedings pages (`docs/NOVELTY_AND_RELATED_WORK_AUDIT.md`). For those we read only the abstract or landing page unless marked "full text".
- Each cell records what a paper *does*. It is not a judgement of quality. "—" means we found no such element. For abstract-only entries that is not proof of absence.

## 1. Closest work, verified in detail

**Nishida, Munne, Liu, Tokunaga, Yamagata, Cheng, Kozaki, Matsumoto (2026). *Dissecting GraphRAG: A Modular Analysis of Knowledge Structuring for Factoid Question Answering.* TACL 14:627–655, doi 10.1162/tacl.a.615.**

- **Question:** which GraphRAG module choices matter: triple extraction (Manual / SLM-SFT / LLM-ICL), community clustering (Hierarchical Leiden / Neighbourhood Aggregation / Triple-Level Factorization) and report generation (LLM-based / template-based).
- **Data:** two templated factoid benchmarks, CDR-QA and DocRED-QA.
- **Retrieval:** Contriever, top-10 chunks of up to 100 tokens.
- **Answer generation:** GPT-4o "in all cases" (§4.3, §5.1).
- **§5.8 "Sensitivity to backbone LLMs":** replaces the LLM used for *triple extraction and report generation* with GPT-4o-mini, Qwen-2.5-7B-Instruct, Llama-3.1-8B and Llama-3.1-70B. The answer generator is not varied.
- **Findings:**
  - extraction quality strongly affects downstream QA;
  - "noisy or hallucinated relations (common in LLM-ICL) can undermine both answer and evidence recall";
  - neighbourhood-sized communities work best;
  - template reports beat LLM summaries;
  - one-module-at-a-time ablations (Table 6);
  - retrieval depth k is varied (Fig. 4).
- **Extraction quality** is measured against gold annotations (NER, ED and DocRE P/R/F1, Table 3), not by human judgement of predicted relations.
- **Results** are point estimates. We found no significance tests or confidence intervals in §5.

## 2. Novelty matrix

| paper | scientific question | evidence type | facts reaching the reader controlled? | graph / relation extraction | relation-quality evaluation | order-only control | token-budget accounting | error propagation measured | statistics | human verification | generators (answering) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **This work** | does the *presentation* of fixed evidence (segmentation, order, relation lines, relation provenance and labels) change answers, and through which channel | gold supporting passages (4,976 + 6,400 fresh questions); retrieved top-4 passages (1,000) | **yes**: identical fact set verified per question (Protocol A); fixed ranking + budget (Protocol B) | derived from dataset annotations by rule; predicted by an NLI cross-encoder + title heuristic | presentation-level interventions: contradiction lines on/off, typed vs neutral labels, targeted relabelling, length-matched filler, all at a fixed order; automatic triage; blinded two-annotator package prepared, **not completed** | **yes** (R5−R1, R5P−R5, R4P−R4P_FO) | **yes**: content vs overhead tokens per format; facts and answer-bearing facts dropped under a budget (pilot) | yes, from relation predictor to abstention (C/W/A transitions) | pre-specified paired tests, Holm, equivalence (TOST); a second frozen confirmatory protocol on untouched questions; paired bootstrap CIs everywhere | none completed | Qwen2.5-7B-Instruct; Mistral-7B-Instruct-v0.3 (same questions) |
| Nishida et al. 2026, TACL (full text) | which GraphRAG module choices matter | KG built from a fixed corpus; retrieved reports/chunks | no: structure changes what is retrieved | manual / SLM-SFT / LLM-ICL triples | vs gold annotations (P/R/F1); downstream recall | — | retrieval depth k varied; processing time; chunk size fixed | yes (extraction → retrieval → answer) | point estimates | — | GPT-4o (extraction/report LLMs varied) |
| Xiang et al. 2026, ICLR, GraphRAG-Bench (abstract) | when graphs help across task types | full pipelines | no | per system | — | — | — | system level | — | — | (several systems) |
| Han et al. 2025, arXiv (abstract) | RAG vs GraphRAG strengths | full pipelines | no | per system | — | — | efficiency discussed | system level | — | — | (several) |
| Zhou et al. 2025, PVLDB (abstract) | graph-RAG methods in one framework | full pipelines | no | per method | — | — | cost reported | method level | — | — | (several) |
| Zhuang et al. 2026, LinearRAG, ICLR (abstract) | relation-free graph RAG | own pipeline | no | none (argues extraction is unreliable) | — | — | efficiency | — | — | — | — |
| Dai et al. 2024, arXiv (abstract) | KG facts as triples vs text | KG subgraphs | **yes** (same facts, different format) | given KG | noisy subgraphs | partly (triple organisation) | — | — | — | — | several LLMs |
| Chen et al. 2024, Dense X, EMNLP | retrieval granularity | propositions / sentences / passages | no (retrieval changes) | LLM propositionizer | — | — | fixed token budget for QA | — | — | — | several readers |
| Chen et al. 2026, PathRAG, AAAI | prune and serialise relational paths | own pipeline | no | LLM KG | — | — | redundancy pruning | — | — | — | — |
| Gutiérrez et al. 2024/2025, HippoRAG 1/2 | KG + PPR retrieval | own pipeline | no | OpenIE | — | — | — | — | — | — | — |
| Guo et al. 2024, LightRAG | graph index + dual retrieval | own pipeline | no | LLM | — | — | — | — | — | — | — |
| Zhu et al. 2025, KG²RAG, NAACL | KG-guided chunk expansion and organisation | own pipeline | no | KG | — | partly (organisation module) | — | — | — | — | — |
| Liu et al. 2024, Lost in the Middle, TACL | position effects | same documents moved | yes | — | — | **yes** (position) | — | — | — | — | several |
| Jiang et al. 2024, LongLLMLingua, ACL | prompt compression | retrieved documents | no (compression removes text) | — | — | reordering | **yes** (compression ratio) | — | — | — | several |
| Jeong et al. 2025, ECoRAG, Findings ACL | evidentiality-guided compression | retrieved documents | no | — | — | — | yes | — | — | — | — |

## 3. What this work establishes that these papers do not

We do **not** claim to be the first to study when GraphRAG helps or hurts, the first to show that noisy relations hurt (Nishida et al. 2026 show it through retrieval), or that structure hurts in general.

What we establish:

1. **The effect of a relation *as displayed*, with the content fixed.** In Nishida et al. and the system-level studies, an extraction error changes what is retrieved. In our interventions, the reader sees the same verified sentences in the same order, and only the relation lines change.
2. **Where the harm sits.** Among the relation components we vary — order, line count, neutral lines, typed labels, contradiction lines — only the asserted contradiction carries a sizeable cost. A targeted relabel and a length-matched filler separate the label's meaning from its tokens.
3. **The channel.** The cost runs through abstention under an instruction that permits it, shown by transitions and by a prompt-factor experiment. None of the closest papers separates abstention from wrong answers.
4. **Evidentiary standard.** Pre-specified, multiplicity-corrected paired tests, equivalence testing, and a second frozen confirmatory test on untouched questions. To our knowledge, the closest GraphRAG analyses report point estimates.
5. **Accounting.** Content and overhead tokens per format, and facts lost under a budget.

**Not established:**
- that the predicted contradictions are *false* (human labels pending);
- anything about GraphRAG indexing or retrieval quality;
- generality beyond two 7B readers;
- the effect of correct structure on incomplete evidence.

## 4. Framing decision

The task brief proposed the framing *"Evidence structure should be evaluated not only by the relationships it adds, but also by how its annotations change answer behaviour, evidence retention and abstention under controlled factual content."* We adopt it only to the extent the results support it:

- **Answer behaviour and abstention:** supported, for asserted contradictions; to be confirmed by `CONFIRMATORY_PROTOCOL_2`.
- **Evidence retention:** supported only at pilot scale and on one retrieved-evidence sample.
- **Derived relations:** we report a null and an equivalence result, not a benefit.

The final wording in the paper follows the confirmatory and second-reader results (see `docs/FINAL_RESEARCH_ASSESSMENT.md`).
