# Confirmatory protocol 2: predicted contradiction lines (frozen 2026-10-13)

**Status: FROZEN.** Written and committed (and pushed to GitHub) **before** the question set `confirm2_v1` was drawn and before any generation on it. Authorised by the investigator on 2026-10-13 (new data from the untouched development pools; compute from the remaining campaign allowance). Any later change goes into §8 with its date and reason; changes after data collection cannot alter the primary analysis.

## 1. Origin of the hypothesis

The hypothesis comes from exploratory analyses on already-analysed questions: the secondary contrast R4P−R4 on `confirm_v1`, and the revision-1 fixed-order controls (`docs/REVISION_PROTOCOL.md`, run `revision/exp1/20261012-200925_a2e6e3a8`). On those questions, adding the predicted `CONTRADICTS` lines to an otherwise identical prompt (R4P_FO vs R4P_FO_NC) changed EM by −0.053 (2Wiki) and −0.056 (MuSiQue) among questions with at least one such line. This protocol tests that effect on questions that no analysis has touched.

## 2. Conditions (both already implemented; `src/wsh/representations/relation_controls.py`)

| condition | facts | order | relation lines |
|---|---|---|---|
| R4P_FO | gold supporting sentences, identical across conditions (Protocol A, verified per question) | R5 order (derived from annotations where available, otherwise dataset order); identical across conditions | all relations predicted by the NLI relation predictor and title heuristic |
| R4P_FO_NC | same | same | the same predicted relations minus every `CONTRADICTS` line |

Everything else is fixed: Qwen2.5-7B-Instruct at revision `a09a3545`, bf16, greedy, batch size 1, max 64 new tokens, prompt `qa-v2`, the relation predictor and thresholds of the confirmatory run, physical GPU 0.

## 3. Sample

- `configs/question_sets/confirm2_v1.spec.yaml`, seed **5**, development split, eligibility rules of `src/wsh/data/question_sets.py` unchanged.
- **2WikiMultiHopQA:** 2,600 questions, 650 per question type.
- **HotpotQA (distractor):** 3,800 questions, stratified by question type.
- Excluded: smoke, pilot, prompt-development, `confirm_v1` and `retr_v1` questions (`configs/excluded_confirm2.json`).
- MuSiQue is not used: its eligible pool is nearly exhausted (about 70 questions remain).

**Population for the primary analysis:** questions whose R4P_FO evidence block renders at least one `CONTRADICTS` line. This is a property of the input, computed before generation and identical for both conditions. For the other questions the two prompts are byte-identical and the effect is zero by construction.

## 4. Hypotheses and tests

Primary family (Holm, family-wise α = 0.05, two tests):

- **H1-2Wiki** and **H1-HotpotQA**: H0: mean paired question-level EM difference (R4P_FO − R4P_FO_NC) = 0, in the primary population, two-sided.

A hypothesis is **confirmed** if its Holm-adjusted p < 0.05 and the estimate is negative. A positive significant estimate is reported as a significant effect in the opposite direction. A non-significant result is reported as inconclusive, never as absence of an effect.

Secondary (reported, Holm over the two datasets separately from the primary family):
- **S1:** abstention rate difference (R4P_FO − R4P_FO_NC), primary population.
- **S2:** EM difference over all questions (including the identical-prompt zero pairs).

Descriptive only: C/W/A transition matrices, accuracy among questions answered under both conditions, strata by number of contradiction lines (1–2, 3–5, 6+).

**Statistics:** paired percentile bootstrap over questions, 2,000 resamples, seed 0, 95 % CI; two-sided bootstrap p-value as in `docs/CONFIRMATORY_PROTOCOL.md` §3. The unit is the question. EM is SQuAD-normalised exact match maximised over aliases; an abstention or an unparseable answer scores 0. No question is dropped after generation; generation errors count as wrong and are reported.

## 5. Power

- From the exploratory runs: SD of the paired EM difference in the primary population ≈ 0.31 (2Wiki), 0.27 (MuSiQue).
- To protect against an inflated exploratory estimate (the pilot once overstated an effect fourfold), we power for **half** the exploratory effect: −0.025.
- With two-sided α = 0.025 (worst case under Holm) and 80 % power: n ≈ (3.08 × 0.31 / 0.025)² ≈ 1,460 questions per dataset in the primary population; with a 10 % margin, about 1,600.
- Prevalence of at least one contradiction line: 63 % (2Wiki, `confirm_v1`); 44 % (HotpotQA, 50 pilot questions, uncertain). Hence 2,600 and 3,800 questions.
- No top-up: if fewer questions qualify, the test runs with the number obtained, and the realised power is reported.

## 6. Cost

About 9,700 uncached generations plus relation prediction: about 2 GPU-hours on GPU 0. Campaign total before this run: 11.99 of 24 GPU-hours.

## 7. Analysis code

`scripts/revision/confirm2_analysis.py` (written before generation, committed with this protocol or before the run starts). It reads only the run's `predictions.jsonl`.

## 8. Changes after freezing

- **2026-10-13, after sampling, before any generation.** `confirm2_v1.json` (sha256 `53fecd59…`): the 2Wiki *inference* type had only 217 eligible unused questions, so the sampler filled the 2,600 from the other types (795 bridge-comparison, 794 comparison, 794 compositional, 217 inference) instead of 650 per type. The sample size, seed and all analyses are unchanged. 0 overlap with every earlier set.
- The analysis script was executed once on the revision-1 exploratory run (`20261012-200925_a2e6e3a8`) as a code check, before any generation on `confirm2_v1`; that output was deleted.
