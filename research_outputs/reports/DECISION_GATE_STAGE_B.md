# Stage B decision gate (2026-10-12, after the focused Exp1 run)

**Basis:**
- Exp1 run `20261012-095222_797a0644`: 200 questions, 9,000 records.
- Analysis: `research_outputs/analysis/A_exp1_*` (via `scripts/analysis/build.py`).

Exp0 (secondary) was still running. Its results cannot change the gate, because the gate concerns the validity of the primary design. The criteria come from the campaign brief, §5.

| question | finding | assessment |
|---|---|---|
| 1. Did the experiment execute correctly? | 9,000 / 9,000 records; 0 unavailable, 0 generation errors, 0 pipeline errors; all outputs ended at EOS (none truncated); generator settings identical across records; physical GPU bus 1, no MPS; batch size 1. | yes |
| 2. Are the comparisons paired and comparable? | Protocol A information equivalence held on every question (a violation would be a pipeline error; there were 0). Identical-evidence pairs are counted per contrast: R5 = R1 for 25/100 MuSiQue and 56/100 2Wiki questions; R4 = R5 for 29/100 2Wiki questions (the comparison questions, which have no edges). Informative-pairs estimates are reported. | yes, with the identical-pair dilution reported |
| 3. Is there enough variation to identify an effect? | Discordant questions per primary contrast: 6–17 %. All six Protocol A primary 95 % CIs contain 0 (largest \|Δ\| = 0.07, 2Wiki R1−R0, [−0.16, +0.01]). The pilot SD implies 1,175–3,232 questions per contrast for 80 % power at \|Δ\| = 0.03. | the pilot cannot resolve effects of this size; a larger sample is required for any statement about H1/H2 |
| 4. Is answer correctness reliably measured? | Manual inspection of discordant cases: most disagreements are abstentions ("insufficient evidence" with complete evidence) or genuine wrong answers (for example, returning the bridge entity). Evaluation errors exist but are rare: diacritic folding (secondary check) changes 3 of 4,500 Protocol A 2Wiki records and no contrast. Alias/format near-misses: about 10 % of incorrect answers have F1 ≥ 0.5. | yes for EM as frozen; F1 and coverage are reported alongside |
| 5. Are information-loss and cost metrics valid? | Facts kept, answer-bearing facts dropped, overhead and evidence tokens behave as designed. `required_facts_fit_budget` is uninformative for MuSiQue (paragraph-level support makes every sentence of a gold paragraph "required"), so it is reported as such and answer-bearing measures are used instead. | yes, with that exception documented |
| 6. Are the trends worth investigating? | Under Protocol B at 1.0× (per-representation policy), R0 keeps 0.83 / 0.81 of the facts against 0.62–0.65 for R1/R4/R5, and the answer string is present in 0.85 vs 0.64–0.66 of 2Wiki blocks. EM differences are small and inconclusive. Representation shifts abstention: 2Wiki R0 abstains on 16 questions, the structured formats on 24–34. | yes: the H4 information-loss signal, the abstention shift and the inconclusive primary contrasts all call for the pre-specified larger test |

**Decision: proceed.**
- No blocking methodological problem was found, and no protocol change is made.
- **Stage C** (expanded exploratory pilot, frozen 350 questions) runs as pre-specified: Exp1, Exp2, Exp3 (expected: unavailable without human annotations) and Exp0.
- **The confirmatory run** follows `docs/CONFIRMATORY_PROTOCOL.md`, committed before its sample was drawn: the six primary tests on a disjoint seed-2 sample of 1,744 MuSiQue and 3,232 2Wiki questions, Protocol A only.

**Compute plan (estimates):**

| item | GPU-h |
|---|---|
| Stage C Exp1 | 0.4 |
| Stage C Exp2 | 1.5 |
| confirmatory Exp1 | 4–6 |
| Stage C Exp0 (150 additional questions) | 1.8 |
| Exp3 | < 0.1 |

That adds about 8–10 GPU-hours to the roughly 3 already used, well below the 24 GPU-hour ceiling. Order: Exp1-350 → Exp2-350 → confirmatory → Exp3 → Exp0-350, so the secondary Exp0 extension runs last and is the first item cut if the budget tightens.
