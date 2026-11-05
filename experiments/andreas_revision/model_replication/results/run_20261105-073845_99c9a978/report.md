# exp1 - run 20261105-073845_99c9a978

> **REVISION - exploratory.** Estimates effect sizes and variance for planning; no confirmatory claims.

- status: completed
- model: {'model_id': 'allenai/OLMo-2-1124-7B-Instruct', 'revision': '470b1fba1ae01581f270116362ee4aa1b97f4c84'}
- code: git=54a1c73e4f883f9e49cd3e3d6eb2bbf2cc68ed23-dirty tree=bce1a4a2ed53
- wall clock: 12190.56 s; uncached generations: 9185
- records: 12800

## Per-condition summary (coverage-adjusted, question-level means; conditional in parentheses)

| dataset | condition | n_q | unavail | coverage | EM | F1 | verdict | cit.valid | cit.recall | support cov | sufficient | grounded NLI | ev.tok | lat s | top failure |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2wikimultihopqa | evidence_source=gold,protocol=A,representation=R4P_FO,scope=gold_passages | 2600 | 0 | 0.888 | 0.050 (0.056) | 0.210 (0.237) | - | 1.000 | 0.347 | 1.000 | 0.953 | 0.282 | 539.677 | 1.305 | wrong_answer |
| 2wikimultihopqa | evidence_source=gold,protocol=A,representation=R4P_FO_NC,scope=gold_passages | 2600 | 0 | 0.901 | 0.068 (0.075) | 0.237 (0.264) | - | 1.000 | 0.322 | 1.000 | 0.953 | 0.266 | 519.741 | 1.247 | wrong_answer |
| hotpotqa | evidence_source=gold,protocol=A,representation=R4P_FO,scope=gold_passages | 3800 | 0 | 0.914 | 0.117 (0.127) | 0.324 (0.355) | - | 1.000 | 0.395 | 1.000 | 0.995 | 0.305 | 294.636 | 1.028 | wrong_answer |
| hotpotqa | evidence_source=gold,protocol=A,representation=R4P_FO_NC,scope=gold_passages | 3800 | 0 | 0.941 | 0.124 (0.132) | 0.341 (0.362) | - | 1.000 | 0.386 | 1.000 | 0.995 | 0.295 | 288.118 | 1.013 | wrong_answer |

## Evidence accounting (Exp1; protocols reported separately)

| dataset | condition | n | facts | content tok | overhead tok | evidence tok | added information | sufficient | answer in ev. | kept frac | truncated | required dropped | answer-bearing dropped | lat s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2wikimultihopqa | evidence_source=gold,protocol=A,representation=R4P_FO,scope=gold_passages | 2600 | 11.748 | 353.827 | 185.850 | 539.677 | explicit_relations:predicted:D_model_predicted, explicit_relations:predicted:none, order_from_derived_graph | 0.953 | 0.962 | - | - | - | - | 1.305 |
| 2wikimultihopqa | evidence_source=gold,protocol=A,representation=R4P_FO_NC,scope=gold_passages | 2600 | 11.748 | 353.827 | 165.914 | 519.741 | explicit_relations:predicted_no_contradicts:D_model_predicted, explicit_relations:predicted_no_contradicts:none, order_from_derived_graph | 0.953 | 0.962 | - | - | - | - | 1.247 |
| hotpotqa | evidence_source=gold,protocol=A,representation=R4P_FO,scope=gold_passages | 3800 | 6.356 | 202.830 | 91.807 | 294.636 | explicit_relations:predicted:D_model_predicted, explicit_relations:predicted:none, order_from_derived_graph | 0.995 | 0.995 | - | - | - | - | 1.028 |
| hotpotqa | evidence_source=gold,protocol=A,representation=R4P_FO_NC,scope=gold_passages | 3800 | 6.356 | 202.830 | 85.288 | 288.118 | explicit_relations:predicted_no_contradicts:D_model_predicted, explicit_relations:predicted_no_contradicts:none, order_from_derived_graph | 0.995 | 0.995 | - | - | - | - | 1.013 |

Unavailable conditions are excluded from metric denominators and counted in 'unavail'.
All numbers can be recomputed with `wsh report <run_dir>`.
