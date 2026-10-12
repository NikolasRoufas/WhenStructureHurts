# Experiment 3 (component attribution): limitations and status

**Status: not executable as designed in this campaign.** The run is queued for completeness and will report every question as unavailable. This report explains why and what would be needed.

## What Experiment 3 is meant to measure

Experiment 3 substitutes predicted components into an oracle pipeline that uses gold evidence and gold structure:
- C1: extracted claims;
- C2: predicted dependency edges;
- C3 and C4: selection under the oracle evidence length.

The loss relative to the oracle is then attributed to the component that was swapped in (`src/wsh/experiments/exp3_component_analysis.py`, EXPERIMENT_SPEC §6). The attribution is only meaningful if the oracle's structure is correct. A "predicted vs gold" comparison against a gold that is itself a heuristic derivation measures agreement between two heuristics, not component error.

## Why it cannot run now

1. **There is no human-verified structure.**
   - The verification package `annotations/verification_v1/` was prepared before the campaign: 50 questions, 64 dependency edges (22 of them with fallback anchors), 178 claim items.
   - It is entirely blank: no annotator has filled any verdict.
   - The pilot configuration therefore sets `exp3.accepted_statuses: [human_verified]`, as frozen in PILOT_PROTOCOL §4. Every Exp3 question is reported `unavailable` by design.
2. **The automatically derived edges are not oracle ground truth.** Claim-level DEPENDS_ON edges are derived from dataset annotations by rule (R-MSQ, R-2WK, R-HPQ, R-ANCHOR). For 25–33 % of primary questions the claim-level endpoint is a fallback guess (stratum C). Treating these as gold would make C2 "accuracy" partly a measure of the anchoring heuristic.
3. **HotpotQA C2 agreement is circular.** The HotpotQA derivation rule shares its title-mention heuristic with the dependency predictor, so their agreement is not reported at all (`dep_prf_suppressed`).

## What we report instead (clearly labelled)

- **Exp1** reports every structural contrast (R1−R5, R4−R5, R4P−R4) pooled and per edge stratum. This lets a reader see whether effects differ between exact-anchor-derived (B) and fallback-anchor-derived (C) structure. These are strata of *derived* structure, not verified-vs-unverified comparisons.
- **Exp2 P2** (relation retyping and flipping on R4) measures sensitivity to *corrupted* relations, relative to the same question's uncorrupted derived relations. This does not require the derived relations to be correct.
- **No relation precision or recall** against derived edges is presented as a measurement of relation quality.

## What would make Experiment 3 possible

1. Completing `annotations/verification_v1/` (GUIDE.md; estimated at 3–5 annotator-hours), ideally with a second annotator on a subset to measure agreement.
2. Importing it with `wsh annotations import`, which validates every row and links each question to the current dataset files by digest.
3. Setting `verified_annotations` in the config and rerunning Exp3. Only the 50 verified questions (stratum A) are then eligible. That is enough for an exploratory attribution, not for a confirmatory one.

Until then, the paper makes no component-attribution claim.
