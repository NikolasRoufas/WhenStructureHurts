# exp0 - run 20261011-002812_6c9a495a

> **SMOKE TEST - software/pipeline validation only.** Sample sizes are tiny and the model is a
> 0.5B development model. Nothing here is evidence for or against any hypothesis.

- status: completed
- model: {'model_id': 'Qwen/Qwen2.5-0.5B-Instruct', 'revision': '7ae557604adf67be50417f59c2c2f167def9a775'}
- code: git=0ec592335817e231bed01784e7c780a6227fe130-dirty tree=6a2a26031013
- wall clock: 490.86 s; uncached generations: 74
- records: 75

## Per-condition summary (coverage-adjusted, question-level means; conditional in parentheses)

| dataset | condition | n_q | unavail | coverage | EM | F1 | verdict | cit.valid | cit.recall | support cov | sufficient | grounded NLI | ev.tok | lat s | top failure |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2wikimultihopqa | extraction=llm,representation=R0,system=B0,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.167 (0.167) | - | - | 0.000 | 0.667 | 0.000 | 0.000 | 444.000 | 9.281 | wrong_answer |
| 2wikimultihopqa | extraction=llm,representation=R0,system=B1,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.133 (0.133) | - | 1.000 | 0.000 | 0.667 | 0.000 | 0.000 | 460.667 | 11.065 | wrong_answer |
| 2wikimultihopqa | extraction=llm,representation=R1,system=B2,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.133 (0.133) | - | - | 0.000 | 0.667 | 0.000 | 0.000 | 1096.000 | 20.452 | wrong_answer |
| 2wikimultihopqa | extraction=llm,representation=R3,system=B3,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.133 (0.133) | - | - | 0.000 | 0.667 | 0.000 | 0.000 | 1294.333 | 22.162 | wrong_answer |
| 2wikimultihopqa | extraction=llm,representation=R4,system=B4,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.133 (0.133) | - | - | 0.000 | 0.667 | 0.000 | 0.000 | 490.667 | 11.065 | wrong_answer |
| fever | extraction=llm,representation=R0,system=B0,top_k=4 | 3 | 0 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 0.750 | 0.500 | 0.000 | 172.000 | 3.272 | wrong_answer |
| fever | extraction=llm,representation=R0,system=B1,top_k=4 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 1.000 | 0.000 | 181.333 | 2.155 | wrong_answer |
| fever | extraction=llm,representation=R1,system=B2,top_k=4 | 3 | 0 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 1.000 | 0.000 | 274.333 | 4.389 | wrong_answer |
| fever | extraction=llm,representation=R3,system=B3,top_k=4 | 3 | 0 | 0.667 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 1.000 | 0.000 | 325.333 | 4.389 | wrong_answer |
| fever | extraction=llm,representation=R4,system=B4,top_k=4 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 1.000 | 0.000 | 288.000 | 4.472 | wrong_answer |
| hotpotqa | extraction=llm,representation=R0,system=B0,top_k=4 | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 1.000 | 0.000 | 804.000 | 16.632 | missing_citation |
| hotpotqa | extraction=llm,representation=R0,system=B1,top_k=4 | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 0.833 | 0.667 | 0.000 | 585.000 | 14.589 | missing_citation |
| hotpotqa | extraction=llm,representation=R1,system=B2,top_k=4 | 3 | 0 | 1.000 | 0.667 (0.667) | 0.889 (0.889) | - | - | 0.000 | 0.833 | 0.667 | 0.000 | 1263.667 | 29.140 | missing_citation |
| hotpotqa | extraction=llm,representation=R3,system=B3,top_k=4 | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 0.833 | 0.667 | 0.000 | 1506.333 | 36.776 | wrong_answer |
| hotpotqa | extraction=llm,representation=R4,system=B4,top_k=4 | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 0.833 | 0.667 | 0.000 | 420.667 | 13.203 | missing_citation |
| hover | extraction=llm,representation=R0,system=B0,top_k=4 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 0.722 | 0.333 | 0.000 | 372.667 | 9.989 | wrong_answer |
| hover | extraction=llm,representation=R0,system=B1,top_k=4 | 3 | 0 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 0.778 | 0.667 | 0.000 | 421.667 | 9.989 | wrong_answer |
| hover | extraction=llm,representation=R1,system=B2,top_k=4 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 0.778 | 0.667 | 0.000 | 856.000 | 21.503 | wrong_answer |
| hover | extraction=llm,representation=R3,system=B3,top_k=4 | 3 | 0 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 0.778 | 0.667 | 0.000 | 1034.000 | 29.140 | wrong_answer |
| hover | extraction=llm,representation=R4,system=B4,top_k=4 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | 1.000 | 0.111 | 0.611 | 0.333 | 0.000 | 393.000 | 9.989 | wrong_answer |
| musique | extraction=llm,representation=R0,system=B0,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.333 | 0.000 | 400.000 | 7.683 | wrong_answer |
| musique | extraction=llm,representation=R0,system=B1,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.333 | 0.000 | 421.667 | 7.683 | wrong_answer |
| musique | extraction=llm,representation=R1,system=B2,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.333 | 0.000 | 839.667 | 17.030 | wrong_answer |
| musique | extraction=llm,representation=R3,system=B3,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.333 | 0.000 | 1014.000 | 20.452 | wrong_answer |
| musique | extraction=llm,representation=R4,system=B4,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.333 | 0.000 | 357.667 | 7.683 | wrong_answer |

## Pre-specified paired contrasts (b - a, question-level bootstrap, 2000 resamples; n < 100 => exploratory)

| dataset | stratum | edges | a | b | role | metric | n | identical ev. | delta | 95% CI | verdict | informative pairs: n, delta [CI] | Δcoverage | confirmatory |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2wikimultihopqa | extraction=llm,top_k=4 | all | B0 | B1 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| 2wikimultihopqa | extraction=llm,top_k=4 | all | B0 | B1 | secondary | f1 | 3 | 0 | -0.033 | [-0.100, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, -0.033 [-0.100, 0.000] | 0.000 | no (exploratory) |
| 2wikimultihopqa | extraction=llm,top_k=4 | all | B1 | B2 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| 2wikimultihopqa | extraction=llm,top_k=4 | all | B1 | B2 | secondary | f1 | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| 2wikimultihopqa | extraction=llm,top_k=4 | all | B2 | B3 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| 2wikimultihopqa | extraction=llm,top_k=4 | all | B2 | B3 | secondary | f1 | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| 2wikimultihopqa | extraction=llm,top_k=4 | all | B2 | B4 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| 2wikimultihopqa | extraction=llm,top_k=4 | all | B2 | B4 | secondary | f1 | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| 2wikimultihopqa | extraction=llm,top_k=4 | all | B1 | B4 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| 2wikimultihopqa | extraction=llm,top_k=4 | all | B1 | B4 | secondary | f1 | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| fever | extraction=llm,top_k=4 | all | B0 | B1 | secondary | verdict_acc | 3 | 0 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.333 [0.000, 1.000] | 0.000 | no (exploratory) |
| fever | extraction=llm,top_k=4 | all | B1 | B2 | secondary | verdict_acc | 3 | 0 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, -0.333 [-1.000, 0.000] | 0.000 | no (exploratory) |
| fever | extraction=llm,top_k=4 | all | B2 | B3 | secondary | verdict_acc | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | -0.333 | no (exploratory) |
| fever | extraction=llm,top_k=4 | all | B2 | B4 | secondary | verdict_acc | 3 | 0 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.333 [0.000, 1.000] | 0.000 | no (exploratory) |
| fever | extraction=llm,top_k=4 | all | B1 | B4 | secondary | verdict_acc | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| hotpotqa | extraction=llm,top_k=4 | all | B0 | B1 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| hotpotqa | extraction=llm,top_k=4 | all | B0 | B1 | secondary | f1 | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| hotpotqa | extraction=llm,top_k=4 | all | B1 | B2 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| hotpotqa | extraction=llm,top_k=4 | all | B1 | B2 | secondary | f1 | 3 | 0 | 0.222 | [0.000, 0.667] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.222 [0.000, 0.667] | 0.000 | no (exploratory) |
| hotpotqa | extraction=llm,top_k=4 | all | B2 | B3 | secondary | em | 3 | 0 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, -0.333 [-1.000, 0.000] | 0.000 | no (exploratory) |
| hotpotqa | extraction=llm,top_k=4 | all | B2 | B3 | secondary | f1 | 3 | 0 | -0.556 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, -0.556 [-1.000, 0.000] | 0.000 | no (exploratory) |
| hotpotqa | extraction=llm,top_k=4 | all | B2 | B4 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| hotpotqa | extraction=llm,top_k=4 | all | B2 | B4 | secondary | f1 | 3 | 0 | -0.222 | [-0.667, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, -0.222 [-0.667, 0.000] | 0.000 | no (exploratory) |
| hotpotqa | extraction=llm,top_k=4 | all | B1 | B4 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| hotpotqa | extraction=llm,top_k=4 | all | B1 | B4 | secondary | f1 | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| hover | extraction=llm,top_k=4 | all | B0 | B1 | secondary | verdict_acc | 3 | 1 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 2, -0.500 [-1.000, 0.000] | 0.000 | no (exploratory) |
| hover | extraction=llm,top_k=4 | all | B1 | B2 | secondary | verdict_acc | 3 | 0 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.333 [0.000, 1.000] | 0.000 | no (exploratory) |
| hover | extraction=llm,top_k=4 | all | B2 | B3 | secondary | verdict_acc | 3 | 0 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, -0.333 [-1.000, 0.000] | 0.000 | no (exploratory) |
| hover | extraction=llm,top_k=4 | all | B2 | B4 | secondary | verdict_acc | 3 | 0 | 0.000 | [-1.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [-1.000, 1.000] | 0.000 | no (exploratory) |
| hover | extraction=llm,top_k=4 | all | B1 | B4 | secondary | verdict_acc | 3 | 0 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.333 [0.000, 1.000] | 0.000 | no (exploratory) |
| musique | extraction=llm,top_k=4 | all | B0 | B1 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| musique | extraction=llm,top_k=4 | all | B0 | B1 | secondary | f1 | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| musique | extraction=llm,top_k=4 | all | B1 | B2 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| musique | extraction=llm,top_k=4 | all | B1 | B2 | secondary | f1 | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| musique | extraction=llm,top_k=4 | all | B2 | B3 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| musique | extraction=llm,top_k=4 | all | B2 | B3 | secondary | f1 | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| musique | extraction=llm,top_k=4 | all | B2 | B4 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| musique | extraction=llm,top_k=4 | all | B2 | B4 | secondary | f1 | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| musique | extraction=llm,top_k=4 | all | B1 | B4 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |
| musique | extraction=llm,top_k=4 | all | B1 | B4 | secondary | f1 | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | 3, 0.000 [0.000, 0.000] | 0.000 | no (exploratory) |

Unavailable conditions are excluded from metric denominators and counted in 'unavail'.
All numbers can be recomputed with `wsh report <run_dir>`.
