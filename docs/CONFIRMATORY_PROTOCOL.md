# Confirmatory protocol (frozen 2026-10-12, before the confirmatory sample was drawn)

**Status: FROZEN.** This file was written and committed:
- before the confirmatory question set was sampled, and
- before any generation on it.

The sample is drawn by `wsh questions freeze` from `configs/question_sets/confirm_v1.spec.yaml`. Any later change goes into §9 with its date and reason.

## 1. What is confirmed, and what is not

The exploratory pilot (`docs/PILOT_PROTOCOL.md`; focused pilot `results/analysis/FOCUSED_PILOT_REPORT.md`) produced:
- the variance estimates used in §4;
- no hypothesis-generating change to the design.

This run tests the **six pre-specified primary tests** of PILOT_PROTOCOL §2. They are the same contrasts, metric, protocol and datasets that were frozen before the pilot. Nothing here was added or selected after seeing pilot outcomes.

| # | contrast (b − a) | isolates | datasets |
|---|---|---|---|
| C-1 | R1 − R0 | passage vs sentence-item presentation of identical text | MuSiQue, 2WikiMultiHopQA |
| C-2 | R5 − R1 | graph-derived ordering of identical items | MuSiQue, 2WikiMultiHopQA |
| C-3 | R4 − R5 | explicit derived relation lines at fixed order | MuSiQue, 2WikiMultiHopQA |

**Not confirmatory (remain exploratory, pilot-level only):**
- Protocol B;
- Exp0 and Exp2;
- HotpotQA, HoVer and FEVER;
- the R2, R3 and R4P contrasts;
- edge strata;
- subgroups;
- any analysis suggested by the pilot.

Structure is **derived** from dataset annotations (strata B and C), not human-verified. A confirmed C-2 or C-3 effect would therefore be an effect of *derived* structure.

## 2. Hypotheses (two-sided)

For each of the six tests, H0: the mean paired question-level EM difference is 0.
- Rejecting H0 says that the representation change affects EM for this generator on this dataset.
- Failing to reject is reported as inconclusive, not as equivalence.

## 3. Procedure (unchanged from PILOT_PROTOCOL §5 and §7)

- **Generator and settings:** Qwen2.5-7B-Instruct `a09a3545`, bf16, greedy decoding, `max_new_tokens` 64, batch size 1, physical GPU 0. Prompt template `qa-v2`; information equivalence checked per question.
- **Evidence:** gold evidence, scope `gold_passages`, **Protocol A** only.
- **Representations:** all seven Protocol A representations are generated (R0, R1, R2 with seeds 0/1/2, R3, R4, R4P, R5), so the secondary contrasts are available descriptively. Only C-1 to C-3 are tested.
  - Protocol B is **not** run in this stage. That is a compute decision taken before any confirmatory generation: Protocol B is outside the confirmatory family.
- **Metric:** question-level exact match (SQuAD normalisation, maximum over aliases), unanswered = 0, all attempted questions in the denominator.
- **Test:** paired percentile bootstrap of the mean difference (2,000 resamples, seed 0), with a two-sided bootstrap p-value.
- **Multiplicity:** Holm correction over the 6 tests at family-wise α = 0.05. This is applied automatically by `wsh.evaluation.reporting.contrasts` at stage `full` for primary contrasts on the primary datasets, Protocol A, n ≥ 100.
- **Always reported with each test:**
  - n paired;
  - identical-evidence pairs;
  - the informative-pairs estimate;
  - the coverage difference;
  - the exact McNemar test (secondary).
- **Equivalence (secondary, pre-specified margin ±0.02 EM):** reported only as "the 90 % CI lies inside ±0.02" or not. It is never inferred from a non-significant test.
- **Exclusions:** none on outcomes. Pipeline errors and unavailable conditions are counted. If pipeline errors exceed 2 % of records in any primary condition, the run is reported as failed and not interpreted.

## 4. Sample size (PILOT_PROTOCOL §8.3)

The target is 80 % power for |ΔEM| = 0.03 at two-sided α = 0.05/6, using the pilot SD of paired question-level differences inflated by 20 % (`research_outputs/analysis/A_exp1_sample_size.csv`). The per-dataset n is the maximum over the three contrasts.

| dataset | n required (max over C-1..C-3) | stratification |
|---|---|---|
| MuSiQue | 1,744 (C-1) | hop count |
| 2WikiMultiHopQA | 3,232 (C-1) | question type |

**Feasibility:**
- The eligible pools, after excluding the 15 smoke and 350 pilot questions, are 2,314 (MuSiQue) and 11,389 (2Wiki).
- Estimated generation: about 4,976 questions × 9 variants. The work is generator-bound at about 0.45 s per uncached generation (measured), plus about 0.11 s per record of overhead.
- That comes to roughly 4–6 GPU-hours on one RTX 5000 Ada. This is an estimate; the actual figure is recorded in `docs/RUN_STATUS.md`.

## 5. Question set

- Spec: `configs/question_sets/confirm_v1.spec.yaml`, seed **2**, development split, the same eligibility rules as the pilot.
- Exclusions: `configs/excluded_confirmatory.json` = the 15 smoke questions + all 350 questions of `pilot_v1.json`.
  - `configs/excluded_questions.json` itself is left unchanged so that the pilot runs keep working.
- Stage `full` additionally refuses any question of any `pilot_*.json` file (`assert_no_excluded`), so overlap is checked twice.
- The frozen file's sha256 is recorded in §9 when it is created.

## 6. Configuration

- `configs/confirm.yaml`, stage `full`.
- Requires `WSH_COMPUTE_AUTHORIZED=1` and `--authorized-compute`.
- Run with `scripts/campaign/run.sh exp1 configs/confirm.yaml`, which checks the physical GPU first.

## 7. Analysis

`scripts/analysis/build.py` on the completed run.
- Confirmatory results are the six rows with `confirmatory = True` and their `p_holm`.
- Everything else in the output is descriptive.

## 8. Independence statement

The confirmatory questions are disjoint from every question whose output was seen during design, prompt development or the pilot. The design was fixed before the pilot. They are **not** an independent replication in the sense of a different generator, dataset or team:
- The generator, prompt and datasets are the same as in the pilot.
- Generalisation beyond Qwen2.5-7B-Instruct and these two datasets is not tested.

## 9. Deviations and records

| date | entry |
|---|---|
| 2026-10-12 | Protocol frozen (this file). |
| 2026-10-12 | Sample frozen: `configs/question_sets/confirm_v1.json` sha256 `d7b49cb3771728821266401ecf543cdab33b1a84015bf852fdda8e18b69d5256`. MuSiQue 1,744 (hop 2/3/4: 687/686/371; only 371 eligible 4-hop questions remain, so the round-robin filled the other strata), 2Wiki 3,232 (808 per type). Overlap with pilot and smoke questions: 0 (checked by uid). No generation yet. |
