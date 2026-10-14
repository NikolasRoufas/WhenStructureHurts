# Claims → evidence audit (revision-2, 2026-10-14)

Every empirical statement in `paper/main.tex` is mapped to the file and row it comes from. **Verified** means the number in the paper equals the number in the source file (checked 2026-10-13). Original-campaign files are under `research_outputs/analysis/`, revision files under `research_outputs/revision/`. Run directories, configs and prediction hashes are in `docs/REPRODUCIBILITY_CHECKLIST.md`; the independent recomputation of the original claims is `research_outputs/revision/audit/claims_check.csv` (all reproduced).

Labels: `F_exp1` confirmatory 1; `C2` confirmatory 2 (`full/exp1/20261013-005305_1ded82bb`); `R2_ctrl` (`revision/exp1/20261013-022332_df336d0b`), `R2_cons` (`revision/exp1/20261013-030726_a3469c77`), `R2_mistral` (`revision/exp1/20261013-033400_145ae2a1`) revision-2 runs; `C_exp1`, `C_exp2`, `C_exp0`, `A_exp0` pilot; `R_ctrl`, `R_retr`, `R_noabst` revision runs (exploratory).

## Abstract and Introduction

| claim | source | status |
|---|---|---|
| 4,976 questions (1,744 MuSiQue + 3,232 2Wiki), disjoint from the pilot | `configs/question_sets/confirm_v1.json`; `docs/CONFIRMATORY_PROTOCOL.md` §9 | verified |
| Order and derived relation lines: no detectable effect; on 2Wiki equivalent to zero within ±0.02 | `F_exp1_contrasts.csv` (R5−R1, R4−R5; `p_holm` 0.535; equivalence 2Wiki yes/yes, MuSiQue no/no) | verified |
| Sentence items lower 2Wiki EM by 1.7 points [−2.9, −0.5], mostly through abstention | `F_exp1_contrasts.csv` (−0.0167, p_Holm 0.018); `revision/analysis/F_exp1_transitions.csv` (ΔAbst +0.052, Δacc given both answered +0.002) | verified |
| Contradiction lines cost 3.3 points on both datasets, mainly by abstention | `revision/controls/relation_control_effects.csv`, R4P_FO−R4P_FO_NC: 2Wiki −0.033 [−0.042, −0.025], MuSiQue −0.033 [−0.043, −0.023]; ΔAbst +0.061 / +0.062 | verified (exploratory) |
| Order and line count explain almost none | same file: R5P−R5 +0.002 / +0.018; R4N_FO−R5 +0.007 / −0.015 | verified (exploratory) |
| Replicated on 1,000 fresh questions with real retrieval | `revision/retrieval/retrieval_contrasts.csv` (A): R4P−R4 −0.036 / −0.030; contradiction lines on−off −0.022 / −0.024 | verified (exploratory) |
| Without the abstention instruction most differences shrink toward zero | `revision/noabst/noabst_contrasts.csv`: R1−R0 −0.004 [−0.026, +0.018], R4P−R4 −0.017 [−0.035, 0.000] | verified (exploratory) |
| Teaser/trailer example | `F_exp1` predictions, 2Wiki "Did the movies Ride A Crooked Trail and The Glassworker…": R4 correct, R4P "insufficient evidence" | verified |
| "It stars Anne Hathaway …" | rendering of the excluded prompt-development question `musique/2hop__219456_87295` | verified |

## §4–5 Framework and setup

| claim | source | status |
|---|---|---|
| Batched bf16 changed 3 of 8 outputs; unbatched identical | `docs/gpu_preflight/gpu0_7b.json` | verified |
| n from the pilot variance rule; hop strata 687/686/371; 808 per 2Wiki type | `A_exp1_sample_size.csv`; `confirm_v1.json` strata | verified |
| Retrieval sample: 500 + 500, seed 3, disjoint | `configs/question_sets/retr_v1.json` (sha256 `8c32d7ed…`); 0 overlap with `configs/excluded_revision.json` | verified |
| Prompt-factor subset: 1,000 2Wiki, seed 4 | `configs/question_sets/confirm_v1_2wiki_sub1000.json` | verified |
| About 12 GPU-hours | `docs/REVISION_EXPERIMENT_LOG.md` (11.99) | verified |
| Holm-TOST agrees with the per-test rule | `docs/STATISTICAL_REVIEW.md` | verified |

## §6 Results

| claim | source | status |
|---|---|---|
| Table 2; 44,784 records, 0 errors | `F_exp1_contrasts.csv`; `analysis/run_summary.json` | verified |
| R5 = R1 for 1,858 of 3,232 2Wiki questions | `F_exp1_contrasts.csv` `n_identical_evidence` | verified |
| 2Wiki R1−R0: abstention +5.2 [4.1, 6.3]; acc. given both answered +0.002 [−0.013, +0.017]; new abstentions on correct 87, on wrong 163 | `revision/analysis/F_exp1_transitions.csv` | verified |
| Derived relation lines: acc. given both answered +0.014 [+0.005, +0.024], abstention +1.1 | same | verified |
| R0 leaves 47 % MuSiQue and 19 % 2Wiki unanswered | `F_exp1_absolute.csv` R0 coverage 0.530 / 0.811 | verified |
| R4P−R4 −3.6 (2Wiki) / −4.5 (MuSiQue) | `F_exp1_contrasts.csv` | verified |
| Typed vs neutral labels 3.7 / 3.0 | `relation_control_effects.csv` R4P_FO−R4N_FO | verified |
| Typed→neutral relabelling with no contradiction line: −0.003 on both (−0.0025 / −0.0027); contradiction lines on−off with 1–2 lines: −0.069 / −0.053 (5–7 points) | `revision/controls/relation_control_strata.csv` (R4P_FO−R4N_FO and R4P_FO−R4P_FO_NC, `n_contra_lines` strata) | verified |
| C→A 89 vs A→C 9 (2Wiki); 52 vs 2 (MuSiQue) | `revision/controls/controls_transitions.csv` | verified |
| Retrieval: complete-retrieval stratum R4P−R4 −0.094 / −0.042; none stratum 0 | `retrieval_contrasts.csv` strata | verified |
| R1−R0 retrieval −0.026 [−0.054, +0.002] (2Wiki), +0.014 (MuSiQue) | `retrieval_contrasts.csv` | verified |
| R5 = R1 for 498/500 2Wiki | `retrieval_contrasts.csv` `n_identical` | verified |
| Prompt: abstention 20–33 % → < 1 %; EM +8 to +13 points | `noabst_contrasts.csv` absolute rows (0.202–0.328 → 0.006–0.009); prompt-effect rows +0.078 to +0.128 | verified |
| Interactions +0.019, CIs touch or include 0 | `noabst_contrasts.csv` | verified |

## §7 Discussion

| claim | source | status |
|---|---|---|
| ≥ 1 contradiction pair in 63 % of 2Wiki prompts | `F_exp1_r4p_relations_exploratory.csv` (2,034 / 3,232) | verified |
| Triage: different entities 40 %, different dates 20 % | `revision/contradictions/contradictions_summary.json` (3,857 / 1,962 of 9,750 pairs) | verified (heuristic, not a judgement) |

## Appendix

Tables 5–11 and Figures 2, 3, 5 come from the original campaign files listed in the previous audit (`F_exp1_*`, `C_exp1_*`, `C_exp2_*`, `A_exp0_*`) and were re-verified by `scripts/audit/verify_claims.py`. Tables 12–18 and Figure 4 are generated by `scripts/revision/paper_assets.py` from `research_outputs/revision/` and carry their source in the caption.

## Revision-2 claims (abstract, introduction, §4–8)

Revision-2 sources are under `research_outputs/revision2/`. In the code, R4P_FO_PAD is `R4P_FO_NCPAD`.

| claim | source | status |
|---|---|---|
| Relabelling only CONTRADICTS lines recovers 3.7 / 3.3 points; filler recovers 4.2 / 3.7; removal 3.3 / 3.3 | `r2/controls2.csv` (`R4P_FO_CN>R4P_FO`, `R4P_FO_NCPAD>R4P_FO`, `R4P_FO_NC>R4P_FO`, stratum all) | verified (exploratory) |
| Relabelling other labels adds nothing (0.000 / +0.003) | `r2/controls2.csv` `R4N_FO>R4P_FO_CN` | verified |
| Relabelling restored 141 correct 2Wiki answers (80 from abstentions), lost 21; MuSiQue 62 and 4 | `R4P_FO_CN>R4P_FO` transitions (C→A 80, C→W 61, A→C 1, W→C 20; MuSiQue 49/13/1/3) | verified |
| Filler 7 vs 8–9 tokens | Qwen tokenizer check (`docs/REVISION2_PROTOCOL.md` §1) | verified |
| Confirmatory 2: 2Wiki −0.077 [−0.095, −0.061], HotpotQA −0.053 [−0.067, −0.039], p_Holm < 0.001; n 1,490/2,600 and 1,295/3,800; abstention +0.089 / +0.076; all questions −0.044 / −0.018; acc given both answered −0.055 / −0.023; about half C→A, half C→W | `confirm2/confirm2_summary.json`, `confirm2_results.csv` | verified (**confirmatory**) |
| 6,400 untouched questions; protocol frozen and published before sampling | `docs/CONFIRMATORY_PROTOCOL_2.md` (`6648eef`), `confirm2_v1.json` (`6ccdc8b`), run start 00:52 UTC | verified |
| 34–63 % of prompts with ≥ 1 contradiction pair | HotpotQA 1,295/3,800 = 34 %; 2Wiki `confirm_v1` 2,034/3,232 = 63 % | verified |
| Mistral: contradiction lines −0.034 / −0.015 (EM), −0.050 / −0.033 (lenient), abstention +5–6 points; predicted lines worse than derived on both datasets | `r2/reader2.csv` | verified (exploratory) |
| Mistral: R1−R0 −0.001 (2Wiki), +0.022 [+0.012, +0.033] (MuSiQue), abstention −4.6 points | `r2/reader2.csv` | verified |
| Abstention policy: stricter guidance R4P−R4 −0.033, R1−R0 −0.032; abstention +10 to +15; without the option −0.004 / −0.017, wrong answers 33–40 % → 51–52 %; 12–19 more points of wrong answers | `r2/prompt3.csv` (restricted to the 1,000 questions) | verified |
| Anchor strata: no effect for exact- or fallback-anchored edges | `serialization/anchor_strata.csv` (R4−R5 CIs all include 0) | verified |
| Retrieved evidence: equal-budget retention 82–84 % vs 63–68 % | `retrieval_costs.csv` (facts kept, Protocol B) | verified |
| About 20 GPU-hours | `docs/REVISION_EXPERIMENT_LOG.md` (19.6) | verified |

## Not claimed (intentionally)

- No human-verified relation precision or recall; no human judgement of the contradiction pairs.
- No component attribution (Exp3 not run).
- No claim about model families in general (two readers only).
- No confirmatory status for any revision analysis other than confirmatory protocol 2.
- No conclusion about the original EG-RAG system from our reconstruction (B4).
