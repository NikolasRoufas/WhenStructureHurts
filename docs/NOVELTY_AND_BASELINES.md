# Related work, baselines, and positioning

Status: **novelty NOT established.** The positioning below is a working hypothesis based on a
limited search (2026-10-10). A systematic literature review (ACL Anthology, arXiv 2024-2026,
Semantic Scholar citations of the works below) is required before any novelty claim is written.

## 1. Neighbouring research lines

| Line | Representative work (verified to exist) | Relation to this project |
|---|---|---|
| Standard RAG | Lewis et al. 2020 (NeurIPS) | B0/B1 baselines |
| Context robustness / distractors | Cuconasu et al. 2024 (SIGIR) "The Power of Noise"; Liu et al. 2024 (TACL) "Lost in the Middle"; Shi et al. 2023 (ICML) irrelevant context* | P3 (ordering) and P4 (distractors) re-use their manipulations; we apply them to *structured* representations |
| Retrieval granularity / propositions | Chen et al. 2024 (EMNLP) "Dense X Retrieval" ([ACL Anthology](https://aclanthology.org/2024.emnlp-main.845)) | Closest prior work for R0 vs R1: they find propositions help *retrieval and QA under a budget*. We hold retrieval fixed (gold evidence) and vary only the *presentation*; our budget-matched mode is the comparable setting |
| Claim decomposition quality | FActScore (Min et al. 2023); Wanner et al. 2024 "A Closer Look at Claim Decomposition" (*SEM)* | Motivates P6 / C1 (extraction errors) |
| GraphRAG / KG-RAG | Edge et al. 2024 (GraphRAG); HippoRAG (Gutiérrez et al. 2024)*; LightRAG (Guo et al. 2024)*; Think-on-Graph 2.0 (Ma et al. 2025) | Graph construction for *retrieval*; EG-RAG (B4) instead uses the graph as a pre-generation evidence layer |
| Systematic RAG vs GraphRAG | Han et al. 2025, "RAG vs. GraphRAG: A Systematic Evaluation and Key Insights" ([arXiv 2502.11371](https://arxiv.org/abs/2502.11371)); "When to use Graphs in RAG" (GraphRAG-Bench, 2025) | **Close neighbour.** They compare whole systems and find complementary strengths and gains from selection/integration. We differ (to be verified) by holding the underlying evidence fixed and isolating representation, perturbation and component effects with oracle substitution |
| Information loss in KG construction | TCR-QF, "How to Mitigate Information Loss in Knowledge Graphs for GraphRAG" (IJCAI 2025, [pdf](https://www.ijcai.org/proceedings/2025/0901.pdf)); MemGraphRAG (arXiv 2606.00610); SocraticKG (arXiv 2601.10003) | **Close neighbour for H2.** TCR-QF names "context loss" and "information sparsity" and proposes mitigation. Our Exp3 attempts *causal attribution* by replacing one component at a time with verified annotations; this specific design was not found in the search, which is not proof of absence |
| Atomic / proposition graphs | AtomicRAG (arXiv 2604.20844); GRASP (arXiv 2605.16598) | 2026 systems combining atomic claims with graphs; must be read in full and possibly added as baselines |
| Adaptive structure / strategy selection | **StructRAG** (Li et al., ICLR 2025, [proceedings](https://proceedings.iclr.cc/paper_files/paper/2025/hash/5975754c7650dfee0682e06e1fec0522-Abstract-Conference.html)): DPO-trained router choosing table/graph/catalogue/algorithm/chunk; Adaptive-RAG (Jeong et al., NAACL 2024)* | **Direct prior art for H4/Experiment 4.** An adaptive representation selector is *not* novel by itself. Any contribution must come from (a) evidence-preservation-aware selection features, (b) controlled evaluation with identical evidence, or (c) diagnostic findings from Exp1-3 |
| Evidence verification / NLI | FEVER (Thorne et al. 2018); HoVer (Jiang et al. 2020); MNLI; ANLI | Relation classifier and groundedness checker |
| Prompt-format sensitivity | Sclar et al. 2024 (ICLR)*; Fatemi et al. 2024 "Talk like a Graph" (ICLR)* | Confound for H1: format effects must be separated from structure effects (R5 controls, identical instructions, token matching) |

\* cited from memory; not re-verified in this session. Verify before citing.

## 2. Working contribution statement (provisional, falsifiable)

1. A controlled protocol in which the **same evidence** is presented as passages, claims, paths and graphs (information-equivalent and token-matched), with structure taken from dataset annotations rather than model predictions.
2. A **perturbation suite** (P1-P7) with recorded per-item changes and label-effect accounting, measuring sensitivity per representation.
3. A **component-substitution analysis** (Exp3) that attributes degradation to extraction, relations or selection, separating evidence loss from generation failure.
4. Only if 1-3 show a reproducible effect: an evidence-preserving adaptive selector, positioned against StructRAG and Han et al.'s selection strategies.

Each item could fail. Null results for 1-3 are reportable findings.

## 3. Baselines in this repository

| ID | System | Status |
|---|---|---|
| B0 | BM25 top-k raw passages | implemented, smoke-tested |
| B1 | BM25 -> cross-encoder rerank -> top-k passages | implemented, smoke-tested |
| B2 | B1 passages -> LLM atomic claims (flat) | implemented, smoke-tested |
| B3 | B2 claims -> heuristic dependency path | implemented, smoke-tested; **new** (not in the original paper) |
| B4 | Reconstructed EG-RAG | implemented, smoke-tested; **reconstruction, not the original code** |

Baselines still missing for a publishable comparison: proposition retrieval (Dense X), one GraphRAG-family system (e.g. HippoRAG 2 or LightRAG), StructRAG (for Exp4), and a summarization/compression baseline (e.g. RECOMP).

## 4. Reconstruction ledger for B4 (EG-RAG)

| Component | Source | Our choice |
|---|---|---|
| Stage order (Algorithm 1) | paper | as specified |
| Hybrid retrieval, Eq. 2 | paper (form) | BM25 + bge-small-en-v1.5, min-max normalised, lambda = 0.5/0.5 (**approximation**) |
| Reranker | paper: "optional reranking model" | ms-marco-MiniLM-L6-v2 (**approximation**) |
| Claim extractor | paper: "generative model / IE / deterministic" | same generator, per-sentence prompt (`extract-v2`), lexical-support check (**approximation**) |
| Claim fields (negation, entities, confidence, ...) | paper | negation regex, capitalised-span entities (**heuristic**) |
| Relation set R | paper | all five types |
| Relation classifier | paper: NLI over pruned pairs | nli-deberta-v3-xsmall; pruning = shared entity or Jaccard >= 0.15; thresholds 0.7 entail / 0.9 contradict + shared non-title entity (**approximation; contradiction rule changed after smoke inspection**) |
| DEPENDS_ON prediction | paper: relation type, method unspecified | title-mention bridge heuristic (**ours**) |
| SUPERSEDES rule | paper: conditions i-iv | years as the only temporal signal (**approximation**) |
| Eq. 5 features and theta | paper gives form only | see `egrag/belief_propagation.py` docstring (**ours**) |
| Eq. 6 features and eta | form only | dense cosine, DEPENDS_ON participation, query-token coverage (**ours**) |
| Eq. 7 propagation | paper | implemented; temporal-term sign is **our interpretation**; DUPLICATE neighbours send no message |
| Eq. 8 stopping | paper | eps = 1e-4, max_iter = 50 (**ours**) |
| Conflict resolution | paper (labels, margin) | margin 0.1 (**ours**) |
| Eqs. 9-10 selection | paper (objective terms) | greedy connected expansion with documented fallback; omega values **ours** |
| Serialization | paper (contents) | `representations/serialization.py`; per-prompt E-ids instead of hash ids (**fix for the paper's citation-copying failures**) |
| Prompt, decoding, budgets | not reported | `models/prompts.py` (qa-v2), greedy, max_new_tokens 48 in smoke (**ours**) |

The original paper's results (Tables 1-5) are **not** reproduced and must not be cited as measured by this codebase.
