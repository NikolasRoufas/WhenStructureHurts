# EG-RAG reconstruction (baseline B4)

Experiment 0 includes a reconstruction of the EG-RAG evidence-graph pipeline, implemented in `src/wsh/egrag/`.
It follows the stage order of the original algorithm. Every component that the original description leaves
unspecified is our own choice, listed below. It is **not** the original implementation, and its results say
nothing about the original paper.

## Baselines in this repository

| ID | System |
|---|---|
| B0 | BM25 top-k raw passages |
| B1 | BM25 → cross-encoder rerank → top-k passages |
| B2 | B1 passages → LLM atomic claims (flat) |
| B3 | B2 claims → heuristic dependency path |
| B4 | reconstructed EG-RAG |

## Reconstruction ledger

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

