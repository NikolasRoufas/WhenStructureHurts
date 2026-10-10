# exp3 - run 20261010-130025_80bc797c

> **SMOKE TEST - software/pipeline validation only.** Sample sizes are tiny and the model is a
> 0.5B development model. Nothing here is evidence for or against any hypothesis.

- status: completed
- model: {'model_id': 'Qwen/Qwen2.5-0.5B-Instruct', 'revision': '7ae557604adf67be50417f59c2c2f167def9a775'}
- code: git=None tree=3a80e4f5895f
- wall clock: 128.61 s; uncached generations: 23
- records: 75

## Per-condition summary (coverage-adjusted, question-level means; conditional in parentheses)

| dataset | condition | n_q | unavail | coverage | F1 | EM | verdict | cit.valid | cit.recall | support cov | grounded NLI | ev.tok | lat s | top failure |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2wikimultihopqa | component_condition=C1,representation=R4 | 3 | 0 | 1.000 | 0.167 (0.167) | 0.000 (0.000) | - | - | 0.000 | 1.000 | 0.000 | 684.667 | 1.145 | wrong_answer |
| 2wikimultihopqa | component_condition=C2,representation=R4 | 3 | 0 | 1.000 | 0.500 (0.500) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 409.667 | 0.757 | wrong_answer |
| 2wikimultihopqa | component_condition=C3,representation=R4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 438.000 | 0.980 | wrong_answer |
| 2wikimultihopqa | component_condition=C4,representation=R4 | 3 | 0 | 1.000 | 0.133 (0.133) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 490.667 | 0.959 | wrong_answer |
| 2wikimultihopqa | component_condition=oracle,representation=R4 | 3 | 0 | 1.000 | 0.412 (0.412) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 392.667 | 1.041 | wrong_answer |
| fever | component_condition=C1,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| fever | component_condition=C2,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| fever | component_condition=C3,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| fever | component_condition=C4,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| fever | component_condition=oracle,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| hotpotqa | component_condition=C1,representation=R4 | 2 | 1 | 1.000 | 0.500 (0.500) | 0.500 (0.500) | - | - | 0.000 | 1.000 | 0.000 | 759.000 | 1.192 | wrong_answer |
| hotpotqa | component_condition=C2,representation=R4 | 2 | 1 | 1.000 | 0.500 (0.500) | 0.500 (0.500) | - | - | 0.000 | 1.000 | 0.000 | 498.000 | 0.970 | wrong_answer |
| hotpotqa | component_condition=C3,representation=R4 | 2 | 1 | 1.000 | 0.500 (0.500) | 0.500 (0.500) | - | - | 0.000 | 1.000 | 0.000 | 463.500 | 0.820 | wrong_answer |
| hotpotqa | component_condition=C4,representation=R4 | 2 | 1 | 1.000 | 0.500 (0.500) | 0.500 (0.500) | - | - | 0.000 | 0.750 | 0.000 | 404.500 | 1.102 | wrong_answer |
| hotpotqa | component_condition=oracle,representation=R4 | 2 | 1 | 1.000 | 0.500 (0.500) | 0.500 (0.500) | - | - | 0.000 | 1.000 | 0.000 | 484.500 | 1.020 | wrong_answer |
| hover | component_condition=C1,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| hover | component_condition=C2,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| hover | component_condition=C3,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| hover | component_condition=C4,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| hover | component_condition=oracle,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - |
| musique | component_condition=C1,representation=R4 | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 685.000 | 1.553 | wrong_answer |
| musique | component_condition=C2,representation=R4 | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 415.000 | 0.746 | wrong_answer |
| musique | component_condition=C3,representation=R4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.833 | 0.000 | 424.000 | 1.293 | wrong_answer |
| musique | component_condition=C4,representation=R4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 357.667 | 0.818 | wrong_answer |
| musique | component_condition=oracle,representation=R4 | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 0.000 | 398.333 | 0.710 | wrong_answer |

## Pre-specified paired contrasts (b - a, question-level bootstrap, 2000 resamples; n < 100 => exploratory)

| dataset | stratum | a | b | metric | n | delta | 95% CI | verdict |
|---|---|---|---|---|---|---|---|---|
| 2wikimultihopqa |  | oracle | C1 | f1 | 3 | -0.245 | [-1.000, 0.265] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa |  | oracle | C1 | em | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa |  | oracle | C2 | f1 | 3 | 0.088 | [0.000, 0.265] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa |  | oracle | C2 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa |  | oracle | C3 | f1 | 3 | -0.412 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa |  | oracle | C3 | em | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa |  | oracle | C4 | f1 | 3 | -0.278 | [-1.000, 0.165] | inconclusive (CI contains 0; not evidence of equivalence) |
| 2wikimultihopqa |  | oracle | C4 | em | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| fever |  | oracle | C1 | verdict_acc | 0 | - | - | no paired data |
| fever |  | oracle | C2 | verdict_acc | 0 | - | - | no paired data |
| fever |  | oracle | C3 | verdict_acc | 0 | - | - | no paired data |
| fever |  | oracle | C4 | verdict_acc | 0 | - | - | no paired data |
| hotpotqa |  | oracle | C1 | f1 | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa |  | oracle | C1 | em | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa |  | oracle | C2 | f1 | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa |  | oracle | C2 | em | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa |  | oracle | C3 | f1 | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa |  | oracle | C3 | em | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa |  | oracle | C4 | f1 | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hotpotqa |  | oracle | C4 | em | 2 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| hover |  | oracle | C1 | verdict_acc | 0 | - | - | no paired data |
| hover |  | oracle | C2 | verdict_acc | 0 | - | - | no paired data |
| hover |  | oracle | C3 | verdict_acc | 0 | - | - | no paired data |
| hover |  | oracle | C4 | verdict_acc | 0 | - | - | no paired data |
| musique |  | oracle | C1 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique |  | oracle | C1 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique |  | oracle | C2 | f1 | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique |  | oracle | C2 | em | 3 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique |  | oracle | C3 | f1 | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique |  | oracle | C3 | em | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique |  | oracle | C4 | f1 | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |
| musique |  | oracle | C4 | em | 3 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) |

## Component attribution (relative to oracle)

```
{
  "C1": {
    "no_degradation": 7,
    "degraded_with_evidence_loss(component)": 1
  },
  "C2": {
    "no_degradation": 8
  },
  "C3": {
    "no_degradation": 5,
    "degraded_with_evidence_loss(component)": 3
  },
  "C4": {
    "no_degradation": 6,
    "degraded_with_evidence_loss(component)": 2
  }
}
```

Unavailable conditions are excluded from metric denominators and counted in 'unavail'.
All numbers can be recomputed with `wsh report <run_dir>`.
