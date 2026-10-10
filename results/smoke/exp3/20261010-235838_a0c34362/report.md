# exp3 - run 20261010-235838_a0c34362

> **SMOKE TEST - software/pipeline validation only.** Sample sizes are tiny and the model is a
> 0.5B development model. Nothing here is evidence for or against any hypothesis.

- status: completed
- model: {'model_id': 'Qwen/Qwen2.5-0.5B-Instruct', 'revision': '7ae557604adf67be50417f59c2c2f167def9a775'}
- code: git=None tree=4d5eb2ce8406
- wall clock: 351.75 s; uncached generations: 24
- records: 75

## Per-condition summary (coverage-adjusted, question-level means; conditional in parentheses)

| dataset | condition | n_q | unavail | coverage | EM | F1 | verdict | cit.valid | cit.recall | support cov | sufficient | grounded NLI | ev.tok | lat s | top failure |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2wikimultihopqa | component_condition=C1,representation=R4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.167 (0.167) | - | - | 0.000 | 1.000 | 0.667 | 0.000 | 684.667 | 2.147 | wrong_answer |
| 2wikimultihopqa | component_condition=C2,representation=R4 | 3 | 0 | 1.000 | 0.333 (0.333) | 0.500 (0.500) | - | - | 0.000 | 1.000 | 0.667 | 0.000 | 409.667 | 0.693 | wrong_answer |
| 2wikimultihopqa | component_condition=C3,representation=R4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.000 | 0.000 | 438.000 | 1.287 | wrong_answer |
| 2wikimultihopqa | component_condition=C4,representation=R4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.133 (0.133) | - | - | 0.000 | 0.667 | 0.000 | 0.000 | 490.667 | 1.481 | wrong_answer |
| 2wikimultihopqa | component_condition=oracle,representation=R4 | 3 | 0 | 1.000 | 0.333 (0.333) | 0.412 (0.412) | - | - | 0.000 | 1.000 | 0.667 | 0.000 | 392.667 | 0.910 | wrong_answer |
| fever | component_condition=C1,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - | - |
| fever | component_condition=C2,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - | - |
| fever | component_condition=C3,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - | - |
| fever | component_condition=C4,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - | - |
| fever | component_condition=oracle,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - | - |
| hotpotqa | component_condition=C1,representation=R4 | 2 | 1 | 1.000 | 0.500 (0.500) | 0.500 (0.500) | - | - | 0.000 | 1.000 | 1.000 | 0.000 | 759.000 | 1.683 | wrong_answer |
| hotpotqa | component_condition=C2,representation=R4 | 2 | 1 | 1.000 | 0.500 (0.500) | 0.500 (0.500) | - | - | 0.000 | 1.000 | 1.000 | 0.000 | 498.000 | 0.826 | wrong_answer |
| hotpotqa | component_condition=C3,representation=R4 | 2 | 1 | 1.000 | 0.500 (0.500) | 0.500 (0.500) | - | - | 0.000 | 1.000 | 1.000 | 0.000 | 463.500 | 1.013 | wrong_answer |
| hotpotqa | component_condition=C4,representation=R4 | 2 | 1 | 1.000 | 0.500 (0.500) | 0.500 (0.500) | - | - | 0.000 | 0.750 | 0.500 | 0.000 | 404.500 | 1.115 | wrong_answer |
| hotpotqa | component_condition=oracle,representation=R4 | 2 | 1 | 1.000 | 0.500 (0.500) | 0.500 (0.500) | - | - | 0.000 | 1.000 | 1.000 | 0.000 | 484.500 | 0.767 | wrong_answer |
| hover | component_condition=C1,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - | - |
| hover | component_condition=C2,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - | - |
| hover | component_condition=C3,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - | - |
| hover | component_condition=C4,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - | - |
| hover | component_condition=oracle,representation=R4 | 0 | 3 | - | - | - | - | - | - | - | - | - | - | - | - |
| musique | component_condition=C1,representation=R4 | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 1.000 | 0.000 | 685.000 | 1.359 | wrong_answer |
| musique | component_condition=C2,representation=R4 | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 1.000 | 0.000 | 415.000 | 0.728 | wrong_answer |
| musique | component_condition=C3,representation=R4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.833 | 0.000 | 0.000 | 424.000 | 1.046 | wrong_answer |
| musique | component_condition=C4,representation=R4 | 3 | 0 | 1.000 | 0.000 (0.000) | 0.000 (0.000) | - | - | 0.000 | 0.667 | 0.333 | 0.000 | 357.667 | 1.405 | wrong_answer |
| musique | component_condition=oracle,representation=R4 | 3 | 0 | 1.000 | 0.333 (0.333) | 0.333 (0.333) | - | - | 0.000 | 1.000 | 1.000 | 0.000 | 398.333 | 0.713 | wrong_answer |

## Pre-specified paired contrasts (b - a, question-level bootstrap, 2000 resamples; n < 100 => exploratory)

| dataset | stratum | edges | a | b | role | metric | n | identical ev. | delta | 95% CI | verdict | confirmatory |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2wikimultihopqa |  | all | oracle | C1 | secondary | em | 3 | 0 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | all | oracle | C1 | secondary | f1 | 3 | 0 | -0.245 | [-1.000, 0.265] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | edge_stratum=B_derived_exact_anchor | oracle | C1 | secondary | em | 2 | 0 | -0.500 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | edge_stratum=B_derived_exact_anchor | oracle | C1 | secondary | f1 | 2 | 0 | -0.368 | [-1.000, 0.265] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | edge_stratum=C_derived_fallback_anchor | oracle | C1 | secondary | em | 1 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | edge_stratum=C_derived_fallback_anchor | oracle | C1 | secondary | f1 | 1 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | all | oracle | C2 | secondary | em | 3 | 1 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | all | oracle | C2 | secondary | f1 | 3 | 1 | 0.088 | [0.000, 0.265] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | edge_stratum=B_derived_exact_anchor | oracle | C2 | secondary | em | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | edge_stratum=B_derived_exact_anchor | oracle | C2 | secondary | f1 | 2 | 0 | 0.132 | [0.000, 0.265] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | edge_stratum=C_derived_fallback_anchor | oracle | C2 | secondary | em | 1 | 1 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | edge_stratum=C_derived_fallback_anchor | oracle | C2 | secondary | f1 | 1 | 1 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | all | oracle | C3 | secondary | em | 3 | 0 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | all | oracle | C3 | secondary | f1 | 3 | 0 | -0.412 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | edge_stratum=B_derived_exact_anchor | oracle | C3 | secondary | em | 2 | 0 | -0.500 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | edge_stratum=B_derived_exact_anchor | oracle | C3 | secondary | f1 | 2 | 0 | -0.618 | [-1.000, -0.235] | b < a | no (exploratory) |
| 2wikimultihopqa |  | edge_stratum=C_derived_fallback_anchor | oracle | C3 | secondary | em | 1 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | edge_stratum=C_derived_fallback_anchor | oracle | C3 | secondary | f1 | 1 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | all | oracle | C4 | secondary | em | 3 | 0 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | all | oracle | C4 | secondary | f1 | 3 | 0 | -0.278 | [-1.000, 0.165] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | edge_stratum=B_derived_exact_anchor | oracle | C4 | secondary | em | 2 | 0 | -0.500 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | edge_stratum=B_derived_exact_anchor | oracle | C4 | secondary | f1 | 2 | 0 | -0.418 | [-1.000, 0.165] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | edge_stratum=C_derived_fallback_anchor | oracle | C4 | secondary | em | 1 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| 2wikimultihopqa |  | edge_stratum=C_derived_fallback_anchor | oracle | C4 | secondary | f1 | 1 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| fever |  | all | oracle | C1 | secondary | verdict_acc | 0 | 0 | - | - | no paired data | no (exploratory) |
| fever |  | edge_stratum=None | oracle | C1 | secondary | verdict_acc | 0 | 0 | - | - | no paired data | no (exploratory) |
| fever |  | all | oracle | C2 | secondary | verdict_acc | 0 | 0 | - | - | no paired data | no (exploratory) |
| fever |  | edge_stratum=None | oracle | C2 | secondary | verdict_acc | 0 | 0 | - | - | no paired data | no (exploratory) |
| fever |  | all | oracle | C3 | secondary | verdict_acc | 0 | 0 | - | - | no paired data | no (exploratory) |
| fever |  | edge_stratum=None | oracle | C3 | secondary | verdict_acc | 0 | 0 | - | - | no paired data | no (exploratory) |
| fever |  | all | oracle | C4 | secondary | verdict_acc | 0 | 0 | - | - | no paired data | no (exploratory) |
| fever |  | edge_stratum=None | oracle | C4 | secondary | verdict_acc | 0 | 0 | - | - | no paired data | no (exploratory) |
| hotpotqa |  | all | oracle | C1 | secondary | em | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| hotpotqa |  | all | oracle | C1 | secondary | f1 | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| hotpotqa |  | edge_stratum=B_derived_exact_anchor | oracle | C1 | secondary | em | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| hotpotqa |  | edge_stratum=B_derived_exact_anchor | oracle | C1 | secondary | f1 | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| hotpotqa |  | edge_stratum=None | oracle | C1 | secondary | em | 0 | 0 | - | - | no paired data | no (exploratory) |
| hotpotqa |  | edge_stratum=None | oracle | C1 | secondary | f1 | 0 | 0 | - | - | no paired data | no (exploratory) |
| hotpotqa |  | all | oracle | C2 | secondary | em | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| hotpotqa |  | all | oracle | C2 | secondary | f1 | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| hotpotqa |  | edge_stratum=B_derived_exact_anchor | oracle | C2 | secondary | em | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| hotpotqa |  | edge_stratum=B_derived_exact_anchor | oracle | C2 | secondary | f1 | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| hotpotqa |  | edge_stratum=None | oracle | C2 | secondary | em | 0 | 0 | - | - | no paired data | no (exploratory) |
| hotpotqa |  | edge_stratum=None | oracle | C2 | secondary | f1 | 0 | 0 | - | - | no paired data | no (exploratory) |
| hotpotqa |  | all | oracle | C3 | secondary | em | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| hotpotqa |  | all | oracle | C3 | secondary | f1 | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| hotpotqa |  | edge_stratum=B_derived_exact_anchor | oracle | C3 | secondary | em | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| hotpotqa |  | edge_stratum=B_derived_exact_anchor | oracle | C3 | secondary | f1 | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| hotpotqa |  | edge_stratum=None | oracle | C3 | secondary | em | 0 | 0 | - | - | no paired data | no (exploratory) |
| hotpotqa |  | edge_stratum=None | oracle | C3 | secondary | f1 | 0 | 0 | - | - | no paired data | no (exploratory) |
| hotpotqa |  | all | oracle | C4 | secondary | em | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| hotpotqa |  | all | oracle | C4 | secondary | f1 | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| hotpotqa |  | edge_stratum=B_derived_exact_anchor | oracle | C4 | secondary | em | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| hotpotqa |  | edge_stratum=B_derived_exact_anchor | oracle | C4 | secondary | f1 | 2 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| hotpotqa |  | edge_stratum=None | oracle | C4 | secondary | em | 0 | 0 | - | - | no paired data | no (exploratory) |
| hotpotqa |  | edge_stratum=None | oracle | C4 | secondary | f1 | 0 | 0 | - | - | no paired data | no (exploratory) |
| hover |  | all | oracle | C1 | secondary | verdict_acc | 0 | 0 | - | - | no paired data | no (exploratory) |
| hover |  | edge_stratum=None | oracle | C1 | secondary | verdict_acc | 0 | 0 | - | - | no paired data | no (exploratory) |
| hover |  | all | oracle | C2 | secondary | verdict_acc | 0 | 0 | - | - | no paired data | no (exploratory) |
| hover |  | edge_stratum=None | oracle | C2 | secondary | verdict_acc | 0 | 0 | - | - | no paired data | no (exploratory) |
| hover |  | all | oracle | C3 | secondary | verdict_acc | 0 | 0 | - | - | no paired data | no (exploratory) |
| hover |  | edge_stratum=None | oracle | C3 | secondary | verdict_acc | 0 | 0 | - | - | no paired data | no (exploratory) |
| hover |  | all | oracle | C4 | secondary | verdict_acc | 0 | 0 | - | - | no paired data | no (exploratory) |
| hover |  | edge_stratum=None | oracle | C4 | secondary | verdict_acc | 0 | 0 | - | - | no paired data | no (exploratory) |
| musique |  | all | oracle | C1 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| musique |  | all | oracle | C1 | secondary | f1 | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| musique |  | edge_stratum=B_derived_exact_anchor | oracle | C1 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| musique |  | edge_stratum=B_derived_exact_anchor | oracle | C1 | secondary | f1 | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| musique |  | all | oracle | C2 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| musique |  | all | oracle | C2 | secondary | f1 | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| musique |  | edge_stratum=B_derived_exact_anchor | oracle | C2 | secondary | em | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| musique |  | edge_stratum=B_derived_exact_anchor | oracle | C2 | secondary | f1 | 3 | 0 | 0.000 | [0.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| musique |  | all | oracle | C3 | secondary | em | 3 | 0 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| musique |  | all | oracle | C3 | secondary | f1 | 3 | 0 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| musique |  | edge_stratum=B_derived_exact_anchor | oracle | C3 | secondary | em | 3 | 0 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| musique |  | edge_stratum=B_derived_exact_anchor | oracle | C3 | secondary | f1 | 3 | 0 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| musique |  | all | oracle | C4 | secondary | em | 3 | 0 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| musique |  | all | oracle | C4 | secondary | f1 | 3 | 0 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| musique |  | edge_stratum=B_derived_exact_anchor | oracle | C4 | secondary | em | 3 | 0 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |
| musique |  | edge_stratum=B_derived_exact_anchor | oracle | C4 | secondary | f1 | 3 | 0 | -0.333 | [-1.000, 0.000] | inconclusive (CI contains 0; not evidence of equivalence) | no (exploratory) |

## Component attribution (relative to oracle)

```
{
  "C1 | edge_stratum=B_derived_exact_anchor": {
    "no_degradation": 6,
    "degraded_with_evidence_loss(component)": 1
  },
  "C2 | edge_stratum=B_derived_exact_anchor": {
    "no_degradation": 7
  },
  "C3 | edge_stratum=B_derived_exact_anchor": {
    "no_degradation": 5,
    "degraded_with_evidence_loss(component)": 2
  },
  "C4 | edge_stratum=B_derived_exact_anchor": {
    "no_degradation": 5,
    "degraded_with_evidence_loss(component)": 2
  },
  "C1 | edge_stratum=C_derived_fallback_anchor": {
    "no_degradation": 1
  },
  "C2 | edge_stratum=C_derived_fallback_anchor": {
    "no_degradation": 1
  },
  "C3 | edge_stratum=C_derived_fallback_anchor": {
    "no_degradation": 1
  },
  "C4 | edge_stratum=C_derived_fallback_anchor": {
    "no_degradation": 1
  },
  "C2_depends_on_agreement_passage_level": {
    "2wikimultihopqa | gold=shared_surface_cue": {
      "n": 3,
      "reported": true,
      "dep_precision": 1.0,
      "dep_recall": 0.6666666666666666,
      "caveat": "gold edges are automatically derived, not verified"
    },
    "hotpotqa | gold=same_rule": {
      "n": 2,
      "reported": false,
      "reason": "gold edges share the predictor's heuristic"
    },
    "musique | gold=shared_surface_cue": {
      "n": 3,
      "reported": true,
      "dep_precision": null,
      "dep_recall": 0.0,
      "caveat": "gold edges are automatically derived, not verified"
    }
  }
}
```

Unavailable conditions are excluded from metric denominators and counted in 'unavail'.
All numbers can be recomputed with `wsh report <run_dir>`.
