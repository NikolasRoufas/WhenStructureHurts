# Experiment specification

All definitions refer to code paths in `src/wsh/`. "Verified" always means *dataset-supplied or deterministically derived from dataset annotations* (status recorded per item), never human-verified unless stated.

## 0. Data and annotation status

| Dataset | Split used | Supporting evidence | Reasoning structure | Status of structure |
|---|---|---|---|---|
| MuSiQue-Ans v1.0 | dev | paragraph-level (`is_supporting`) | decomposition (sub-q, sub-answer, paragraph) | order: dataset-supplied; DEPENDS_ON: derived (R-MSQ `#k`) |
| 2WikiMultiHopQA | dev | sentence-level | evidence triples | derived (R-2WK); unavailable for 8.6% |
| HotpotQA distractor | dev | sentence-level | none | bridge order derived (R-HPQ); unavailable for 18.4% |
| HoVer v1.1 | dev (908/4000 recoverable; 904 load) | sentence-level | none | unavailable |
| FEVER (copenlu) | "valid" | sentence; **NEI evidence is model-predicted (not gold)** | none | unavailable |

SUPPORTS / CONTRADICTS / DUPLICATE / SUPERSEDES gold edges: **unavailable for every dataset.** Sentence segmentation of MuSiQue: derived (regex-v1). Claim-level anchoring of DEPENDS_ON edges: rule R-ANCHOR (`representations/evidence.py`), with each edge tagged `anchor_match = exact | fallback`.

## 1. Controls common to all generation experiments

- Generator checkpoint pinned by revision; greedy decoding (sampling is forbidden by config); a single prompt template per task (`models/prompts.py`, version recorded per record). The instruction text is identical across representations, only the evidence block differs, and the prompt overhead is recorded (`prompt.overhead_tokens`).
- Answer format: two plain-text lines, with the assistant turn prefilled with `Answer:`. JSON is never required. Format deviations, truncation, missing and invalid citations are tracked but never zero a correctly parsed answer.
- Display IDs `E1..En` are assigned per prompt, so generators never copy internal IDs.
- `max_new_tokens`, `max_input_tokens` and `max_time_s` are fixed per config. Overflow is recorded as `context_overflow` and stays in the denominator.
- Every attempted example is in the denominator. Conditions that cannot be built without fabricating annotations are recorded as `unavailable`, excluded from metric denominators, and counted in every table.

## 2. Metrics

| Metric | Definition (`evaluation/`) |
|---|---|
| **EM (primary, QA)** | SQuAD exact match, max over aliases; yes/no exact (frozen in PILOT_PROTOCOL.md) |
| F1 | SQuAD token F1 (secondary); yes/no requires exact match |
| **Verdict accuracy (primary, verification)** | keyword-rule mapping of the answer onto the label set; free-form statements are `unparseable_verdict` (the FEVER fix) |
| Coverage | fraction of attempted examples with a parsed answer/verdict and no abstention (abstention = failure to answer, not a wrong answer) |
| Coverage-adjusted vs conditional | unanswered = 0 over all attempted examples, vs mean over answered examples only (with its n) |
| Citation validity / status | valid cited IDs / cited IDs; `citation_status` keeps missing (none_given) and invalid (some/all_invalid) citations apart. Not interpreted for generators that do not cite (0.5B) |
| Citation precision / recall | unit level (overlap with gold sentence/passage spans) and passage level |
| Evidence coverage | `support_coverage`, `content_recall`, `answer_in_evidence`, `hop_answer_coverage`, computed on what was actually shown; corrupted items never count. Presence checks are order-invariant: each shown item, and each passage's shown spans in original passage order |
| Groundedness | `grounded_lexical` (answer string in cited items); `grounded_nli` (nli-deberta-v3-**small** entailment ≥ 0.5, a different model from the relation classifier) |
| Cost | input/output/evidence/overhead tokens, latency (original-call latency for cache hits, flagged) |
| Failure taxonomy | `evaluation/failure_analysis.py` (13 flags, precedence-ordered primary) |

## 3. Experiment 0 — baselines (retrieved evidence)

B0–B4 as in `systems.py`. Fixes are covered by unit tests: position-based passage IDs (duplicate-title regression), invalid citation ≠ wrong answer, truncated-but-parsed answers scored, FEVER verdict mapping, pipeline errors kept in the denominator.

## 4. Experiment 1 — representation (primary)

Evidence: gold, scope `gold_passages`, i.e. all sentences of the gold passages, so every representation contains the same sentences (unit-tested).

| ID | Rendering | Order |
|---|---|---|
| R0 | one item per passage | dataset context order |
| R1 | one item per sentence-claim | dataset order |
| R2 | R1 | seeded shuffle (seeds recorded) |
| R3 | R1 grouped under `Step k:` (context order within a step) | reasoning-annotation order |
| R4 | R1 + `Relations:` block (verified DEPENDS_ON) | graph-derived (passage-level topological) |
| R4P | R4 with model-predicted edges | graph-derived from predicted edges |
| R5 | R4 without the relations block | same as R4 |

Evidence-sufficiency (`evidence_sufficient`): a lexical proxy — gold support shown, answer string present, sub-answers present.

**Protocols** (`representations/protocols.py`; never pooled — `protocol` is part of every condition):

* **A — information-controlled.** All representations show the identical fact set (claim id -> text), verified per question (`InformationEquivalenceViolation` otherwise). Natural lengths; overhead = evidence tokens - content tokens recorded separately. Structure a representation adds on top of the facts is named per record with its annotation status (`info.information.added_information`): R3 step grouping/order, R5 graph-derived passage order, R4 that order plus relation lines. Detected R0/R1 differences are recorded, not assumed away: context-dependent (pronoun-initial) facts, and passage text outside any sentence span.
* **B — budget-controlled.** A gold-free, representation-independent BM25 ranking of facts; budget = f x content tokens of the full fact set (`content:f`) or absolute (`abs:n`). Policy `shared`: largest ranking prefix that fits in every representation (same facts everywhere); `per_representation`: largest prefix that fits each representation's own rendering (verbose formats keep fewer facts). Whole facts only; every dropped fact logged with gold-support / answer-bearing flags; whether the required (gold-support) facts could fit at all is recorded. Reported: accuracy, facts kept, sufficiency, overhead, tokens, truncation, latency.

Primary contrasts (Protocol A, MuSiQue + 2Wiki; PILOT_PROTOCOL.md): R1−R0, R5−R1, R4−R5. Secondary: R2−R1, R3−R5, R4P−R4, all Protocol B contrasts, all per-edge-stratum contrasts. Contrasts with R3/R4/R4P/R5 are reported pooled and per edge stratum (A human-verified / B exact-anchor derived / C fallback-anchor derived / D predicted); every contrast reports `n_identical_evidence`.

Known non-equivalences: R0 vs R1 differ in ID markers and per-claim source titles (overhead, measured). For comparison/parallel questions R4 = R5 (no edges) and often R5 = R1. R3 is unavailable where no reasoning order exists.

> **Retired (audit A1, 2026-10-10):** the former `min_matched` mode truncated rendered evidence from the end, counting formatting tokens; structured representations lost answer-bearing content (answer present 0.89 for R0 vs 0.44 for R4 in the first smoke run). Replaced by Protocols A and B; see METHODOLOGICAL_AUDIT.md F1.

## 5. Experiment 2 — perturbations

Base: gold-evidence R1 and R4. P4 never injects sentences stating a gold answer; every intervention records `answer_introduced`, and accuracy deltas use only label-preserving records without introduced answers. Rates {0, .1, .2, .4}, with k = ⌈rate·n_eligible⌉ recorded. Seeds are recorded, and every changed item is listed in `info.intervention.changes`.

| P | Operation | Label effect |
|---|---|---|
| P1 | remove required claims | not_guaranteed / answer_removed → robustness + abstention |
| P2 | retype (or flip) edges | preserved (graph reps only) |
| P3 | permute claim / step positions | preserved |
| P4 | insert real non-gold sentences from the question's pool (BM25-hard or random) | preserved (distractor conflicts not checked) |
| P5 | strip sources / duplicate with fake "(mirror)" lineage | preserved |
| P6 | delete negation / qualifiers / dates, or replace an entity with "it" | not_guaranteed / answer_removed |
| P7 | external verified old/new statements + SUPERSEDES | from spec; **unavailable** (no verified temporal data) |

Sensitivity is measured against each question's own rate-0 record: answer-change rate and abstention change, plus ΔF1 *only* for label-preserving cases. H3 test: the representation × perturbation interaction on these deltas.

## 6. Experiment 3 — component substitution

Conditions oracle/C1–C4 as in the module docstring of `experiments/exp3_component_analysis.py`. All conditions use R4. In C3 and C4 the selection token budget equals the oracle evidence length. Eligibility: supporting passages, reasoning order and DEPENDS_ON status ∈ `accepted_statuses`, plus at least one dependency. Diagnostics: extraction stats (claims, unsupported, empty, truncated), edges lost in projection, DEPENDS_ON precision/recall at passage-pair level, count of unverifiable predicted edges. Attribution per (question, condition) vs oracle: no degradation / degraded with evidence loss (component) / degraded with evidence preserved (generation/structure) / format failure.

## 7. Experiment 4 — adaptive selection (gated)

See `experiments/exp4_adaptive_selection.py`. Deployable features only (name-checked), the R4P edges only, a question-level hashed train/test split, the oracle flagged as non-deployable, and the graph-build cost counted.

## 8. Statistics

Question-level paired bootstrap (2,000 resamples). Seeds and shuffles are averaged within question first. Holm correction is applied over the 6 planned primary tests at the confirmatory stage only (stage `full`, n ≥ 100); every pilot result is exploratory. n < 100 is tagged exploratory, and "CI contains 0" is reported as inconclusive, never as equivalence. Breakdowns are by dataset, hop count (`hop_count` in every record) and question type.

## 9. Preregistration (to be completed after the pilot, before the full run)

- [x] Primary metric per task: EM / verdict accuracy, coverage-adjusted (PILOT_PROTOCOL.md §5)
- [x] Primary contrasts: R1−R0, R5−R1, R4−R5, Protocol A, MuSiQue + 2Wiki (PILOT_PROTOCOL.md §2)
- [ ] Equivalence margin (proposed ±0.02 EM)
- [ ] n per dataset from pilot variance (power 0.8, α 0.05 Holm-adjusted)
- [ ] Generators (≥2 families) and decoding budget
- [ ] Human audit of ≥100 derived DEPENDS_ON edges and reasoning orders
