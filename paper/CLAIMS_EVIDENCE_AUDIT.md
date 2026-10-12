# Claims → evidence audit

Every empirical statement in `paper/main.tex` is mapped to the file and row it comes from.

**Where the files live:**
- All files are under `research_outputs/` (copied from `/data/roufas/wsh_campaign/research_outputs/` on the server).
- `analysis/provenance.json` holds the sha256 of every input run file (manifests, configs, predictions).
- `experiments/runs.json` maps each label to its run directory.

**Run labels:**

| label | experiment | run directory | stage |
|---|---|---|---|
| `A_exp1` | Exp1, focused pilot | `gpu_pilot/exp1/20261012-095222_797a0644` | exploratory |
| `A_exp0` | Exp0, focused pilot | `gpu_pilot/exp0/20261012-102947_8dad35aa` | exploratory |
| `C_exp1` | Exp1, expanded pilot (350 questions; the 200 focused ones from cache, so identical) | `gpu_pilot/exp1/20261012-120617_d4f7f61d` | exploratory |
| `C_exp2` | Exp2 | `gpu_pilot/exp2/20261012-122150_20896430` | exploratory |
| `C_exp3` | Exp3: every question unavailable by design | `gpu_pilot/exp3/20261012-183018_f702b552` | — |
| `F_exp1` | confirmatory Exp1 | `full/exp1/20261012-125639_49dfe135` | confirmatory |

Status: **verified** means the number in the paper equals the number in the source file (checked 2026-10-12).

## Abstract and introduction

| claim | source | status |
|---|---|---|
| 4,976 questions (1,744 MuSiQue + 3,232 2Wiki), disjoint from the pilot | `configs/question_sets/confirm_v1.json` (sha256 `d7b49cb3…`); overlap check in `docs/CONFIRMATORY_PROTOCOL.md` §9 | verified |
| Graph order and derived relations: no detectable change; on 2Wiki equivalent to zero within ±0.02 | `F_exp1_contrasts.csv`, rows `setting=A, edge_stratum=all, metric=em, contrast ∈ {R5-R1, R4-R5}`: `p_holm` 0.535; `equivalent_within_0.02`: 2Wiki True/True, MuSiQue False/False | verified |
| Sentence items lower 2Wiki EM by 1.7 points, 95 % CI [−2.9, −0.5] | `F_exp1_contrasts.csv`, 2Wiki R1-R0 em: delta −0.0167, ci [−0.0288, −0.0046], p_holm 0.018 | verified |
| "almost entirely through more frequent abstention" | `F_exp1_decomposition_exploratory.csv`, 2Wiki R1-R0: both_answered +0.0012, one-abstains −0.0179, 250/81 | verified (exploratory analysis) |
| Predicted relations lower EM by 3.6 and 4.5 points | `F_exp1_contrasts.csv`, R4P-R4 em: 2Wiki −0.0359, MuSiQue −0.0447 | verified (secondary contrast) |
| Loss concentrated where compatible facts are marked contradictory | `F_exp1_r4p_relations_exploratory_paired.csv` | verified (exploratory analysis) |
| Structured formats keep 15–20 pp fewer facts under a budget | `C_exp1_protocol_accounting.csv`, budget content:1.0, per_representation: R0 0.834/0.806 vs R1/R4/R5 0.632–0.654 (2Wiki/MuSiQue); differences 0.152–0.202 | verified (pilot) |
| Teaser/trailer example | `F_exp1` predictions: 2Wiki question "Did the movies Ride A Crooked Trail and The Glassworker, originate from the same country?"; R4 answer "no" (EM 1), R4P "insufficient evidence" | verified |
| "It stars Anne Hathaway …" example | rendering of smoke question `musique/2hop__219456_87295` (excluded from all runs) by the experiment code | verified |

## Section 5 (setup)

| claim | source | status |
|---|---|---|
| Batched bf16 changed 3 of 8 7B outputs; unbatched outputs identical across runs | `docs/gpu_preflight/gpu0_7b.json` (`batched_vs_unbatched_identical` 5/8, `unbatched_run_to_run_identical` 8/8) | verified |
| Confirmatory n from the pilot variance rule | `A_exp1_sample_size.csv` (`n_required` max per dataset: 1,744 and 3,232) | verified |
| MuSiQue hop strata 687/686/371; 808 per 2Wiki type | `confirm_v1.json` `details.*.strata_counts` | verified |

## Section 6 (results)

| claim | source | status |
|---|---|---|
| Table 2 (confirmatory) | `tables/tab_confirmatory.csv` ← `F_exp1_contrasts.csv` | generated |
| 44,784 records, 0 errors, information equivalence verified | `analysis/run_summary.json` `F_exp1` (`n_generation_error` 0, `n_pipeline_error` 0; information-equivalence violations would be pipeline errors) | verified |
| MuSiQue R1−R0 −0.001 [−0.014, +0.014], equivalent | `F_exp1_contrasts.csv` | verified |
| Identical pairs 1,858 / 522 / 879 | `F_exp1_contrasts.csv` `n_identical_evidence` | verified |
| Informative estimates −0.019, −0.016, +0.008 | `F_exp1_contrasts.csv` `informative_delta` | verified |
| Table 3 (decomposition) | `tables/tab_decomposition_main.csv` ← `F_exp1_decomposition_exploratory.csv` | generated |
| 710 of 1,744 and 529 of 3,232 answered under neither R0 nor R1 | `F_exp1_decomposition_exploratory.csv` `n_neither_answered` | verified |
| Secondary: R4P−R4 −0.036 [−0.045, −0.027] / −0.045 [−0.060, −0.030]; coverage −0.061 / −0.089; R2−R1 −0.024 / +0.013; R3−R5 −0.004 / −0.007 | `F_exp1_contrasts.csv` | verified |
| Pilot budget summary: R0 keeps 0.83/0.81, others 0.62–0.65; overhead 2.5–4×; answer present 0.85 vs 0.64–0.66 (2Wiki) | `C_exp1_protocol_accounting.csv` (per_representation, 1.0×) | verified |
| Exp0: claims/paths ≈ reranked passages at ~3× tokens; B4 −0.15 / −0.09 | `A_exp0_absolute.csv`, `A_exp0_contrasts.csv` (B4-B1 em: 2Wiki −0.15 [−0.23, −0.07], MuSiQue −0.09 [−0.15, −0.04]) | verified |
| Exp2: P4 negative in every QA cell, up to −0.16; P2 2Wiki −0.10 [−0.18, −0.01] | `C_exp2_sensitivity.csv` (P4 at rates 0.2 and 0.4, R1 and R4, MuSiQue/2Wiki/HotpotQA: all negative; P2 2Wiki R4 0.4: −0.0986 [−0.183, −0.014], n=71) | verified |
| Figure 2 | `figures/fig5_contrasts_pilot_vs_confirmatory.pdf` ← `C_exp1_contrasts.csv`, `F_exp1_contrasts.csv` | generated |

## Section 7 (discussion)

| claim | source | status |
|---|---|---|
| 9,688 CONTRADICTS lines in 3,232 2Wiki prompts; ≥1 in 63 % | `F_exp1_r4p_relations_exploratory.csv` (`lines_CONTRADICTS` 9,688; has-contradiction subset 2,034 / 3,232 = 62.9 %) | verified |
| Zhou kings example | `F_exp1` predictions: 2Wiki "Who is the paternal grandfather of King Kuang Of Zhou?" | verified |
| Abstention 0.32 → 0.42 (2Wiki), 0.50 → 0.64 (MuSiQue); EM 0.33 → 0.28 | `F_exp1_r4p_relations_exploratory_paired.csv` | verified |
| 7 of the 12 pilot wins of R0 over R1 are R1 abstentions | `A_exp1_discordant_examples.json` key `2wikimultihopqa:R1-R0` (manual reading; `research_outputs/reports/focused_pilot_notes.md`) | verified |
| 1.5 to 3 times as many answer-bearing facts dropped | `C_exp1_protocol_accounting.csv` (`answer_bearing_dropped`: 2Wiki 0.11 vs 0.33–0.34; MuSiQue 0.19 vs 0.28–0.35) | verified |
| Pilot −0.07 vs confirmatory −0.017 | `C_exp1_contrasts.csv`, `F_exp1_contrasts.csv` | verified |

## Not claimed (intentionally)

- No component-attribution result (Exp3: all unavailable, `C_exp3`).
- No relation precision or recall.
- No citation-faithfulness analysis.
- No adaptive-selector result.
- No P7 result.
- No human-verified structure.
