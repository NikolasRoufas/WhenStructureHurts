# Pre-GPU readiness gate (2026-10-11)

> **Superseded by [FINAL_SERVER_HANDOFF.md](FINAL_SERVER_HANDOFF.md)** (final audit later on 2026-10-11: batching implemented, GPU models prepared, 156 tests). Kept as a record.

## Verdict: **READY_WITH_RESTRICTIONS**

The framework is ready for a **small exploratory GPU pilot of Experiment 1 (Protocols A and B) and Experiment 2** on the frozen question set.

Graph-structure conclusions are restricted to the automatically derived annotation strata (B/C), reported separately, until the human-verification package is completed. **Experiment 3 stays disabled** in the pilot until verified annotations exist. **Experiment 4 stays disabled.** Citation metrics are computed but not interpretable with the 0.5B generator.

Running code is not readiness. Each item below states what was verified and what was not.

## 1. Test results

`.venv/bin/python -m pytest -q` → **133 passed in 17.85 s, 0 failed, 0 skipped** (Python 3.14.3, Apple M3, 2026-10-11)

| file | covers |
|---|---|
| `test_protocols.py` (21) | Protocol A fact identity, violation detection, named added information, overhead; shuffle-invariant coverage; token limits under both policies and 5 budgets; truncation logging; answer-bearing loss measured; selection policies; edge strata; end-to-end Exp1 with protocols kept separate and `n_identical_evidence` |
| `test_validity_guards.py` (36) | prompt = template + evidence + question; rendered lines map to the exact source facts; gold vs predicted edges; circular C2 suppression; exclusion and frozen-set guards; abstention ≠ wrong answer; missing vs invalid citations; EM/F1; pairing and question-level resampling; cache key; consistency check; intervention label effects; P4 answer guard; annotation export → import → overlay round trip, validation errors, digest linking, no overwrite; shipped package blank and linked; preflight |
| other suites | identifiers/provenance, dataset loaders (all 5, real files), representations, metrics/parsing, interventions, config/model-size policy/cache, statistics/EG-RAG/Exp4 guards, runner/artefacts/resume |

Integration on real data with the real 0.5B model, all on smoke questions:

| run | records | pipeline errors | key checks |
|---|---|---|---|
| exp1 `20261010-235522_b81ab513` | 210 | 0 | identical fact sets in 14/14 questions; equal answer-in-evidence across R0–R5 under A; 0 budget overruns under B |
| exp2 `20261010-235657_c2bf4194` | 480 | 0 | 0 introduced answers; P4 guard fired once on real data |
| exp3 `20261010-235838_a0c34362` | 75 (35 unavailable) | 0 | oracle edge stratum recorded (7 B, 1 C); attribution per stratum; C2 agreement suppressed on HotpotQA (circular); 361 s |
| preflight (pilot config) | — | — | all 8 checks passed, including dataset hashes against the frozen set and an MPS generation |

## 2. Bugs fixed in this phase

Full list with tests: METHODOLOGICAL_AUDIT.md §1.

1. `min_matched` truncation confounded structure with information loss. Replaced by Protocols A and B.
2. R3 leaked the supporting-fact annotation through within-step ordering.
3. Abstentions were counted as answered.
4. Missing and invalid citations were not separated per record.
5. P4 could inject answer-bearing distractors. There is now a generic `answer_introduced` audit.
6. C2 agreement was circular on HotpotQA. It is now suppressed.
7. The generation cache was shared across devices.
8. The smoke/pilot boundary was unenforced. There is now an exclusion list plus frozen question files.
9. Run directories could collide.
10. Machine paths were part of the config hash.
11. Contrasts did not report identical-evidence pairs.
12. The primary QA metric was changed to EM, as instructed.

## 3. Remaining methodological risks

METHODOLOGICAL_AUDIT.md §3–§5 has the full list. These matter most for the pilot:
- **Graph structure is automatically derived:** none is human-verified yet. 18–26% of derived edges use fallback anchors (stratum C).
- **Comparison questions dilute the graph contrasts:** for the 50 comparison questions R4 = R5, and often R5 = R1, which dilutes P-2/P-3. `n_identical_evidence` is reported.
- **Sufficiency is a lexical proxy.** MuSiQue's support is passage-level, so `required_facts_dropped` is pessimistic there.
- **Protocol B parameters are design choices:** the BM25 ranking and the budget points have no empirical justification.
- **Relation-classifier thresholds** (R4P, C2–C4) were chosen without accuracy data.
- **Throughput:** generation is unbatched.

## 4. Status of each experiment

| experiment | status for the GPU pilot | condition |
|---|---|---|
| Exp1 Protocol A | **ready (primary)** | R1−R0 needs no structural annotation. R5−R1 and R4−R5 use derived structure: they are reported per stratum and described as *derived-structure* effects until stratum A exists. |
| Exp1 Protocol B | **ready (secondary, exploratory)** | Budget points and ranking are pre-specified. Results are reported only alongside the evidence-accounting table. |
| Exp2 perturbations | **ready (secondary)**, P7 disabled | P7 needs verified temporal data |
| Exp0 baselines | **ready (secondary)** | B4 is a labelled reconstruction of EG-RAG |
| Exp3 component analysis | **disabled until annotations are imported** | The pilot config accepts only `human_verified`, so every question is unavailable by design |
| Exp4 adaptive selection | **disabled** | Gated on reproducible Exp1–3 effects |
| Citation / grounding analysis | **not interpretable at 0.5B** | Retained for larger authorised generators |

## 5. Verified evidence annotations

- **Human-verified:** none (0 questions).
- **Package prepared:** `annotations/verification_v1`, containing 50 pilot questions, 64 proposed edges (42 exact-anchor, 22 fallback-anchor) and 178 claim items.
  - Includes an annotation guide, a readable view and the CSVs to fill.
  - The importer validates entries and links them to dataset content.
  - All fields are blank (unit-tested).
- **Not prepared:** LLM-extracted claims for Exp3 C1/C4. They must come from the generator that is actually used.

## 6. Is Protocol A scientifically usable?

**Yes, for the primary question, with one restriction.** Identical fact sets are enforced per question, every piece of added information is named with its provenance, and overhead is measured separately.

R1 vs R0 isolates passage vs claim format directly. The graph contrasts (R5−R1, R4−R5) currently test the effect of **automatically derived** structure. They can be interpreted as effects of *verified* structure only on stratum-A questions, after annotation.

Recorded but not removed: residual R0/R1 non-equivalences (per-claim source titles, context-dependent sentences).

## 7. Is Protocol B scientifically usable?

**Yes, as a secondary and exploratory accuracy–cost analysis.** It never truncates text: it selects whole facts with a gold-free ranking, respects the budget (tested), and logs every dropped fact with its support and answer-bearing status.

Restrictions:
- Its conclusions depend on the pre-specified ranking and budget points.
- Sufficiency is a lexical proxy.
- It is never pooled with Protocol A.

## 8. Is the pilot design frozen?

**Yes, for the 0.5B pilot.** PILOT_PROTOCOL.md fixes:
- the questions: `configs/question_sets/pilot_v1.json`, sha256 `67e81564…`;
- the conditions, metric, contrasts, statistical procedure and expansion rules;
- a deviations log, with 3 pre-pilot entries.

**Not frozen:** the choice of any larger GPU generator. It needs your written authorisation, and it must be fixed before any of its outputs are seen.

## 9. Commands for running the pilot later (prepared, not executed)

```bash
# on the server (docs/SERVER_SETUP.md)
python -m pytest -q
wsh preflight --config configs/pilot.yaml --tiny-generation
wsh run exp1 --config configs/pilot.yaml
wsh run exp2 --config configs/pilot.yaml
wsh run exp0 --config configs/pilot.yaml
# resume after interruption
wsh run exp1 --config configs/pilot.yaml --resume <results_root>/pilot/exp1/<run_id>
# larger authorised generator: configs/gpu_pilot.yaml (stage gpu_pilot) + WSH_COMPUTE_AUTHORIZED=1 + --authorized-compute
# after annotation: wsh annotations import ... ; then exp3 with verified_annotations=<file>
```

## 10. Human review required before launch

1. **Your approval to run the pilot**, and for a GPU pilot, the written authorisation of the generator(s): model ID, pinned revision and GPU-hour budget.
2. **Review of PILOT_PROTOCOL.md** before the first pilot generation. After that it is frozen, and changes go to the deviations log.
3. **The verification package** (about 3–5 hours). It is not required to start the Exp1 Protocol A pilot. It **is** required for any claim about verified structure, for stratum A, and for Exp3.
4. **The hardware information** listed in SERVER_SETUP.md §10.
5. Optional: a decision on batching generation before a large GPU pilot (an engineering item; it does not affect validity).
