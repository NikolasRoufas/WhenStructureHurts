# Novelty and related-work audit (revision-1, 2026-10-12)

**Basis.** Each entry was checked on its publisher, Anthology, arXiv or proceedings page. "(full text)" marks papers whose method sections we read; "(abstract)" marks statements based on the abstract or landing page only. We record what each paper *does*, not what it could be read to imply.

**Correction to the draft.** The draft claimed that "Dissecting GraphRAG" could not be found. That was a search failure on our side. The paper exists and is the closest work to ours.

## Closest work

### Nishida et al. (2026), *Dissecting GraphRAG: A Modular Analysis of Knowledge Structuring for Factoid Question Answering*, TACL 14:627–655, doi 10.1162/tacl.a.615 (full text, §1–5.3)

- **Question:** which GraphRAG modules matter (triple extraction, community clustering, report generation) for factoid QA.
- **Benchmarks:** two new templated datasets, CDR-QA (biomedical) and DocRED-QA (encyclopedic). Each has 128 questions per type (neighbourhood, intersection, multi-hop), and every question has a set of answers.
- **Reader:** GPT-4o. Retrieval uses Contriever, top-10 chunks of up to 100 tokens. The metric is answer recall plus evidence recall@10.
- **Source facts controlled?** Partly. The source corpus is fixed, and gold triples give an "ideal extraction" condition. But extraction, clustering and verbalisation change *what is retrieved*, so content reaching the reader changes together with structure.
- **Extraction evaluated?** Yes: NER, ED and DocRE precision/recall/F1 against gold annotations. Noisy LLM-ICL triples (low DocRE precision) lower answer and evidence recall.
- **Ordering isolated?** No. **Serialisation overhead?** Not as a budget accounting, though report granularity and chunking are studied. **Error propagation?** Yes, via extraction quality, at system level.
- **Statistics:** point estimates; we found no significance tests or confidence intervals in §5.
- **Overlap with us:** both find that noisy relations hurt and that structure alone does not guarantee gains.
- **Difference:** we hold the evidence the reader sees fixed (Protocol A verifies identical facts per question). We vary only presentation (sentence items, order, relation lines, predicted vs derived relations) with retrieval and content fixed, isolate the effect of contradiction lines and of order through fixed-order interventions, account for serialisation overhead under a budget, separate abstention from wrong answers, and use pre-specified paired tests on a disjoint 4,976-question sample with an open 7B reader. They study a full GraphRAG pipeline with community reports. We study evidence presentation of gold or retrieved passages, not GraphRAG indexing.

### Xiang et al. (2026), *When to use Graphs in RAG*, ICLR (abstract and landing page)

- Introduces GraphRAG-Bench (fact retrieval to complex reasoning, summarisation, creative generation). It evaluates the whole pipeline (construction → retrieval → generation) and identifies when graphs help.
- Content is not controlled (system-level comparison).
- **Difference:** we isolate presentation with the facts fixed.

### Han et al. (2025), *RAG vs. GraphRAG: A Systematic Evaluation and Key Insights*, arXiv 2502.11371 (abstract)

- Compares RAG and GraphRAG on QA and query-based summarisation under a unified protocol. It finds task-dependent strengths and that combining them helps, and it discusses failure modes and efficiency.
- **Difference:** system-level; it does not hold facts fixed or isolate relation lines or order.

### Zhou et al. (2025), *In-depth Analysis of Graph-based RAG in a Unified Framework*, PVLDB 18 (abstract)

- Places graph-RAG methods in one framework and benchmarks them under the same settings; it also builds new variants.
- **Difference:** method-level comparison, not presentation of fixed evidence.

### Dai et al. (2024/2025), *Large Language Models Can Better Understand Knowledge Graphs Than We Thought*, arXiv 2402.11541 (abstract)

- The same KG facts are given as linearized triples or as fluent text. It reports that triples are more effective for fact-intensive QA, that triple organisation preferences vary by model, and that larger models are more sensitive to noisy subgraphs.
- **Overlap:** a controlled-content format comparison, the closest in spirit to our Protocol A. **Difference:** our units are dataset sentences (not triples). We isolate ordering and explicit relations (derived vs predicted) at a fixed order, use multi-hop RC benchmarks with paired confirmatory tests, and examine abstention.

## Other cited work (verified metadata; role in the paper)

| paper | question | facts controlled? | extraction evaluated? | order isolated? | overhead isolated? | error propagation? | relation to us |
|---|---|---|---|---|---|---|---|
| Edge et al. 2024 (GraphRAG), arXiv | query-focused summarisation with entity graphs and community summaries | no | no | no | no | no | a system our study does not run; motivates structure |
| Sarthi et al. 2024 (RAPTOR), ICLR | tree of recursive summaries | no | n/a | no | no | no | hierarchical structure |
| Gutiérrez et al. 2024, 2025 (HippoRAG 1/2), NeurIPS / ICML | KG + PPR memory for multi-hop retrieval | no | no | no | no | no | structure for retrieval, not presentation |
| Zhu et al. 2025 (KG²RAG), NAACL | fact-level KG links between chunks, expansion and organisation | no | no | partly (organisation is a module) | no | no | organises chunks; we isolate order on fixed facts |
| Guo et al. 2024 (LightRAG), arXiv | graph index + dual-level retrieval | no | no | no | no | no | system |
| Chen et al. 2026 (PathRAG), AAAI | relational paths, flow-based pruning, path prompting | no | no | no | partly (redundancy) | no | path serialisation as a system component |
| Zhuang et al. 2026 (LinearRAG), ICLR | relation-free graph, arguing relation extraction is unreliable | no | no (argued) | no | no | no | our predicted-relation results support its premise in a controlled setting |
| Chen et al. 2024 (Dense X), EMNLP | proposition-level retrieval units | no | yes (propositionizer) | no | no | no | finer units help retrieval; our R1 uses sentences, not propositions |
| Liu et al. 2024 (Lost in the Middle), TACL | position effects in long contexts | yes (same documents, moved) | n/a | yes (position) | no | no | order sensitivity; our R2 and R5 orders are a related manipulation |
| Jiang et al. 2024 (LongLLMLingua), ACL | prompt compression | no | n/a | partly (reordering) | yes (compression) | no | budget/compression; our Protocol B accounts for formatting overhead |
| Jeong et al. 2025 (ECoRAG), Findings ACL | evidentiality-guided compression | no | n/a | no | yes | no | budget |
| Gao et al. 2023 (ALCE), EMNLP | citation evaluation | n/a | n/a | n/a | n/a | n/a | citations (we do not analyse them) |
| Cuconasu et al. 2024, SIGIR | noise in retrieved context | partly | n/a | yes (position of noise) | no | no | distractor effects; our P4 |

## Our defensible contribution

We claim none of the following:
- that GraphRAG or structure hurts in general;
- that we are first to study when graphs help;
- that we are first to show that noisy relations hurt (Nishida et al. 2026 show it at system level).

What remains, as far as our review found, is a **controlled-presentation** study in which:
1. the facts shown are verified identical across representations;
2. order, relation lines, relation provenance (derived vs predicted) and relation semantics (typed vs neutral label at equal line count) are varied one at a time;
3. serialisation overhead is accounted for under a fixed fact ranking and budget;
4. abstention is separated from wrong answers through paired transitions;
5. the primary contrasts are tested on a disjoint sample with pre-specified, multiplicity-corrected paired statistics.

The empirical novelty is modest. The methodological contribution (controls and accounting) and the mechanistic finding about misleading relation lines (to be judged on the fixed-order controls) are the parts most likely to interest reviewers. A single reader and gold evidence limit significance.
