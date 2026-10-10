# exp0 - run 20261010-210157_79ce4ae8

> **SMOKE TEST - software/pipeline validation only.** Sample sizes are tiny and the model is a
> 0.5B development model. Nothing here is evidence for or against any hypothesis.

- status: completed
- model: {'model_id': 'Qwen/Qwen2.5-0.5B-Instruct', 'revision': '7ae557604adf67be50417f59c2c2f167def9a775'}
- code: git=None tree=3a80e4f5895f
- wall clock: 82.09 s; uncached generations: 49
- records: 75

## Per-condition summary (coverage-adjusted, question-level means; conditional in parentheses)

| dataset | condition | n_q | unavail | coverage | F1 | EM | verdict | cit.valid | cit.recall | support cov | grounded NLI | ev.tok | lat s | top failure |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2wikimultihopqa | extraction=llm,representation=R0,system=B0,top_k=4 | 3 | 0 | 1.000 | 0.167 (0.167) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 444.000 | 0.782 | wrong_answer |
| 2wikimultihopqa | extraction=llm,representation=R0,system=B1,top_k=4 | 3 | 0 | 1.000 | 0.133 (0.133) | 0.000 (0.000) | - | 1.000 | 0.000 | 0.667 | 0.000 | 460.667 | 0.967 | wrong_answer |
| 2wikimultihopqa | extraction=llm,representation=R1,system=B2,top_k=4 | 3 | 0 | 1.000 | 0.133 (0.133) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 1096.000 | 1.470 | wrong_answer |
| 2wikimultihopqa | extraction=llm,representation=R3,system=B3,top_k=4 | 3 | 0 | 1.000 | 0.133 (0.133) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 1294.333 | 1.796 | wrong_answer |
| 2wikimultihopqa | extraction=llm,representation=R4,system=B4,top_k=4 | 3 | 0 | 1.000 | 0.133 (0.133) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 490.667 | 0.959 | wrong_answer |
| fever | extraction=llm,representation=R0,system=B0,top_k=4 | 3 | 0 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 0.750 | 0.000 | 172.000 | 0.407 | wrong_answer |
| fever | extraction=llm,representation=R0,system=B1,top_k=4 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 181.333 | 0.361 | wrong_answer |
| fever | extraction=llm,representation=R1,system=B2,top_k=4 | 3 | 0 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 274.333 | 0.423 | wrong_answer |
| fever | extraction=llm,representation=R3,system=B3,top_k=4 | 3 | 0 | 0.667 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 325.333 | 0.477 | wrong_answer |
| fever | extraction=llm,representation=R4,system=B4,top_k=4 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 288.000 | 0.433 | wrong_answer |
| hotpotqa | extraction=llm,representation=R0,system=B0,top_k=4 | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 804.000 | 1.220 | missing_citation |
| hotpotqa | extraction=llm,representation=R0,system=B1,top_k=4 | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 0.833 | 0.000 | 585.000 | 0.913 | missing_citation |
| hotpotqa | extraction=llm,representation=R1,system=B2,top_k=4 | 3 | 0 | 1.000 | 0.889 (0.889) | 0.667 (0.667) | - | - | 0.000 | 0.833 | 0.000 | 1263.667 | 1.952 | missing_citation |
| hotpotqa | extraction=llm,representation=R3,system=B3,top_k=4 | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 0.833 | 0.000 | 1506.333 | 2.199 | wrong_answer |
| hotpotqa | extraction=llm,representation=R4,system=B4,top_k=4 | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 0.833 | 0.000 | 420.667 | 0.987 | missing_citation |
| hover | extraction=llm,representation=R0,system=B0,top_k=4 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 0.722 | 0.000 | 372.667 | 0.584 | wrong_answer |
| hover | extraction=llm,representation=R0,system=B1,top_k=4 | 3 | 0 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 0.778 | 0.000 | 421.667 | 0.601 | wrong_answer |
| hover | extraction=llm,representation=R1,system=B2,top_k=4 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 0.778 | 0.000 | 856.000 | 1.692 | wrong_answer |
| hover | extraction=llm,representation=R3,system=B3,top_k=4 | 3 | 0 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 0.778 | 0.000 | 1034.000 | 2.343 | wrong_answer |
| hover | extraction=llm,representation=R4,system=B4,top_k=4 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | 1.000 | 0.111 | 0.611 | 0.000 | 393.000 | 1.218 | wrong_answer |
| musique | extraction=llm,representation=R0,system=B0,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 400.000 | 0.742 | wrong_answer |
| musique | extraction=llm,representation=R0,system=B1,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 421.667 | 0.781 | wrong_answer |
| musique | extraction=llm,representation=R1,system=B2,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 839.667 | 1.085 | wrong_answer |
| musique | extraction=llm,representation=R3,system=B3,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 1014.000 | 1.350 | wrong_answer |
| musique | extraction=llm,representation=R4,system=B4,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 357.667 | 0.818 | wrong_answer |

## Pre-specified paired contrasts (b - a, question-level bootstrap, 2000 resamples; n < 100 => exploratory)

| dataset | stratum | a | b | metric | n | delta | 95% CI | verdict |
|---|---|---|---|---|---|---|---|---|
| 2wikimultihopqa | extraction=llm,top_k=4 | B0 | B1 | f1 | 3 | -0.033 | [-0.100, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B0 | B1 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B1 | B2 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B1 | B2 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B2 | B3 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B2 | B3 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B2 | B4 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B2 | B4 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B1 | B4 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B1 | B4 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | extraction=llm,top_k=4 | B0 | B1 | verdict_acc | 3 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | extraction=llm,top_k=4 | B1 | B2 | verdict_acc | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | extraction=llm,top_k=4 | B2 | B3 | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | extraction=llm,top_k=4 | B2 | B4 | verdict_acc | 3 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | extraction=llm,top_k=4 | B1 | B4 | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B0 | B1 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B0 | B1 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B1 | B2 | f1 | 3 | 0.222 | [0.000, 0.667] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B1 | B2 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B2 | B3 | f1 | 3 | -0.556 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B2 | B3 | em | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B2 | B4 | f1 | 3 | -0.222 | [-0.667, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B2 | B4 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B1 | B4 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B1 | B4 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | extraction=llm,top_k=4 | B0 | B1 | verdict_acc | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | extraction=llm,top_k=4 | B1 | B2 | verdict_acc | 3 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | extraction=llm,top_k=4 | B2 | B3 | verdict_acc | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | extraction=llm,top_k=4 | B2 | B4 | verdict_acc | 3 | 0.000 | [-1.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | extraction=llm,top_k=4 | B1 | B4 | verdict_acc | 3 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | extraction=llm,top_k=4 | B0 | B1 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | extraction=llm,top_k=4 | B0 | B1 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | extraction=llm,top_k=4 | B1 | B2 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | extraction=llm,top_k=4 | B1 | B2 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | extraction=llm,top_k=4 | B2 | B3 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | extraction=llm,top_k=4 | B2 | B3 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | extraction=llm,top_k=4 | B2 | B4 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | extraction=llm,top_k=4 | B2 | B4 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | extraction=llm,top_k=4 | B1 | B4 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | extraction=llm,top_k=4 | B1 | B4 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |

Unavailable conditions are excluded from metric denominators and counted in 'unavail'.
All numbers can be recomputed with `wsh report <run_dir>`.
