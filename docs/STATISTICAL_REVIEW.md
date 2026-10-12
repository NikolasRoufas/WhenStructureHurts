# Statistical review (revision-1)

This review is written as an ACL statistics reviewer would read the paper. Numbers come from `research_outputs/revision/audit/audit.json` (independent re-derivation) unless stated.

## 1. Confirmatory design

| item | assessment |
|---|---|
| Hypothesis family | Six two-sided tests: R1−R0, R5−R1 and R4−R5 on MuSiQue and 2Wiki, Protocol A, EM. Fixed in PILOT_PROTOCOL (`7311217`) before any generation; unchanged afterwards. **Sound.** |
| Unit of analysis | The question. Each representation is one greedy record per question, so the paired difference per question is the unit. R2 seeds (not in the family) are averaged within question. **Sound.** |
| Dependence between tests | The six tests share questions within a dataset and share representations (R1 in two contrasts, R5 in two). Holm controls the family-wise error rate under any dependence. **Sound.** |
| Bootstrap | Paired percentile bootstrap of the mean difference, 2,000 resamples, seed 0. The p-value is 2·min(P(d* ≤ 0), P(d* ≥ 0)) on the bootstrap distribution, so p has a resolution of 0.001. An independent numpy bootstrap (20,000 resamples, a different seed) gives CIs within 0.001 of the reported ones. With n = 1,744 / 3,232 and bounded differences in {−1, 0, 1}, the percentile bootstrap is well behaved. **Sound.** The exact McNemar test (secondary) agrees in direction: 2Wiki R1−R0 McNemar p = 0.010. |
| Holm correction | Recomputed independently: 2Wiki R1−R0 p_Holm = 0.018 (0.003 × 6); all others 0.535–0.974. **Correct.** |
| Sample size | Set prospectively from pilot SDs (inflated 20 %) for 80 % power at \|ΔEM\| = 0.03, α = 0.05/6. The sample was drawn after the protocol commit. The observed SDs of paired differences are close to the pilot's, so the confirmatory tests were adequately powered for 0.03. The one significant effect (−0.017) is smaller than the effect the study was powered for, so its interval is wide relative to its size; we report it as small. |
| Pilot vs confirmatory independence | Confirmatory questions are disjoint from all pilot and development questions (checked by uid). They come from the same dev splits, generator and prompt, so this is a *disjoint-sample* confirmation, not an independent cross-model or cross-dataset replication. The paper must say so. |

## 2. Equivalence claims (±0.02)

The draft's rule was "the 90 % bootstrap CI lies inside ±0.02". That equals a TOST at α = 0.05 per test, **without** adjustment across the six tests. The margin was proposed in PILOT_PROTOCOL before the pilot and fixed in CONFIRMATORY_PROTOCOL before the confirmatory sample, so it was not chosen after the results.

Stricter check: a paired TOST (normal approximation, which is appropriate at these n) with Holm over the six tests.

| contrast | 90 % bootstrap CI | TOST p | TOST p_Holm | equivalent at ±0.02? |
|---|---|---|---|---|
| MuSiQue R1−R0 | [−0.012, +0.011] | 0.0022 | 0.011 | yes |
| MuSiQue R5−R1 | [−0.023, +0.001] | 0.117 | 0.233 | no (inconclusive) |
| MuSiQue R4−R5 | [−0.001, +0.022] | 0.071 | 0.212 | no (inconclusive) |
| 2Wiki R1−R0 | [−0.027, −0.007] | 0.30 | 0.30 | no (a nonzero effect) |
| 2Wiki R5−R1 | [−0.016, 0.000] | 0.010 | 0.041 | yes |
| 2Wiki R4−R5 | [−0.001, +0.013] | 0.0004 | 0.0025 | yes |

**Verdict.** The three equivalence statements in the draft survive multiplicity correction. The paper now names the procedure and its multiplicity treatment. Equivalence is relative to a ±2 EM-point margin. It does not mean "no effect at all": for example, the 2Wiki R5−R1 interval still allows −0.016.

## 3. Problems found

1. **Overstated wording.** "Pre-registered" becomes "pre-specified and committed to version control before sampling". There was no external registry.
2. **The R4P−R4 secondary contrast changes order, relation content and line count at once.** The draft called it a relation-quality effect. The fixed-order controls (revision-1) are the appropriate design. They run on already-inspected questions, so they are exploratory interventions, not confirmations.
3. **Post-hoc subset analyses.** The "contradiction line present / absent" split conditions on an input property that is correlated with line count and with question type. The draft acknowledged the line-count confound. The revision replaces it with the intervention contrasts and keeps the split only as description.
4. **Exploratory multiplicity.** Exp2 has about 50 cells, the strata analyses several dozen, and the controls about 18 contrasts. No correction is applied to exploratory analyses, but the paper reports them as exploratory, gives intervals, and highlights only patterns that recur across datasets or representations. Readers should expect about 5 % of exploratory intervals to exclude zero by chance.
5. **Identical prompts.** Contrasts with many byte-identical prompts (R5 = R1 for 1,858 / 3,232 2Wiki questions) are diluted. The informative-pairs estimate is a pre-specified secondary analysis that selects on inputs only. Both estimates are reported.
6. **Abstention and EM.** EM counts an abstention as 0. Representation effects therefore mix "willingness to answer" with "correctness". The transition matrices (C/W/A, `scripts/revision/transitions.py`) separate them. These were added after the confirmatory result and are exploratory, but they are a descriptive decomposition of the same paired data, not a new test.
7. **Pilot-only results** (Protocol B, Exp0, Exp2) have n = 50–100 and wide intervals. They are not combined with confirmatory results, and the abstract now marks them as pilot.
8. **A prompt change is a new factor.** The no-abstention variant (revision-1) is analysed within prompt and as a prompt × representation interaction, never pooled with `qa-v2`.

## 4. What would make the statistics stronger

- An independent confirmation of the fixed-order contradiction-removal effect on fresh questions. There is a 2Wiki pool of more than 8,000 unused questions; MuSiQue has almost none left.
- A cross-model replication with a protocol frozen before its generation.
- Reporting the generator's run-to-run determinism. It is already verified: unbatched bf16 outputs were identical across runs on the preflight prompts.
