# exp1 - run 20261010-125634_2390c640

> **SMOKE TEST - software/pipeline validation only.** Sample sizes are tiny and the model is a
> 0.5B development model. Nothing here is evidence for or against any hypothesis.

- status: completed
- model: {'model_id': 'Qwen/Qwen2.5-0.5B-Instruct', 'revision': '7ae557604adf67be50417f59c2c2f167def9a775'}
- code: git=None tree=2a186c4f24aa
- wall clock: 113.79 s; uncached generations: 119
- records: 210

## Per-condition summary (coverage-adjusted, question-level means; conditional in parentheses)

| dataset | condition | n_q | unavail | coverage | F1 | EM | verdict | cit.valid | cit.recall | support cov | grounded NLI | ev.tok | lat s | top failure |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,representation=R0,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 302.333 | 0.716 | wrong_answer |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,representation=R1,scope=gold_passages | 3 | 0 | 0.667 | 0.167 (0.250) | 0.000 (0.000) | - | - | 0.000 | 0.833 | 0.000 | 288.000 | 0.641 | wrong_answer |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,representation=R2,scope=gold_passages,shuffle_seed=0 | 3 | 0 | 1.000 | 0.133 (0.133) | 0.000 (0.000) | - | - | 0.000 | 0.833 | 0.000 | 281.333 | 1.084 | wrong_answer |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,representation=R3,scope=gold_passages | 3 | 0 | 1.000 | 0.250 (0.250) | 0.000 (0.000) | - | 1.000 | 0.167 | 1.000 | 0.000 | 287.667 | 1.383 | wrong_answer |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.167 (0.167) | 0.000 (0.000) | - | - | 0.000 | 0.833 | 0.000 | 271.333 | 0.916 | wrong_answer |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,representation=R4P,scope=gold_passages | 3 | 0 | 1.000 | 0.167 (0.167) | 0.000 (0.000) | - | - | 0.000 | 0.833 | 0.000 | 273.667 | 0.918 | wrong_answer |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,representation=R5,scope=gold_passages | 3 | 0 | 0.667 | 0.167 (0.250) | 0.000 (0.000) | - | - | 0.000 | 0.833 | 0.000 | 288.000 | 0.641 | wrong_answer |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,representation=R0,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 302.333 | 0.716 | wrong_answer |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 382.667 | 0.736 | wrong_answer |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,representation=R2,scope=gold_passages,shuffle_seed=0 | 3 | 0 | 1.000 | 0.133 (0.133) | 0.000 (0.000) | - | - | 0.000 | 1.000 | 0.000 | 382.667 | 0.815 | wrong_answer |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,representation=R3,scope=gold_passages | 3 | 0 | 1.000 | 0.250 (0.250) | 0.000 (0.000) | - | - | 0.000 | 1.000 | 0.000 | 390.667 | 0.748 | wrong_answer |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.412 (0.412) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 392.667 | 1.041 | wrong_answer |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,representation=R4P,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 409.667 | 0.757 | wrong_answer |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,representation=R5,scope=gold_passages | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 382.667 | 0.736 | wrong_answer |
| fever | budget_mode=min_matched,evidence_source=gold,representation=R0,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | budget_mode=min_matched,evidence_source=gold,representation=R1,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | budget_mode=min_matched,evidence_source=gold,representation=R2,scope=gold_passages,shuffle_seed=0 | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | budget_mode=min_matched,evidence_source=gold,representation=R3,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| fever | budget_mode=min_matched,evidence_source=gold,representation=R4,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | budget_mode=min_matched,evidence_source=gold,representation=R4P,scope=gold_passages | 2 | 1 | 0.000 | - | - | 0.000 (-) | - | 0.000 | 0.750 | - | 30.000 | 0.384 | unparseable_verdict |
| fever | budget_mode=min_matched,evidence_source=gold,representation=R5,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | budget_mode=none,evidence_source=gold,representation=R0,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | budget_mode=none,evidence_source=gold,representation=R1,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | budget_mode=none,evidence_source=gold,representation=R2,scope=gold_passages,shuffle_seed=0 | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | budget_mode=none,evidence_source=gold,representation=R3,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| fever | budget_mode=none,evidence_source=gold,representation=R4,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| fever | budget_mode=none,evidence_source=gold,representation=R4P,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 68.500 | 0.411 | wrong_answer |
| fever | budget_mode=none,evidence_source=gold,representation=R5,scope=gold_passages | 2 | 1 | 0.500 | - | - | 0.000 (0.000) | - | 0.000 | 1.000 | 0.000 | 63.500 | 0.409 | wrong_answer |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,representation=R0,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 341.667 | 1.120 | missing_citation |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 0.833 | 0.000 | 313.000 | 0.872 | missing_citation |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,representation=R2,scope=gold_passages,shuffle_seed=0 | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 0.500 | 0.000 | 310.000 | 1.080 | wrong_answer |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,representation=R3,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 0.833 | 0.000 | 324.667 | 1.204 | wrong_answer |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 0.833 | 0.000 | 321.333 | 0.923 | wrong_answer |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,representation=R4P,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 0.833 | 0.000 | 327.333 | 0.949 | wrong_answer |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,representation=R5,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 0.833 | 0.000 | 318.000 | 0.880 | wrong_answer |
| hotpotqa | budget_mode=none,evidence_source=gold,representation=R0,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 341.667 | 1.120 | missing_citation |
| hotpotqa | budget_mode=none,evidence_source=gold,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 422.333 | 1.005 | missing_citation |
| hotpotqa | budget_mode=none,evidence_source=gold,representation=R2,scope=gold_passages,shuffle_seed=0 | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 422.333 | 0.899 | wrong_answer |
| hotpotqa | budget_mode=none,evidence_source=gold,representation=R3,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 430.333 | 1.060 | missing_citation |
| hotpotqa | budget_mode=none,evidence_source=gold,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 429.000 | 1.089 | missing_citation |
| hotpotqa | budget_mode=none,evidence_source=gold,representation=R4P,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 438.000 | 1.056 | missing_citation |
| hotpotqa | budget_mode=none,evidence_source=gold,representation=R5,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 422.333 | 1.005 | missing_citation |
| hover | budget_mode=min_matched,evidence_source=gold,representation=R0,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 257.000 | 0.789 | wrong_answer |
| hover | budget_mode=min_matched,evidence_source=gold,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 0.778 | 0.000 | 232.667 | 0.604 | wrong_answer |
| hover | budget_mode=min_matched,evidence_source=gold,representation=R2,scope=gold_passages,shuffle_seed=0 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 0.889 | 0.000 | 226.000 | 0.593 | wrong_answer |
| hover | budget_mode=min_matched,evidence_source=gold,representation=R3,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| hover | budget_mode=min_matched,evidence_source=gold,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 0.778 | 0.000 | 232.667 | 0.604 | wrong_answer |
| hover | budget_mode=min_matched,evidence_source=gold,representation=R4P,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 0.778 | 0.000 | 231.667 | 0.587 | wrong_answer |
| hover | budget_mode=min_matched,evidence_source=gold,representation=R5,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 0.778 | 0.000 | 232.667 | 0.604 | wrong_answer |
| hover | budget_mode=none,evidence_source=gold,representation=R0,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 257.000 | 0.789 | wrong_answer |
| hover | budget_mode=none,evidence_source=gold,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | budget_mode=none,evidence_source=gold,representation=R2,scope=gold_passages,shuffle_seed=0 | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.609 | wrong_answer |
| hover | budget_mode=none,evidence_source=gold,representation=R3,scope=gold_passages | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| hover | budget_mode=none,evidence_source=gold,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| hover | budget_mode=none,evidence_source=gold,representation=R4P,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 338.000 | 1.212 | wrong_answer |
| hover | budget_mode=none,evidence_source=gold,representation=R5,scope=gold_passages | 3 | 0 | 1.000 | - | - | 0.333 (0.333) | - | 0.000 | 1.000 | 0.000 | 304.667 | 0.695 | wrong_answer |
| musique | budget_mode=min_matched,evidence_source=gold,representation=R0,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 287.667 | 0.926 | wrong_answer |
| musique | budget_mode=min_matched,evidence_source=gold,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 0.917 | 0.000 | 275.333 | 0.598 | wrong_answer |
| musique | budget_mode=min_matched,evidence_source=gold,representation=R2,scope=gold_passages,shuffle_seed=0 | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 0.917 | 0.000 | 269.333 | 0.594 | wrong_answer |
| musique | budget_mode=min_matched,evidence_source=gold,representation=R3,scope=gold_passages | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.917 | 0.000 | 259.000 | 0.742 | wrong_answer |
| musique | budget_mode=min_matched,evidence_source=gold,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.917 | 0.000 | 259.333 | 0.511 | wrong_answer |
| musique | budget_mode=min_matched,evidence_source=gold,representation=R4P,scope=gold_passages | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.750 | 0.000 | 259.000 | 0.797 | wrong_answer |
| musique | budget_mode=min_matched,evidence_source=gold,representation=R5,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 0.917 | 0.000 | 264.333 | 0.546 | wrong_answer |
| musique | budget_mode=none,evidence_source=gold,representation=R0,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 287.667 | 0.926 | wrong_answer |
| musique | budget_mode=none,evidence_source=gold,representation=R1,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 382.000 | 0.700 | missing_citation |
| musique | budget_mode=none,evidence_source=gold,representation=R2,scope=gold_passages,shuffle_seed=0 | 3 | 0 | 1.000 | 0.133 (0.133) | 0.000 (0.000) | - | - | 0.000 | 1.000 | 0.000 | 382.000 | 0.706 | wrong_answer |
| musique | budget_mode=none,evidence_source=gold,representation=R3,scope=gold_passages | 3 | 0 | 1.000 | 0.667 (0.667) | 0.667 (0.667) | - | - | 0.000 | 1.000 | 0.000 | 392.667 | 0.780 | missing_citation |
| musique | budget_mode=none,evidence_source=gold,representation=R4,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 398.333 | 0.710 | wrong_answer |
| musique | budget_mode=none,evidence_source=gold,representation=R4P,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 415.000 | 0.746 | wrong_answer |
| musique | budget_mode=none,evidence_source=gold,representation=R5,scope=gold_passages | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 382.000 | 0.663 | wrong_answer |

## Pre-specified paired contrasts (b - a, question-level bootstrap, 2000 resamples; n < 100 => exploratory)

| dataset | stratum | a | b | metric | n | delta | 95% CI | verdict |
|---|---|---|---|---|---|---|---|---|
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R0 | R1 | f1 | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R0 | R1 | em | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R0 | R1 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R0 | R1 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R1 | R2 | f1 | 3 | -0.033 | [-0.100, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R1 | R2 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R1 | R2 | f1 | 3 | -0.367 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R1 | R2 | em | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R1 | R5 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R1 | R5 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R1 | R5 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R1 | R5 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R5 | R3 | f1 | 3 | 0.083 | [0.000, 0.250] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R5 | R3 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R5 | R3 | f1 | 3 | -0.250 | [-1.000, 0.250] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R5 | R3 | em | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R5 | R4 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R5 | R4 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R5 | R4 | f1 | 3 | -0.088 | [-0.265, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R5 | R4 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R4 | R4P | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R4 | R4P | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R4 | R4P | f1 | 3 | 0.088 | [0.000, 0.265] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R4 | R4P | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R0 | R1 | verdict_acc | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | budget_mode=none,evidence_source=gold,scope=gold_passages | R0 | R1 | verdict_acc | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R1 | R2 | verdict_acc | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | budget_mode=none,evidence_source=gold,scope=gold_passages | R1 | R2 | verdict_acc | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R1 | R5 | verdict_acc | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | budget_mode=none,evidence_source=gold,scope=gold_passages | R1 | R5 | verdict_acc | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R5 | R3 | verdict_acc | 0 | - | - | no paired data |
| fever | budget_mode=none,evidence_source=gold,scope=gold_passages | R5 | R3 | verdict_acc | 0 | - | - | no paired data |
| fever | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R5 | R4 | verdict_acc | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | budget_mode=none,evidence_source=gold,scope=gold_passages | R5 | R4 | verdict_acc | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R4 | R4P | verdict_acc | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever | budget_mode=none,evidence_source=gold,scope=gold_passages | R4 | R4P | verdict_acc | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R0 | R1 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R0 | R1 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R0 | R1 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R0 | R1 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R1 | R2 | f1 | 3 | -0.167 | [-0.500, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R1 | R2 | em | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R1 | R2 | f1 | 3 | -0.167 | [-0.500, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R1 | R2 | em | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R1 | R5 | f1 | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R1 | R5 | em | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R1 | R5 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R1 | R5 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R5 | R3 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R5 | R3 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R5 | R3 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R5 | R3 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R5 | R4 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R5 | R4 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R5 | R4 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R5 | R4 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R4 | R4P | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R4 | R4P | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R4 | R4P | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa | budget_mode=none,evidence_source=gold,scope=gold_passages | R4 | R4P | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R0 | R1 | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | budget_mode=none,evidence_source=gold,scope=gold_passages | R0 | R1 | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R1 | R2 | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | budget_mode=none,evidence_source=gold,scope=gold_passages | R1 | R2 | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R1 | R5 | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | budget_mode=none,evidence_source=gold,scope=gold_passages | R1 | R5 | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R5 | R3 | verdict_acc | 0 | - | - | no paired data |
| hover | budget_mode=none,evidence_source=gold,scope=gold_passages | R5 | R3 | verdict_acc | 0 | - | - | no paired data |
| hover | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R5 | R4 | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | budget_mode=none,evidence_source=gold,scope=gold_passages | R5 | R4 | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R4 | R4P | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover | budget_mode=none,evidence_source=gold,scope=gold_passages | R4 | R4P | verdict_acc | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R0 | R1 | f1 | 3 | 0.000 | [-1.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R0 | R1 | em | 3 | 0.000 | [-1.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=none,evidence_source=gold,scope=gold_passages | R0 | R1 | f1 | 3 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=none,evidence_source=gold,scope=gold_passages | R0 | R1 | em | 3 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R1 | R2 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R1 | R2 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=none,evidence_source=gold,scope=gold_passages | R1 | R2 | f1 | 3 | -0.533 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=none,evidence_source=gold,scope=gold_passages | R1 | R2 | em | 3 | -0.667 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R1 | R5 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R1 | R5 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=none,evidence_source=gold,scope=gold_passages | R1 | R5 | f1 | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=none,evidence_source=gold,scope=gold_passages | R1 | R5 | em | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R5 | R3 | f1 | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R5 | R3 | em | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=none,evidence_source=gold,scope=gold_passages | R5 | R3 | f1 | 3 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=none,evidence_source=gold,scope=gold_passages | R5 | R3 | em | 3 | 0.333 | [0.000, 1.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R5 | R4 | f1 | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R5 | R4 | em | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=none,evidence_source=gold,scope=gold_passages | R5 | R4 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=none,evidence_source=gold,scope=gold_passages | R5 | R4 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R4 | R4P | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=min_matched,evidence_source=gold,scope=gold_passages | R4 | R4P | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=none,evidence_source=gold,scope=gold_passages | R4 | R4P | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique | budget_mode=none,evidence_source=gold,scope=gold_passages | R4 | R4P | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |

Unavailable conditions are excluded from metric denominators and counted in 'unavail'.
All numbers can be recomputed with `wsh report <run_dir>`.
