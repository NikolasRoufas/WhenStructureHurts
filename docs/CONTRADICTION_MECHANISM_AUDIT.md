# Contradiction-mechanism audit (revision-1, exploratory)

**Question.** The draft attributed the R4P−R4 drop (−0.036 on 2Wiki, −0.045 on MuSiQue, confirmatory sample, secondary contrast) to spurious CONTRADICTS lines that make the reader abstain. That claim rested on a subset split by "contradiction line present". R4P−R4, however, also changes the item order and the number of lines. We tested the mechanism with fixed-order interventions.

**Status.** Every analysis here was designed after the R4P−R4 result was seen, and runs on the already-analysed `confirm_v1` questions. The contrasts are *interventions*: the manipulated factor is the only difference between two prompts for the same question, on identical facts. They therefore estimate the effect of that factor on these questions for this reader. They are not confirmations and are not multiplicity-corrected.

**Run.** `results/revision/exp1/20261012-200925_a2e6e3a8`, config `configs/revision_relation_controls.yaml`, commit `ceb8802`.
- 39,808 records, 0 errors, 1.0 GPU-hour.
- R4, R4P and R5 were served from the cache with byte-identical prompts, so the predicted relations reproduce exactly.
- Outputs: `research_outputs/revision/controls/`, produced by `scripts/revision/contradictions.py effects` and `transitions.py`.

## 1. Factorial controls (paired, question-level, 95 % bootstrap CIs, 2,000 resamples)

Δ is the first-named condition minus the second (difference in EM, or in the abstention rate). "Identical" counts byte-identical prompt pairs.

| contrast (first − second) | factor isolated | 2Wiki ΔEM (n = 3,232) | 2Wiki ΔAbst | MuSiQue ΔEM (n = 1,744) | MuSiQue ΔAbst |
|---|---|---|---|---|---|
| R4P_FO − R4P_FO_NC | contradiction lines present vs removed (derived order) | **−0.033 [−0.042, −0.025]** (identical 1,198) | +0.061 [0.052, 0.071] | **−0.033 [−0.043, −0.023]** (identical 734) | +0.062 [0.049, 0.075] |
| R4P − R4P_NC | the same, at the predicted order | −0.035 [−0.043, −0.026] | +0.061 | −0.041 [−0.051, −0.031] | +0.061 |
| R4P_FO − R4N_FO | relation labels vs neutral `RELATED_TO`, same pairs and line count | **−0.037 [−0.045, −0.029]** | +0.056 | **−0.030 [−0.040, −0.020]** | +0.048 |
| R4N_FO − R5 | neutral lines vs none (line count and overhead only) | +0.007 [−0.003, +0.017] | +0.019 [0.010, 0.029] | −0.015 [−0.026, −0.004] | +0.038 [0.025, 0.052] |
| R5P − R5 | predicted vs derived order, no lines | +0.002 [−0.001, +0.005] (identical 3,057) | −0.003 | **+0.018 [+0.006, +0.031]** (identical 704) | +0.003 |
| R4P − R4P_FO | predicted vs derived order, predicted lines | 0.000 [−0.003, +0.003] | −0.003 | +0.010 [−0.002, +0.023] | −0.001 |
| R4P_FO − R4 | predicted vs derived lines, fixed order | −0.036 [−0.045, −0.027] | +0.064 | −0.055 [−0.068, −0.043] | +0.089 |
| R4P − R4 | original contrast (order + lines) | −0.036 [−0.045, −0.027] | +0.061 | −0.045 [−0.060, −0.029] | +0.089 |

**Reading:**
1. **Order is not the cause.** Recomputing the order from the predicted graph changes nothing on 2Wiki (the orders are almost always identical) and *helps* slightly on MuSiQue (+0.018). The original R4P−R4 drop therefore comes from the relation lines, not the order.
2. **Line count and overhead explain little.** Neutral lines at the same pairs and count cost nothing on 2Wiki (+0.007, CI includes 0) and 0.015 on MuSiQue. On both datasets they raise abstention by 2–4 points.
3. **The relation labels carry the effect.** At equal pairs and line count, typed predicted labels versus neutral labels cost 3.0–3.7 points. Removing only the CONTRADICTS lines costs the same 3.3 points.
4. **The effect is specific to contradiction lines.** In questions whose predicted block has *no* contradiction line, relabelling the other predicted lines (SUPPORTS, DUPLICATES, DEPENDS_ON, SUPERSEDES) to neutral changes EM by −0.003 [−0.010, +0.004] (2Wiki) and −0.003 [−0.014, +0.008] (MuSiQue).

## 2. Stratification (contradiction-line removal R4P_FO − R4P_FO_NC)

| stratum | 2Wiki n | 2Wiki ΔEM | 2Wiki ΔAbst | MuSiQue n | MuSiQue ΔEM | MuSiQue ΔAbst |
|---|---|---|---|---|---|---|
| 0 contradiction lines | 1,198 | 0 (identical prompts) | 0 | 734 | 0 (identical) | 0 |
| 1–2 lines | 1,015 | −0.069 [−0.089, −0.049] | +0.088 | 660 | −0.053 [−0.073, −0.033] | +0.094 |
| 3–5 lines | 577 | −0.050 [−0.075, −0.024] | +0.137 | 257 | −0.039 [−0.066, −0.016] | +0.132 |
| 6+ lines | 442 | −0.020 [−0.043, +0.002] | +0.066 | 93 | −0.129 [−0.194, −0.065] | +0.129 |

- **By question type and hop count** (2Wiki types; MuSiQue hops), every stratum is negative. On MuSiQue the effect grows with hops: 2-hop −0.025, 3-hop −0.036, 4-hop −0.040. On 2Wiki it is largest for inference and bridge-comparison questions (abstention +0.10 / +0.08) and smallest for comparison questions.
- **Dose-response is not monotone on 2Wiki** (6+ lines: −0.020). One plausible reason is that prompts with many contradiction lines belong to questions the reader already abstains on more often. We do not interpret it further.
- **The pre-planned OLS of the paired difference** on contradiction lines, other-line difference and token difference is **not interpretable**: the three predictors are nearly collinear (removing contradiction lines changes all three together). The coefficients are in `relation_control_effects.csv` for transparency, but we do not use them. Stratification by contradiction-line count is the analysis we report.

## 3. Outcome transitions (removal contrast)

States: C correct, W wrong, A unanswered.

| | C→A | A→C | C→W | W→C | W→A | A→W | Δ accuracy among questions answered under both |
|---|---|---|---|---|---|---|---|
| 2Wiki: contradiction lines added | 89 | 9 | 64 | 36 | 137 | 20 | −0.013 [−0.022, −0.004] (n = 2,141) |
| MuSiQue: contradiction lines added | 52 | 2 | 14 | 7 | 64 | 6 | −0.009 [−0.020, +0.003] (n = 789) |

Adding contradiction lines mainly turns answered questions into abstentions, both previously correct (C→A) and previously wrong (W→A). On 2Wiki it also lowers accuracy slightly among questions that stay answered.

## 4. What the predicted contradictions are (automatic diagnostics, not judgements)

- **Volume:** 12,816 predicted CONTRADICTS edges, of which 12,372 were rendered (the rest were removed by the 40-line cap). That is 9,750 unordered pairs in 3,044 of 4,976 questions. Rendered lines: 9,697 in 2Wiki, 2,675 in MuSiQue.
- **Confidence:** every edge has NLI confidence ≥ 0.90 (median 0.985), the classifier's threshold.
- **Heuristic triage of the 9,750 pairs:**

| heuristic triage | pairs |
|---|---|
| different source titles (facts about different entities) | 3,857 (40 %) |
| same title, different years | 1,962 (20 %) |
| same title, different numbers | 671 (7 %) |
| same title, pronoun-initial sentence | 734 (8 %) |
| same title, other | 2,526 (26 %) |

The gold supporting passages of a question are, by dataset construction, mutually consistent evidence for one answer. Most of these pairs are therefore probably not genuine contradictions. Examples:
- teaser vs trailer release dates of the same film;
- the "nineteenth" and "twentieth" Zhou king, who are father and son;
- the birth dates of two different film directors.

This is a hypothesis about label correctness, **not a measurement**. The blinded human package (`research_outputs/revision/contradictions/human_package_v1`, 240 pairs) is required before the paper may say what fraction is wrong, or that *wrong* contradictions (rather than contradiction lines as such) cause the harm.

## 5. Conclusions supported now

- **Supported (intervention, exploratory, two datasets, one reader):** showing predicted CONTRADICTS lines causes about a 3.3-point EM loss across all questions, and about a 4–7-point loss on questions that have such lines. It does so mainly by inducing abstention. Neither item order nor line count and overhead explains the original R4P−R4 effect.
- **Not yet supported:**
  - that the harm requires the contradictions to be *false* (this needs human labels);
  - that the effect generalises to other readers (this needs the second model);
  - an independent confirmation on fresh questions (possible on the 2Wiki pool of more than 8,000 unused questions, but not run).
