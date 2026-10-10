# Methodological audit (pre-GPU preflight 2026-10-10; final readiness audit 2026-10-11)

Each item is in exactly one category:

- **Fixed:** a confirmed defect, corrected in code, with a regression test.
- **Controlled by design:** a validity risk that the design or an automated guard prevents or makes visible.
- **Requires human verification:** cannot be settled by code.
- **Requires stronger model:** not measurable or meaningful with the 0.5B development generator.
- **Still unresolved:** a known limitation with no fix yet, reported as such.

Tests are in `tests/`; the guards are named so they can be found with grep.

## 1. Fixed

| id | problem | fix | test |
|---|---|---|---|
| F1 | **`min_matched` end truncation** counted formatting tokens and cut from the end. Structured representations lost answer-bearing content: answer present in 0.89 of R0 cases vs 0.44 of R4 cases in the smoke run. | Mode retired. **Protocol A** uses identical fact sets with equivalence checked per question. **Protocol B** selects whole facts with a representation-independent ranking under a budget, logs every drop, and records sufficiency. New smoke run: answer-in-evidence equal across R0–R5 under A (0.889 each), 0/14 equivalence violations. | `test_protocols.py` (21 test cases) |
| F2 | `answer_in_evidence` and `hop_answer_coverage` depended on display order | Order-invariant: each item, and each passage's shown spans in passage order | `test_answer_in_evidence_is_order_invariant`, `test_shuffle_does_not_change_coverage` |
| F3 | **R3 leaked the supporting-fact annotation.** Within each step, gold supporting sentences were listed first; no other representation had this information. | Step claims are kept in context order | `test_gold_edges_and_path_from_annotations` |
| F4 | An abstention ("insufficient evidence") counted as *answered*, mixing failure to answer with answering | Abstention is unanswered: it leaves coverage and still scores 0 | `test_abstention_is_unanswered_not_wrong` |
| F5 | Missing and invalid citations were not separated in the per-record metrics | `eval.citation_status` ∈ {none_given, all_valid, some_invalid, all_invalid, not_applicable}, with separate failure flags | `test_missing_and_invalid_citations_are_separate` |
| F6 | **P4 could inject distractor sentences that state the gold answer**, adding answer evidence | Answer-bearing candidates are excluded (it fired on 1 real smoke question, 2Wiki 3733d61a…). Every intervention now records `answer_introduced`, and such records are excluded from accuracy deltas. | `test_p4_never_injects_answer_evidence`, `test_every_intervention_declares_label_effect` |
| F7 | **C2 DEPENDS_ON agreement was circular on HotpotQA**: the gold rule R-HPQ and the predictor both use title mention | Precision/recall suppressed when the gold edges share the heuristic. Otherwise reported at passage level with a "derived, not verified" caveat; against human-verified edges once they exist. | `test_c2_agreement_suppressed_when_gold_shares_the_heuristic` |
| F8 | The generation cache was shared across devices, so CPU outputs could be reused in a GPU run | Device and dtype are part of the cache key | `test_cache_key_covers_everything_that_changes_outputs` |
| F9 | Smoke/pilot separation was not enforced | Exclusion list (`configs/excluded_questions.json`). Pilot and full runs refuse excluded questions and require a frozen question file. | `test_excluded_questions_refused_outside_smoke`, `test_pilot_must_use_frozen_questions`, `test_frozen_pilot_set_excludes_smoke_questions` |
| F10 | Two runs started in the same second with the same config collided | Atomic, unique run directories (`…-2`) | `test_new_run_never_reuses_directory` |
| F11 | The primary QA metric was F1 | Exact match (frozen protocol) | reporting / `primary_metric` |
| F12 | Machine-specific paths entered the config hash, so a run could not resume on another mount point | Paths excluded from the hash; env vars `WSH_RESULTS_ROOT`, `WSH_CACHE_PATH`, `WSH_DATA_ROOT` | — |
| F13 | Contrasts did not show how many pairs had identical evidence (e.g. R5 = R1 when the graph order equals the context order) | `n_identical_evidence` in every contrast | `test_exp1_records_keep_protocols_separate` |
| F14 | Generation was unbatched | Batched generation implemented and tested (§6 below) | `tests/test_batching.py` (12 cases) |
| F15 | Qwen3.5's default chat template opens a `<think>` block, so answers would follow free-form reasoning and break the answer format, unlike the Qwen2.5 conditions | `chat_template_kwargs: {enable_thinking: false}` in the registry, passed to the template and recorded in the decoding settings | `test_qwen35_disables_thinking_in_chat_template`, `test_chat_template_kwargs_reach_the_template` |
| F16 | A larger-model pilot could only run as stage `full` (the confirmatory stage) | New stage `gpu_pilot`: authorisation required, frozen pilot questions, exploratory labels. `full` refuses every pilot question. | `test_gpu_pilot_config_pinned_and_gated`, `test_full_stage_refuses_pilot_questions`, `test_gpu_models_*` |
| F17 | The smoke script needed `/usr/bin/time` (often missing on Linux) and a fixed venv path | Bash `time`; `WSH` can point at any install | — |
| (earlier) | Reranker NaN; order-dependent coverage; report column shift; budget counter; prompt v1 | See EXPERIMENT_LOG §4 | — |

## 2. Controlled by experimental design

| risk | control |
|---|---|
| Gold answers reaching the model through hidden context | `assert_prompt_composition` runs on every generation: the prompt must equal the fixed template filled with the evidence block and the question, nothing else. Tests: `test_prompt_is_template_plus_evidence_plus_question`, `test_templates_contain_no_dataset_content`, `test_rendered_evidence_has_only_facts_and_structure` (every rendered line is a fact whose ID maps to exactly that text, or a structural line; no sub-questions, sub-answers or gold flags). |
| Annotation-derived information in R3/R4/R5 | It is the treatment, but it is named per record (`info.information.added_information`, with the annotation status) and never hidden. R0/R1 use the dataset's context order, never gold order. |
| Gold vs predicted evidence mixed | Every edge carries a status. R4P is a separate condition, and strata A/B/C/D are never pooled (`test_gold_and_predicted_edges_are_separate`, `test_edge_strata`). |
| Dev/test boundary | Test splits are refused by the loader and by config validation (`test_test_split_refused`, `test_stage_limits_enforced`). |
| Prompt tuning on evaluation questions | The only prompt revision (qa-v1→v2) and the relation-threshold inspection used the 15 smoke questions, which are excluded from the pilot and full study. |
| Protocol A and B conflated | `protocol` is part of every condition, so every summary row and contrast stratum belongs to one protocol (`test_exp1_records_keep_protocols_separate`). |
| Unpaired comparisons | The intersection of available questions only; `n_only_a`/`n_only_b` reported (`test_paired_uses_only_shared_questions`). |
| Resampling unit | The question; repeated records are averaged within the question (`test_bootstrap_unit_is_the_question`, `test_repeated_runs_are_averaged_within_question`). |
| Generator settings differing between paired conditions | One config per run. `metrics.json → consistency` and a report banner flag any difference (`test_consistency_flags_mixed_generator_settings`). |
| Answer validity after perturbation | Every intervention declares `preserved` / `not_guaranteed` / `answer_removed` / `unavailable` (validated). Accuracy deltas use only `preserved` records without introduced answers. |
| Unavailable conditions | Recorded with a reason, counted in reports, excluded from denominators, never imputed. |
| Length confound in Exp2 (P1 removes text, P4 adds it) | `evidence_tokens` is on every record; perturbation effects should be read alongside it. |
| Same-question selection bias | The frozen sample is drawn by seeded stratified round-robin from a rule-filtered pool. Eligibility counts are recorded in the frozen file. |
| Identical prompts across conditions | On the frozen set R5 = R1 byte-identically for 25/100 MuSiQue, 56/100 2Wiki and 36/50 HotpotQA questions; R4 = R5 for 29/100 2Wiki and 25/50 HotpotQA (no edges). These pairs contribute a true zero. Every contrast reports `n_identical_evidence` and, as a pre-specified secondary estimate, the contrast on informative pairs only. |
| Generation failures driving accuracy differences | Every contrast reports the paired coverage difference next to the EM difference |
| Cache serving stale outputs | The key includes model, revision, the full rendered prompt (template + evidence), `max_new_tokens` and all decoding settings, including device, dtype and batch size. |

## 3. Requires human verification

| item | status |
|---|---|
| Derived DEPENDS_ON edges (strata B/C). 18–26% use fallback anchors (pilot sample). | Package `annotations/verification_v1`: 50 questions, 64 edges (42 exact, 22 fallback), blank. Import is validated and digest-linked. |
| Derived reasoning orders (R-MSQ, R-2WK, R-HPQ) | Same package (`paths.csv`) |
| Claim faithfulness and self-containedness | 178 items in `claims.csv`: rule-based splits plus context-dependent supporting sentences |
| LLM-extracted claims (Exp3 C1/C4) | **Not in the package.** They must be extracted by the generator actually used, then audited. |
| Gold answer correctness | Recorded per question (`answer_correct`), never applied to labels |
| Exp3 as evidence | The pilot config accepts only `human_verified`, so Exp3 is unavailable until the package is imported |
| P7 temporal conflicts | Needs a verified temporal spec; unavailable otherwise |

## 4. Requires stronger model

| item | evidence |
|---|---|
| Citation validity, precision and recall; citation-based groundedness | 0.5B cited in 5 of 671 answered smoke records (0 of 186 in the new Exp1 smoke). Not interpreted; prompts are not tuned to change this. |
| LLM claim extraction quality (C1/C4) | 0.5B fragments sentences (EXPERIMENT_LOG §3) |
| Verification label compliance | 0.5B sometimes outputs labels outside the set ("REJECTS"); these are counted as unparseable |
| Whether any representation effect transfers | Effects at 0.5B may not hold for 7B+ models; generators are never pooled |

## 5. Still unresolved

| id | limitation | how it is handled |
|---|---|---|
| U1 | Dataset sentence segmentation is sometimes not self-contained (HotpotQA splits "Hey Pa! / There's a Goat…"). Pronoun-initial claims lose their referents when reordered (R2) or isolated. | Kept, because supporting-fact indices refer to it. Measured per record (`context_dependent_facts`) and listed for annotation. |
| U2 | MuSiQue support is passage-level, so every sentence of a gold passage counts as "required". Protocol B's `required_facts_dropped` is pessimistic there, and `support_first` selection is uninformative. | Sufficiency for MuSiQue relies on answer and sub-answer presence (`hop_answer_coverage`) |
| U3 | `evidence_sufficient` is a lexical proxy: it misses paraphrased answers, and is undefined (None) for yes/no and verification | Reported as a proxy; never a primary outcome |
| U4 | Relation-classifier thresholds (CONTRADICTS ≥ 0.9 plus a shared entity) were chosen by inspecting smoke edge counts, without accuracy data | R4P, C2–C4 are secondary; thresholds are recorded |
| U5 | Comparison questions (25 2Wiki, 25 HotpotQA) have no edges, so R4 = R5 and often R5 = R1; this dilutes P-2/P-3 | `n_identical_evidence` and the `no_edges` stratum are reported |
| U6 | FEVER NEI is excluded from gold-evidence experiments, shifting the label distribution relative to Exp0 | Documented; FEVER is secondary |
| U7 | The Protocol B ranking (BM25 relevance) and budget points (1.0×, 0.5× content) are design choices without empirical justification | Pre-specified, in the deviations log |
| U8 | HoVer: only 904 of about 4,000 dev claims are recoverable without the 2017 Wikipedia dump | Secondary dataset |
| U9 | Exp0 B4 is a *reconstruction* of EG-RAG; features and weights are our choices | Labelled everywhere; never compared with the original paper's numbers |
| U10 | GPU determinism is best effort (`warn_only`), so GPU and CPU outputs differ | Device in the cache key and manifest; runs never mix devices |
| U11 | Batched = unbatched is verified only for Qwen2.5-0.5B on CPU fp32 (30/30 prompts; 186/186 Exp1 records end to end) and MPS (16/16). It is **not verified on CUDA/bf16 or for any GPU model**, and batching was slower than unbatched on CPU and MPS. | `wsh preflight --batch-check` per model on the server; use batch_size 1 if it fails |
| U13 | Qwen3.5-9B: loading the multimodal checkpoint as text-only `Qwen3_5ForCausalLM` is supported by transformers 5.12.1 by design (it ignores the visual and mtp weights and remaps the prefix) but has **never been executed**. Its hybrid linear attention makes the batching check essential. | `wsh preflight --tiny-generation --batch-check` before any Qwen3.5 run |
| U14 | Graph contrasts have reduced power: the informative pairs for R1−R5 are 75 (MuSiQue) and 44 (2Wiki) of 100. 33% of MuSiQue and 25% of 2Wiki pilot questions have fallback-anchored edges (stratum C). | Reported; pilot SDs feed the full-study sample size |
| U12 | Old smoke runs carry superseded per-record metrics | `SUPERSEDED.md` in each run directory; raw predictions kept |

## 6. Batched generation: what is verified

| property | evidence |
|---|---|
| batched = unbatched outputs (mixed lengths, two `max_new_tokens` groups, batch sizes 2/4/16) | tiny randomly initialised Qwen2 (padding errors would change its outputs): exact equality of text, output tokens, input tokens and finish reasons |
| real model | Qwen2.5-0.5B on 30 real smoke prompts (R0/R2/R4): 30/30 identical on CPU fp32. Frozen pilot prompts on MPS: 16/16. End-to-end batched Exp1 smoke run vs the earlier unbatched run: 210/210 record keys, 186/186 identical outputs and evaluations. |
| left padding, attention mask, cut at first EOS, request-order association | `test_batched_is_deterministic_and_left_padded`, `test_rows_are_cut_at_first_eos`, `test_runner_batched_equals_unbatched_records` (answers depend on the prompt, so any mix-up shows) |
| out-of-memory handling | `test_oom_splits_batch_and_keeps_every_result` (halving down to 1; a single prompt that still fails is an error record) |
| caching | `test_cache_works_with_batching_and_is_batch_size_specific`; identical prompts are generated once and served as cache hits, as a sequential run would |
| resume after interruption, no duplicates or losses | `test_interrupted_batched_run_resumes_without_loss_or_duplication`; budget caps count queued records (`test_budget_cap_counts_queued_records`) |
| not verified | CUDA, bf16, the 3B/7B/9B models, throughput on a GPU |
