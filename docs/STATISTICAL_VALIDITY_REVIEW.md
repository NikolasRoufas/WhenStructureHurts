# Statistical validity review (revision-2, 2026-10-13)

This review extends `docs/STATISTICAL_REVIEW.md` (revision-1), which covers the original confirmatory family, the equivalence procedure and exploratory multiplicity. Here we add the new confirmatory test, the evidentiary categories used in the paper, and the remaining threats.

## 1. Evidentiary categories (used in every table and in the text)

| category | what belongs to it | multiplicity | may support a claim of |
|---|---|---|---|
| **Confirmatory 1** | six primary tests on `confirm_v1` (R1−R0, R5−R1, R4−R5 × MuSiQue, 2Wiki); protocol `CONFIRMATORY_PROTOCOL.md` | Holm over 6; equivalence ±0.02 (per-test 90 % CI rule, plus Holm-TOST) | an effect, or equivalence within ±0.02 |
| **Confirmatory 2** | contradiction lines on vs off at a fixed order, on untouched 2Wiki and HotpotQA questions (`confirm2_v1`); protocol `CONFIRMATORY_PROTOCOL_2.md` (frozen and pushed before sampling) | Holm over 2 (primary); Holm over 2 (secondary: abstention) | an effect |
| **Exploratory pilot** | all `pilot_v1` results (Protocol B, Exp0, Exp2, HotpotQA/HoVer/FEVER contrasts) | none | hypotheses only |
| **Post-hoc exploratory** | revision-1/2 interventions on already-analysed questions (fixed-order controls, targeted relabel, filler), the prompt variants, the retrieved-evidence sample, the second reader, every stratum and transition table | none | patterns, with intervals; never "confirmed" |

The paper labels each table with its category. Results from different categories are never pooled.

## 2. Confirmatory 2: result and checks

**Design checks.**
- **Chronology.** The protocol commit `6648eef` (00:39 UTC) was pushed to GitHub before the sample (`6ccdc8b`) and before generation (run start 00:52 UTC).
- **Deviations.** One deviation, logged before any generation: a type rebalancing in the 2Wiki sample, because the inference type had only 217 eligible questions.
- **Analysis code.** It ran unchanged. It was code-checked once on an earlier exploratory run, and that output was deleted.
- **Prompt identity.** Prompts are byte-identical exactly when no contradiction line is rendered (asserted in the code): 1,110 2Wiki and 2,505 HotpotQA questions.
- **Errors.** 0 generation errors in 12,800 records.

**Results (EM, R4P_FO − R4P_FO_NC; paired percentile bootstrap, 2,000 resamples, seed 0).**

| | 2Wiki | HotpotQA |
|---|---|---|
| primary population (≥ 1 contradiction line) | 1,490 of 2,600 | 1,295 of 3,800 |
| **primary ΔEM** | **−0.077 [−0.095, −0.061]**, p_Holm < 0.001 | **−0.053 [−0.067, −0.039]**, p_Holm < 0.001 |
| decision | confirmed | confirmed |
| secondary ΔAbstention | +0.089 [+0.072, +0.104], p_Holm < 0.001 | +0.076 [+0.061, +0.092], p_Holm < 0.001 |
| secondary ΔEM, all questions | −0.044 [−0.054, −0.035] | −0.018 [−0.023, −0.013] |
| descriptive: Δaccuracy among questions answered under both conditions | −0.055 [−0.076, −0.036] (n = 946) | −0.023 [−0.037, −0.010] (n = 1,025) |
| descriptive: transitions off → on (C→A / C→W / A→C / W→C) | 67 / 73 / 4 / 21 | 46 / 37 / 1 / 13 |

"p < 0.001" means no bootstrap resample reached zero (resolution 1/2,000).

**Realised power.**
- The observed SDs of the paired difference are about 0.33 (2Wiki) and 0.26 (HotpotQA). The protocol planned for 0.31.
- Prevalence was below plan for HotpotQA: 34 % with at least one line, against an assumed 44 %, so n = 1,295 instead of about 1,600.
- Power to detect the pre-specified −0.025 at α = 0.025 was about 0.75 (2Wiki) and about 0.88 (HotpotQA).
- The observed effects are 2–3 times that size, so the conclusions do not depend on power.

**Interpretation.**
- The fixed-order contradiction effect, found exploratorily on `confirm_v1`, replicates as a **confirmatory** result on fresh questions and on a dataset (HotpotQA) that played no role in generating the hypothesis.
- On these questions the effect is **not purely abstention**. About half of the lost correct answers become abstentions and about half become wrong answers. Accuracy among questions answered under both conditions also drops.
- This refines the exploratory claim "abstention is the channel" to "abstention is the main but not the only channel".

## 3. Threats reviewed

| threat | assessment |
|---|---|
| Question-level independence | Questions are the unit. Multi-hop datasets contain questions about the same entity, so mild clustering is possible. A cluster bootstrap that resamples groups of questions sharing their first evidence title (2,000 resamples, seed 0) barely changes the intervals: Confirmatory 2, 2Wiki [−0.094, −0.060] (1,470 clusters) and HotpotQA [−0.068, −0.039] (1,267); Confirmatory 1, 2Wiki R1−R0 [−0.030, −0.005] (3,086) and MuSiQue R1−R0 [−0.014, +0.013] (1,010). This is a robustness check, not a test. |
| Identical prompts | Always counted. Primary estimands either exclude identical-prompt pairs by an input-only rule (Confirmatory 2) or include them as zeros, with the informative estimate also reported (Confirmatory 1). |
| Availability bias | None in the confirmatory tests: every question has both conditions (0 unavailable, 0 errors). In the retrieved-evidence study all 500 + 500 questions are paired. |
| Selection on outcomes | None. Strata are defined by inputs (contradiction lines, retrieval outcome), never by answers. "Restored" strata in the annotation package select on outcomes deliberately, for prioritising human labels; they are not used for any estimate. |
| Dataset heterogeneity | Effects are reported per dataset, never pooled. The contradiction effect has the same sign on all four datasets (MuSiQue, 2Wiki and retrieved-evidence exploratory; 2Wiki and HotpotQA confirmatory), with sizes between −0.022 and −0.077 depending on the population. |
| Exploratory multiplicity | About 40 exploratory contrasts and many strata, uncorrected. We highlight only patterns that recur across datasets, and the main one is now confirmed. Smaller exploratory findings (e.g. predicted order +0.018 on MuSiQue; the fallback-anchor stratum of R5−R1 on MuSiQue, −0.040) are reported as unconfirmed. |
| Effect sizes | Confirmatory 1: 2Wiki sentence items −0.017, about 4 % relative to EM 0.41. Confirmatory 2: −0.053 to −0.077, about 13–19 % relative within the affected population. |
| Equivalence | Holm-TOST agrees with the per-test rule (`STATISTICAL_REVIEW.md` §2). Non-significant results are never called equivalence unless a test says so. |
| Model-family interaction | Descriptive only (two readers). See `docs/FINAL_RESEARCH_ASSESSMENT.md` for the Mistral comparison; no test of "model family" is claimed. |
| Prompt-tuning risk | Each prompt variant was written once, before its run. No variant was revised after outcomes. |
| Sample-size inflation | None: both confirmatory samples were fixed in advance, with no top-up. |

## 4. Remaining recommendations

1. The prompt dependence of the mechanism (abstention instruction) and the second reader are post-hoc. A confirmatory test across readers would need a new frozen protocol and further compute.
2. Whether the harmful lines are *false* (rather than merely asserted) needs the human labels. The confirmatory result is about showing NLI-predicted contradiction lines, whatever their truth.
