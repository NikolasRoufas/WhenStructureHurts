# exp0 - run 20261010-124651_79ce4ae8

> **SMOKE TEST - software/pipeline validation only.** Sample sizes are tiny and the model is a
> 0.5B development model. Nothing here is evidence for or against any hypothesis.

- status: completed
- model: {'model_id': 'Qwen/Qwen2.5-0.5B-Instruct', 'revision': '7ae557604adf67be50417f59c2c2f167def9a775'}
- code: git=None tree=2a186c4f24aa
- wall clock: 575.14 s; uncached generations: 60
- records: 75

## Per-condition summary (coverage-adjusted, question-level means; conditional in parentheses)

| group | n_q | unavail | coverage | F1 | EM | verdict | cit.valid | cit.recall | support cov | grounded NLI | ev.tok | lat s | top failure |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2wikimultihopqa | extraction=llm,representation=R0,system=B0,top_k=4 | 3 | 0 | 1.000 | 0.167 (0.167) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 444.000 | 0.782 | wrong_answer |
| 2wikimultihopqa | extraction=llm,representation=R0,system=B1,top_k=4 | 3 | 0 | 1.000 | 0.167 (0.167) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 444.000 | 0.782 | wrong_answer |
| 2wikimultihopqa | extraction=llm,representation=R1,system=B2,top_k=4 | 3 | 0 | 1.000 | 0.133 (0.133) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 1109.667 | 1.533 | wrong_answer |
| 2wikimultihopqa | extraction=llm,representation=R3,system=B3,top_k=4 | 3 | 0 | 1.000 | 0.133 (0.133) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 1296.000 | 1.765 | wrong_answer |
| 2wikimultihopqa | extraction=llm,representation=R4,system=B4,top_k=4 | 3 | 0 | 1.000 | 0.167 (0.167) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 553.333 | 0.787 | wrong_answer |
| fever | extraction=llm,representation=R0,system=B0,top_k=4 | 3 | 0 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 0.750 | 0.000 | 172.000 | 0.407 | wrong_answer |
| fever | extraction=llm,representation=R0,system=B1,top_k=4 | 3 | 0 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 0.750 | 0.000 | 172.000 | 0.407 | wrong_answer |
| fever | extraction=llm,representation=R1,system=B2,top_k=4 | 3 | 0 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 0.750 | 0.000 | 248.333 | 0.587 | wrong_answer |
| fever | extraction=llm,representation=R3,system=B3,top_k=4 | 3 | 0 | 1.000 | - | - | 0.000 (0.000) | - | 0.000 | 0.750 | 0.000 | 296.000 | 0.609 | wrong_answer |
| fever | extraction=llm,representation=R4,system=B4,top_k=4 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 317.667 | 0.594 | wrong_answer |
| hotpotqa | extraction=llm,representation=R0,system=B0,top_k=4 | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 804.000 | 1.220 | missing_citation |
| hotpotqa | extraction=llm,representation=R0,system=B1,top_k=4 | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 804.000 | 1.220 | missing_citation |
| hotpotqa | extraction=llm,representation=R1,system=B2,top_k=4 | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 1854.333 | 3.238 | wrong_answer |
| hotpotqa | extraction=llm,representation=R3,system=B3,top_k=4 | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 2230.333 | 3.376 | wrong_answer |
| hotpotqa | extraction=llm,representation=R4,system=B4,top_k=4 | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 425.000 | 0.770 | missing_citation |
| hover | extraction=llm,representation=R0,system=B0,top_k=4 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 0.722 | 0.000 | 372.667 | 0.584 | wrong_answer |
| hover | extraction=llm,representation=R0,system=B1,top_k=4 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 0.722 | 0.000 | 372.667 | 0.584 | wrong_answer |
| hover | extraction=llm,representation=R1,system=B2,top_k=4 | 3 | 0 | 1.000 | - | - | 0.667 (0.667) | - | 0.000 | 0.722 | 0.000 | 705.667 | 1.699 | missing_citation |
| hover | extraction=llm,representation=R3,system=B3,top_k=4 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 0.722 | 0.000 | 855.333 | 2.013 | wrong_answer |
| hover | extraction=llm,representation=R4,system=B4,top_k=4 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 0.833 | 0.000 | 398.000 | 1.007 | wrong_answer |
| musique | extraction=llm,representation=R0,system=B0,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 400.000 | 0.742 | wrong_answer |
| musique | extraction=llm,representation=R0,system=B1,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 400.000 | 0.742 | wrong_answer |
| musique | extraction=llm,representation=R1,system=B2,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 838.333 | 1.024 | wrong_answer |
| musique | extraction=llm,representation=R3,system=B3,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 1026.000 | 1.319 | wrong_answer |
| musique | extraction=llm,representation=R4,system=B4,top_k=4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.583 | 0.000 | 359.667 | 0.631 | wrong_answer |

## Pre-specified paired contrasts (b - a, question-level bootstrap, 2000 resamples; n < 100 => exploratory)

| dataset | stratum | a | b | metric | n | delta | 95% CI | verdict |
|---|---|---|---|---|---|---|---|---|
| 2wikimultihopqa | extraction=llm,top_k=4 | B0 | B1 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B0 | B1 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B1 | B2 | f1 | 3 | -0.033 | [-0.100, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B1 | B2 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B2 | B3 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B2 | B3 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B2 | B4 | f1 | 3 | 0.033 | [0.000, 0.100] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B2 | B4 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B1 | B4 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | extraction=llm,top_k=4 | B1 | B4 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | extraction=llm,top_k=4 | B0 | B1 | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | extraction=llm,top_k=4 | B1 | B2 | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | extraction=llm,top_k=4 | B2 | B3 | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | extraction=llm,top_k=4 | B2 | B4 | verdict_acc | 3 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | extraction=llm,top_k=4 | B1 | B4 | verdict_acc | 3 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B0 | B1 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B0 | B1 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B1 | B2 | f1 | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B1 | B2 | em | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B2 | B3 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B2 | B3 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B2 | B4 | f1 | 3 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B2 | B4 | em | 3 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B1 | B4 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | extraction=llm,top_k=4 | B1 | B4 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | extraction=llm,top_k=4 | B0 | B1 | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | extraction=llm,top_k=4 | B1 | B2 | verdict_acc | 3 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | extraction=llm,top_k=4 | B2 | B3 | verdict_acc | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | extraction=llm,top_k=4 | B2 | B4 | verdict_acc | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | extraction=llm,top_k=4 | B1 | B4 | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
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
