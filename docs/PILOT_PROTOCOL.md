# Pilot protocol (frozen 2026-10-10, before any pilot generation)

**Status: FROZEN.** Do not edit this document after the pilot starts. If a change is unavoidable, add it to §11 (deviations) with the date, the reason and whether pilot outputs had been seen. Hypotheses H1–H4 (RESEARCH_PLAN.md) are not changed after pilot results are seen.

**Pilot status:**
- **Exploratory:** it estimates effect sizes and variance, and finds failure modes at scale.
- **Not confirmatory:** no result from it is a publication claim.
- **Too small for definitive conclusions:** 50–100 questions per dataset cannot support them.

## 1. Primary question

> Does the representation of the **same** supporting evidence affect multi-hop question-answering accuracy?

## 2. Primary comparisons (Experiment 1, Protocol A, gold evidence)

| # | contrast (b − a) | isolates |
|---|---|---|
| P-1 | R1 − R0 | passage vs claim representation (same sentences, same order) |
| P-2 | R5 − R1 | graph-derived ordering (same claims, same formatting) |
| P-3 | R4 − R5 | explicit relation lines (same claims, same order) |

**Primary datasets:** MuSiQue and 2WikiMultiHopQA. That makes 3 contrasts × 2 datasets = **6 planned primary tests**.

**Secondary comparisons (all exploratory):**
- R2 − R1 (order), R3 − R5 (step markers), R4P − R4 (verified vs predicted structure).
- Each primary contrast within edge strata A/B/C (§6).
- Protocol B, budget-controlled: the same contrasts at each budget and policy.
- Exp2 perturbation sensitivity: the change relative to rate 0, on label-preserving records without introduced answers.
- Exp3 component substitution: run only on human-verified questions.
- Exp0 baselines B0–B4.
- HotpotQA, HoVer and FEVER.

## 3. Questions (frozen)

`configs/question_sets/pilot_v1.json`
**sha256 `67e815648caf9bbcacd3928904b84205097f84df0e475d5a4b591ccb4b786f58`**

It was produced by `wsh questions freeze --spec configs/question_sets/pilot_v1.spec.yaml` with seed 1. Eligibility rules are in code (`wsh.data.question_sets.ELIGIBILITY`):
- the dev split only;
- not in `configs/excluded_questions.json`, which lists the 15 smoke questions used during prompt revision;
- gold evidence is available;
- for MuSiQue, 2Wiki and HotpotQA, a reasoning order is available.

| dataset | role | n | strata (seeded round-robin) | eligible pool | excluded by rule |
|---|---|---|---|---|---|
| MuSiQue | primary | 100 | hop 2/3/4: 34/33/33 | 2,414 | 3 (smoke) |
| 2WikiMultiHopQA | primary | 100 | 4 question types × 25 | 11,489 | 3 smoke; 1,084 no reasoning order |
| HotpotQA | secondary | 50 | bridge/comparison 25/25 | 6,043 | 3 smoke; 1,359 no reasoning order |
| HoVer | secondary | 50 | hop 2/3/4: 17/17/16 | 901 | 3 smoke |
| FEVER | secondary (verification baseline) | 50 | SUPPORTS/REFUTES 25/25 | 9,523 | 3 smoke; 6,409 NEI (no gold evidence) |

Pilot and full configs refuse to run on an unfrozen sample (`require_frozen_questions`) and refuse any excluded question (`assert_no_excluded`).

**Known structure of the sample:** 25 2Wiki comparison questions and 25 HotpotQA comparison questions have parallel steps and no dependency edges. For them R4 = R5 and R5 typically equals R1. They stay in the sample and appear in the `no_edges` stratum, and every contrast reports the number of identical-evidence pairs (§7).

## 4. Conditions

- **Generator:**
  - Default: the policy-compliant `Qwen/Qwen2.5-0.5B-Instruct@7ae55760` (`configs/pilot.yaml`).
  - A larger generator is possible only with written authorisation, via `configs/gpu_pilot.yaml` (stage `gpu_pilot`). It uses the same questions and conditions, and its results are reported per generator, never pooled.
- **Decoding:** greedy, a fixed prompt template (`qa-v2`) identical for every representation, and `max_new_tokens` 64.
- **Determinism:** seed 0, with deterministic CUDA settings where supported. Generator settings are checked to be identical across the records of a run (`metrics.json → consistency`).
- **Exp1 representations:**
  - R0, R1, R2 (3 shuffle seeds, averaged within question), R3, R4, R4P and R5.
  - Gold evidence: all sentences of the gold passages.
  - Structure comes from dataset-derived annotations, or human-verified ones once imported. Its provenance is named per record in `info.information.added_information`.
- **Protocol A (information-controlled):**
  - Natural lengths.
  - The fact set (claim ID → text) is identical for every representation and checked per question; a mismatch is a pipeline error.
  - Overhead (evidence tokens − content tokens) is recorded separately.
- **Protocol B (budget-controlled):**
  - Budgets of 1.0× and 0.5× the content tokens of the full fact set.
  - Gold-free BM25 fact ranking.
  - Two policies: `shared`, where every representation shows the same facts, and `per_representation`, where each keeps the largest prefix that fits.
  - Whole facts only. Every dropped fact is logged with its gold-support and answer-bearing flags, along with whether the required facts could fit at all.
- **Exp2 (secondary):**
  - R1 and R4 with P1–P7 at rates {0, 0.2, 0.4} (some at {0, 0.4}), seed 0.
  - P7 stays unavailable without verified temporal data.
- **Exp3 (secondary):** `accepted_statuses: [human_verified]`. Until the verification package is completed and imported, every Exp3 question is reported unavailable, by design.
- **Upper bound on Exp1 records:** (100 + 100 + 50) × 9 variants × 5 settings + (50 + 50) × 8 × 5 = **15,250**. HoVer and FEVER have no R3. Identical prompts are generated once and served from the cache.

## 5. Metrics

- **Primary:** question-level **exact match** for QA (SQuAD normalisation, maximum over aliases; yes/no exact) and **verdict accuracy** for HoVer and FEVER. These are coverage-adjusted: every attempted question is in the denominator, and unanswered ones score 0.
- **Secondary:**
  - token F1;
  - coverage, meaning answered = parsed and not abstained;
  - generation failure rate by type (taxonomy in `failure_analysis.py`);
  - evidence sufficiency (a lexical proxy: support shown, answer string present, sub-answers present);
  - answer-in-evidence;
  - evidence, content and overhead tokens;
  - facts kept and dropped, and answer-bearing facts dropped (Protocol B);
  - latency.
- **Citation accuracy** (validity, precision, recall, and missing vs invalid citations) and **citation-based groundedness** are computed but **not interpreted** for generators that fail to cite. At 0.5B, 5 of 671 answered smoke records cited anything. These metrics wait for a larger generator, and prompts will not be tuned to raise them.

## 6. Annotation strata (graph conditions)

| stratum | meaning |
|---|---|
| A | human-verified (imported from `annotations/verification_v1`) |
| B | dataset-supplied (B_dataset_supplied; currently none at claim level) or derived with an exact anchor (B_derived_exact_anchor) |
| C | derived with a fallback anchor: the claim-level endpoint is a guess |
| D | model-predicted (R4P) |

The strata are never pooled into "gold". Every contrast involving R3/R4/R4P/R5 is reported pooled and per stratum. Exp3 attribution is reported per stratum. C2 DEPENDS_ON agreement is **not reported** against labels derived with the predictor's own heuristic (HotpotQA). On other datasets it is reported only at passage level, with a caveat, until stratum A exists.

## 7. Statistical procedure (fixed)

- **Unit:** the question. Repeated records of a question (R2 seeds) are averaged within the question first.
- **Pairing:** only questions with both conditions available. `n_paired`, `n_only_a`, `n_only_b` and `n_identical_evidence` are reported for every contrast.
- **Inference:** paired percentile bootstrap of the mean difference, 2,000 resamples, seed 0, 95% CI, plus a two-sided bootstrap p-value.
- **Multiplicity:** Holm correction over the 6 planned primary tests. This applies **only** at the confirmatory stage (`stage: full`, n ≥ 100 per contrast). In the pilot no test is labelled confirmatory, and the reports print "exploratory".
- **Reporting rule:** a CI containing 0 is "inconclusive", never "no effect". Equivalence would need a pre-registered margin (proposed ±0.02 EM) and adequate n, which the pilot does not have.
- **Never pooled:** Protocols A and B, datasets, generators and edge strata.
- **Exclusions from accuracy analyses:** Exp2 records whose label effect is not `preserved`, or whose intervention introduced answer text. These are reported separately.

## 8. What the pilot is used for (decisions made in advance)

1. **Pipeline health.**
   - If pipeline errors exceed 2% of records, or an `InformationEquivalenceViolation` occurs, in any primary condition, fix the problem before anything else.
   - If generator settings are inconsistent within a run, discard that run.
2. **Variance:** estimate the standard deviation of paired EM differences for P-1 to P-3 on each primary dataset.
3. **Sample size for the full study:** the n giving 80% power to detect |Δ EM| = 0.03 (smallest effect of interest) at the Holm-adjusted α for 6 tests, using the pilot SD inflated by 20%. If the n exceeds the dev pool, report the minimum detectable effect instead.
4. **Generator:** the full study uses at least two generator families, each authorised in writing, chosen before seeing any confirmatory output.
5. **Protocol B budgets:** the full study keeps the pilot's two budget points unless the pilot shows a pipeline failure (e.g. budgets too small to keep any fact). In that case a change is recorded in §11 before the full run.
6. **Full-study questions:** a fresh frozen sample (seed 2) drawn after adding every pilot question to `configs/excluded_questions.json`.
7. **No outcome-based reselection:**
   - No representation, dataset or metric is dropped or added because of pilot results.
   - New analyses suggested by the pilot are labelled exploratory in the paper.
8. **Exp4 (adaptive selection):** stays disabled unless Exp1–3 show a reproducible effect in the full study.

## 9. What the pilot cannot show

- No hypothesis can be confirmed or rejected.
- Generalisation beyond one (0.5B) or two generators.
- Citation faithfulness, at 0.5B.
- Exp3 without human-verified annotations.
- Claim-level relation accuracy against derived labels.

## 10. Commands

`docs/SERVER_SETUP.md` §7 has the exact commands, which are prepared but not executed.

## 11. Deviations log

| date | change | reason | pilot outputs seen? |
|---|---|---|---|
| 2026-10-10 | Primary QA metric changed from token F1 to exact match | Investigator instruction during preflight | no (no pilot run exists) |
| 2026-10-10 | `min_matched` budget mode replaced by Protocols A/B | Audit A1: end truncation confounded structure with information loss | no |
| 2026-10-10 | Protocol B budgets set to {1.0, 0.5}× content tokens | The smoke run at 0.75× kept about 37% of facts under the shared policy; one point cannot show a trade-off. Chosen on smoke questions only, before any pilot question was used. | no |
| 2026-10-11 | Reporting addition (secondary): each contrast also reports the estimate restricted to pairs whose evidence differs ("informative pairs") and the paired coverage difference. Primary estimate, metric and contrasts are unchanged. | On the frozen set R5 = R1 byte-identically for 25/100 MuSiQue and 56/100 2Wiki questions, and R4 = R5 for 29/100 2Wiki questions. Pair selection uses inputs only. | no |
| 2026-10-11 | Engineering: batched generation (`model.batch_size: 8`) | Throughput. Batched = unbatched verified: 30/30 real prompts (CPU fp32) and 16/16 (MPS fp32). Must be re-verified on the server for each GPU model (`wsh preflight --batch-check`); otherwise use batch_size 1. | no |
| 2026-10-11 | Larger authorised generators run as stage `gpu_pilot` (`configs/gpu_pilot.yaml`) on the same frozen questions and conditions; `full` refuses every pilot question | Separate the exploratory GPU pilot from the confirmatory study | no |
| 2026-10-12 | Engineering: `configs/gpu_pilot.yaml` batch_size 8 → 1 (the fallback pre-specified in the 2026-10-11 entry) | Server batch check failed in bf16 on the RTX 5000 Ada: Qwen2.5-7B 5/8 and 0.5B 27/30 batched = unbatched (fp32 30/30), with changed answers. Unbatched bf16 is run-to-run identical. Smoke questions only (docs/GPU_PREFLIGHT_REPORT.md §5). | no |
