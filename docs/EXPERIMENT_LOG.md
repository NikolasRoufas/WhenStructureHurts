# Experiment log

This is a chronological record of what was actually executed. **Every run so far is a smoke test.** These runs check the software and pipeline only, using a 0.5B development model and 3 questions per dataset. None of the numbers here, or in the run reports, is evidence for or against H1–H4.

## 1. Environment

Apple M3, 16 GB RAM, CPU float32, Python 3.14.3; full details are in REPRODUCIBILITY.md. Generator: `Qwen/Qwen2.5-0.5B-Instruct@7ae55760` (494M parameters, checked again after load). Encoders, all under 150M parameters:
- `BAAI/bge-small-en-v1.5`
- `cross-encoder/ms-marco-MiniLM-L6-v2`
- `cross-encoder/nli-deberta-v3-xsmall` (relation classifier)
- `cross-encoder/nli-deberta-v3-small` (groundedness)

No model above 1B parameters was downloaded or loaded. No paid API was used. The directory is not a git repository, so manifests identify the code by `source_tree_sha256`.

### Dataset files (sha256, from `data/raw/MANIFEST.json`)

| dataset / split | sha256 |
|---|---|
| musique/dev | `15fa63794d18a94ce12411aca6e2327e65b6e83b0b1490efab3f1962e48abf3b` |
| 2wikimultihopqa/dev | `408e2dbb28edc6c8b9ca3ba0c94d4fc7bf17ffb923766593a3a7f546ab4cba59` |
| hotpotqa/dev | `c20b638ca82b21d04fe12e14ff417ad05153d4d215a65de54497fca4e972f7c6` |
| hover/dev | `67c14858f2d7fcdb96b6fe3d538ffcd6f76e3ba594aa2c0cd4359f601101e89d` |
| fever/dev | `5da0ccc0ccf77f974611de13f8aac6f78c6bba6293912835099eb6029baa85d9` |

Full dev splits parse with 0 validation errors:
- MuSiQue: 2,417 questions.
- 2Wiki: 12,576 (reasoning order derivable for 11,492).
- HotpotQA: 7,405 (bridge/comparison order derivable for 6,046).
- HoVer: 904 recoverable from the HotpotQA distractor context.
- FEVER: 15,935.

### Smoke sample (`configs/smoke.yaml`, sample_seed 0, 3 per dataset)

| dataset | qids |
|---|---|
| musique | 2hop__219456_87295, 2hop__802991_443552, 4hop1__58323_375563_161848_53331 |
| 2wikimultihopqa | 3733d61a0bde11eba7f7acde48001122, cd791c8a0bdd11eba7f7acde48001122, 676d16800bb011ebab90acde48001122 |
| hotpotqa | 5abf63f15542997ec76fd3ea, 5a7555215542996c70cfaee1, 5a8595a85542992a431d1b48 |
| hover | 1fde776f-f5e1-45d1-a48a-b2929ebedf39, 984928b7-6d4b-412a-9265-d04ed8738a64, 9a6c72f4-024b-406e-aa1e-575ab2be55f3 |
| fever | bfc5009bd295d44758b6393a23e07820, 5e6341966910fa8a0d09cd89c8005201, 1e1e148d1e1c89c5c9e959fddec7b792 (NEI: no gold evidence, so it is `unavailable` in the gold-evidence experiments) |

None of these questions appears in the pilot sample (sample_seed 1, checked 2026-10-10). This is not enforced in code; see §6.

## 2. Runs

| run | status | wall clock | uncached model calls | records | notes |
|---|---|---|---|---|---|
| `exp0/20261010-124651_79ce4ae8` | **INVALID** (see `INVALID.md` in the run directory) | 575 s | 297 | 75 | Every reranker score was NaN (§4.5). Kept for the audit trail. |
| `exp1/20261010-125634_2390c640` | valid | 114 s | 119 | 210 (24 unavailable) | Gold evidence, modes `none` and `min_matched`. No reranker involved. |
| `exp2/20261010-125836_79ebd969` | valid | 101 s | 113 | 480 (110 unavailable) | R1/R4 × P1–P7, rates {0, 0.4}. P4 uses BM25 only, so the reranker bug did not affect it. |
| `exp3/20261010-130025_80bc797c` | valid | 129 s | 61 | 75 (35 unavailable) | Ran after the reranker fix. |
| `exp1/.../exp4_plumbing_check.json` | plumbing only | <10 s | 0 | – | 9 complete questions, 7 train / 2 test. Exercises the selectors and leakage checks; no conclusions can be drawn. |
| `exp0/20261010-210157_79ce4ae8` | valid | 82 s (warm cache) | 57 | 75 | Rerun with the fixed reranker. LLM extractions for unchanged passage sets were served from the deterministic cache. A cold run takes about 575 s. |

Pipeline errors in valid runs: **0**. Non-finite metric values: **0**. Empty generations: **0**. Truncated generations: **0**. Every `unavailable` record carries a reason:
- FEVER NEI has no gold evidence.
- HoVer and FEVER have no reasoning order, so R3, R4-edges and P2 are unavailable.
- P6 is unavailable when no claim admits the edit.
- P7 is unavailable because no verified temporal spec exists.
- In Exp3, verified annotations are missing for HoVer and FEVER.
- In Exp3, HotpotQA comparison questions have no dependency structure.

### Exp0 rerun verification (the reranker fix)
- 420 of 420 numeric retrieval scores are finite. In the invalid run, every reranker score was NaN.
- In 14 of 15 B1 questions the reranker changed the top-k relative to first-stage order. First-stage ranks of the selected passages reach position 5, so reranking pulls in passages from below the cut-off.
- B0 and B1 show identical evidence for 1 of 15 questions; in the invalid run it was 15 of 15. Nothing forces them to differ: the remaining identical case is a genuine agreement between the two rankings.
- B0 evidence is identical between the invalid run and the rerun (15 of 15), as expected, since B0 has no reranker.
- B2, B3 and B4 evidence changed in 14, 14 and 13 of 15 questions respectively.

## 3. Behaviour of the 0.5B generator (pipeline observations, not results)

- The model almost never writes the `Evidence:` line. Only 1/186, 2/370, 0/40 and 2/75 answered records cite anything (Exp1, 2, 3, 0 respectively). **Citation precision and recall, and citation-based groundedness, are therefore unmeasurable at 0.5B.** In the reports they show as 0, but those zeros reflect output format, not attribution quality. A larger generator, or a separate citation step, is needed before these metrics mean anything.
- Verification outputs sometimes use labels outside the label set (e.g. "REJECTS"). These are counted as `unparseable_verdict`, never mapped by guesswork.
- Some outputs are a bare ID (`Answer: [E1]`). These are parsed as a citation with no answer, which is correct.

## 4. Problems found and fixes made (chronological)

1. **Model revisions in the config were not verified.** All of them were checked against the Hub API. Two encoder parameter counts and the `nli-deberta-v3-small` revision were corrected.
2. **Prompt revision qa-v1 → qa-v2.** The 0.5B model ignored the format instruction when it came before the question. In qa-v2 the instruction follows the question and the response is prefilled with `Answer:`; the parser also accepts `[Answer: X]`. `PROMPT_VERSION` was bumped, which changes cache keys. Only smoke questions were seen when making this change, and they do not overlap the pilot sample.
3. **The relation classifier over-predicted CONTRADICTS** (190 edges among 42 claims). The threshold was raised from 0.7 to 0.9, and a shared non-title entity is now required. This change was based on edge counts in smoke data, not on measured accuracy, and remains unvalidated (§6).
4. **The generation budget counted only answer generations.** It now counts every uncached model call, including LLM extraction (`n_model_calls_uncached_incl_extraction`).
5. **All reranker scores were NaN.** Safetensors memory-maps weights. For `ms-marco-MiniLM-L6-v2`, tensors ended up at misaligned addresses (`data_ptr % 64 == 2`), and the Apple-CPU matmul returns NaN on those. Python sorting with NaN keys kept the first-stage order, so **B1 silently equalled B0**, and B2–B4 ran without reranking.
   - Fix: `realign_parameters` copies every parameter into fresh memory for all four encoders and the generator.
   - Guard: `assert_finite` now checks NLI, reranker and dense outputs, so this kind of failure raises an error instead of passing silently.
   - Cleanup: 30 NaN rerank cache entries were purged, and the run was marked INVALID.
   - Check: NLI and dense cache entries were confirmed free of NaN.
   - Unit test: `test_realign_and_finite_guard`.
6. **`answer_in_evidence` and `hop_answer_coverage` depended on display order** (found during this audit). They matched answers against shown texts concatenated in render order. An answer that crosses a sentence boundary could therefore be "present" in R1 and absent in R2, so order alone changed a coverage metric. Example: HotpotQA `5a7555215542996c70cfaee1`, whose answer is "Hey Pa! There's a Goat on the Roof"; HotpotQA's own segmentation splits it after "Hey Pa!".
   - Fix: each shown item is checked on its own, and so is each passage's set of shown spans re-joined in original passage order.
   - Regression test: `test_answer_in_evidence_is_order_invariant`. On the same fixture, the old metric failed 5 of 6 shuffles.
   - **The per-record values stored in the existing smoke `predictions.jsonl` files were computed with the old metric.** The reports were regenerated (`wsh report`) for formatting only, and the records were not changed.
7. **The report table header had one column fewer than its rows.** The `dataset` cell was never labelled, so every column heading was shifted by one. Fixed and covered by a test. The four valid smoke reports were regenerated from unchanged `predictions.jsonl`; `metrics.json`, `summary.csv` and `report.md` are derived files.
8. **P3 gave an empty "not applicable" reason** for single-claim bundles (`P3 not applicable: None`). It now gives an explicit reason.
9. **C2 DEPENDS_ON agreement can be circular** (audit). Every Exp3 record now carries `dep_gold_circularity` (`same_rule` for HotpotQA, `shared_surface_cue` for MuSiQue and 2Wiki); see §5.

Unit tests at the end of the first audit: **78 passed** (`.venv/bin/python -m pytest -q`, 2026-10-10).

## 5. Design audit (2026-10-10)

### Confirmed problems
| # | problem | effect | status |
|---|---|---|---|
| A1 | `min_matched` truncates from the end and counts formatting tokens | Structured representations lose content. In smoke, answer-in-evidence was 0.89 for R0 vs 0.44 for R4/R5/R3 (R1 0.67). Ordered layouts put the final hop last, so it is cut first. Token-matched contrasts confound structure with information loss. | **Open.** Documented in EXPERIMENT_SPEC §4; a fix is proposed there and needs a decision. |
| A2 | Order-dependent `answer_in_evidence` | Biased the R1 vs R2/R3/R4 coverage comparisons | Fixed (§4.6) |
| A3 | C2 DEPENDS_ON predictor (title mention) vs HotpotQA gold (R-HPQ, title mention) | C2 precision and recall on HotpotQA are inflated by construction. On MuSiQue and 2Wiki, R-ANCHOR uses sub-answer mentions, which often coincide with titles. | Flagged per record. Agreement can only be interpreted against human-verified edges. |
| A4 | 0.5B emits no citations | Citation and grounding metrics are uninformative | Documented; needs a larger generator |
| A5 | Derived edges use fallback anchors | Claim-level endpoints are guessed for 18% of MuSiQue, 26% of 2Wiki and 20% of HotpotQA derived DEPENDS_ON edges (pilot sample; tagged `anchor_match=fallback`). Passage-level structure is unaffected. | Documented. Claim-level analyses should either be stratified by `anchor_match` or restricted to exact anchors. |
| A6 | Report table misaligned; P3 reason missing | Cosmetic, but misleading | Fixed |

### Methodological risks (not confirmed defects)
- **Leakage checks that passed:** R0, R1 and R2 use dataset passage position, never gold order (only R3 and R4 use gold order, by design). Exp4 features use predicted R4P edges, not gold edges. Exp4 splits by question. Smoke and pilot samples do not overlap.
- **Gold quality:** all reasoning orders and edges for 2Wiki and HotpotQA, and the step dependencies for MuSiQue, are `deterministic_derived` and have never been human-verified. HotpotQA sentence segmentation is dataset-supplied and sometimes splits titles ("Hey Pa! / There's a Goat on the Roof"). We keep that segmentation because supporting-fact indices refer to it, but it makes some sentence claims non-self-contained.
- **Claim faithfulness:** the LLM extractor, which is the same 0.5B model as the answerer, fragments sentences (e.g. "intervened against"), and the lexical-support check does not catch this. Exp3 C1 measures this degradation; it is not a defect in the measurement itself. A human audit of about 100 extracted claims is still needed (COMPUTE_HANDOFF item 5).
- **Relation thresholds** (CONTRADICTS ≥ 0.9 with a shared entity) were chosen by inspecting smoke edge counts, without accuracy data. R4P and C3/C4 results depend on them.
- **Length confounds in Exp2:** P1 removes text and P4 adds it. `evidence_tokens` is recorded on every record, so analyses should control for it.
- **FEVER in gold-evidence experiments** excludes NEI because it has no gold evidence, which shifts the label distribution relative to Exp0.
- **Statistics:** pairing uses only questions present under both conditions, and `n_only_a`/`n_only_b` are reported. If unavailability differs between conditions, the paired set differs between contrasts, so contrasts across representations are run on different question sets. Report the paired n for every contrast (already in the table) and do not compare deltas across contrasts with different n. With n=3, every CI is uninformative by construction.
- **Smoke/pilot separation** holds today but is not enforced. A future change to sampling could make them overlap.

## 6. Untested or unexercised

- **P7 temporal conflicts:** no verified temporal data, so it was always `unavailable`.
- **Exp3 with `human_verified` annotations:** none exist yet.
- **Retrieved-evidence Exp1** (`exp1.evidence_source=retrieved`), which Exp4 requires.
- **Exp4:** real selector training and evaluation (only the plumbing check ran, with 2 test questions).
- **Batched generation:** not implemented.
- **Hardware and models:** GPU/bf16 execution, larger models, and the `full` stage beyond policy unit tests.
- **Rates:** perturbation rates 0.1 and 0.2 (smoke used 0 and 0.4).
- **Dataset coverage:** HoVer claims outside the HotpotQA dev context (3,092 claims; these need the 2017 Wikipedia abstracts).
- **Not run:** the pilot (200/200/100/100/100 questions) and the full stage.

## 7. Pre-GPU preflight (2026-10-10 / 2026-10-11)

Scope: the investigator's preflight instructions. No pilot or full run; no model above 1B; only the cached 0.5B model and the sub-150M encoders were used.

### Changes
Details and tests are in METHODOLOGICAL_AUDIT.md §1.
- **Exp1** split into Protocol A (information-controlled) and Protocol B (budget-controlled). `min_matched` is retired.
- **R3** no longer lists supporting sentences first within a step; that ordering leaked the supporting-fact annotation.
- **Evaluation:**
  - abstention now counts as unanswered;
  - `citation_status` separates missing from invalid citations;
  - `evidence_sufficient` proxy added;
  - EM is the primary QA metric.
- **Guards:**
  - every prompt is checked to be template + evidence + question;
  - P4 excludes answer-bearing distractors, and every intervention records `answer_introduced`;
  - C2 agreement is suppressed against circular HotpotQA labels;
  - the device is part of the generation cache key;
  - smoke questions are excluded and pilot/full runs require frozen question files;
  - run directories are unique.
- **Reporting:**
  - protocol is part of every stratum;
  - contrasts are reported pooled and per edge stratum (A/B/C/D) for structural representations;
  - `n_identical_evidence`, a generator-settings consistency check, and a Protocol A/B evidence-accounting table;
  - an exploratory/confirmatory label, with Holm correction only at stage `full`.
- **Human verification:** annotation package export, validated import and overlay (`wsh annotations export|import`). The package is in `annotations/verification_v1`, blank.
- **GPU readiness:**
  - configurable device for the generator and all encoders, and deterministic CUDA settings;
  - hardware recorded in the manifest (GPU names and memory, CUDA/cuDNN, nvidia-smi);
  - path environment variables;
  - `wsh preflight`;
  - `requirements-pinned.txt`.

### Frozen artefacts
- Pilot question set: `configs/question_sets/pilot_v1.json`, sha256 `67e815648caf9bbcacd3928904b84205097f84df0e475d5a4b591ccb4b786f58`. Sizes: MuSiQue 100, 2Wiki 100, HotpotQA 50, HoVer 50, FEVER 50; seed 1; 15 smoke questions excluded.
- Verification package: `annotations/verification_v1`. 50 questions (MuSiQue 20, 2Wiki 15, HotpotQA 15), 64 proposed edges (42 exact-anchor, 22 fallback-anchor), 178 claim items. All verification fields are blank.

### Runs (smoke, 0.5B on CPU, the same 15 questions; pipeline checks only)

| run | wall clock | records | pipeline errors | notes |
|---|---|---|---|---|
| `exp1/20261010-235522_b81ab513` | 94 s | 210 (24 unavailable) | 0 | Protocol A: identical fact sets in 14/14 questions; answer-in-evidence 0.889 for every representation; overhead R0 26, R1 91, R3 122, R4 98 tokens. Protocol B (content:0.75, shared): about 37% of facts kept, 0 budget overruns, answer-bearing facts dropped are logged. |
| `exp3/20261010-235838_a0c34362` | 361 s | 75 (35 unavailable) | 0 | Oracle edge stratum per record: 7 B_derived_exact_anchor, 1 C_derived_fallback_anchor. C2 agreement suppressed for both HotpotQA questions (same rule); reported with a caveat for 2Wiki. Attribution reported per stratum. The smoke config still accepts derived statuses so that the code path runs; the pilot accepts only human_verified. |
| `exp2/20261010-235657_c2bf4194` | 102 s | 480 (110 unavailable) | 0 | 0 introduced answers; P4 excluded an answer-bearing distractor candidate for 1 question (2Wiki 3733d61a…, under both R1 and R4); label effects: 240 preserved, 46 not_guaranteed, 14 answer_removed, 70 unavailable |

Generations were not served from the old cache, because the generation cache key now includes the device. Generator settings were identical across records in both runs (`consistency`).

**What this run motivated:** at 0.75× content tokens the shared policy kept about 37% of facts. The pilot therefore pre-specifies two budget points (1.0× and 0.5×), recorded in the PILOT_PROTOCOL deviations log. This was decided on smoke questions only.

**Superseded:** the earlier smoke runs (`exp0/20261010-210157`, `exp1/20261010-125634`, `exp2/20261010-125836`, `exp3/20261010-130025`) are marked `SUPERSEDED.md`. Their raw predictions are kept; their per-record metrics use the old definitions.

**Preflight on this laptop:** `wsh preflight --config configs/pilot.yaml --tiny-generation` passed every check. The device resolved to MPS, the dataset hashes match the frozen set, and the frozen questions load with 0 excluded questions.

Reports for the three runs were regenerated with `wsh report` after the run, from unchanged `predictions.jsonl`: the reporting code gained the identical-evidence column while Exp1 was running. Final test suite: **133 passed** (2026-10-11).

## 8. Final readiness audit (2026-10-11)

**Changes:**
- Batched generation (`model.batch_size`): left padding, out-of-memory splitting, de-duplication, request-order results, batch-size-specific cache keys, and a runner queue with resume.
- GPU memory statistics in run manifests.
- Stage `gpu_pilot` (authorised, exploratory, frozen pilot questions); `full` refuses pilot questions.
- Qwen2.5-3B/7B-Instruct and Qwen3.5-9B registered with Hub-verified revisions, parameter counts and licences. Qwen3.5 thinking is disabled through the chat template.
- `--set` for `validate-config` and `preflight`; `wsh preflight --batch-check`.
- Informative-pairs and coverage-difference columns in contrasts.
- Portable smoke script.

**Runs (0.5B, smoke questions, pipeline checks only):**

| run | wall clock | records | errors | notes |
|---|---|---|---|---|
| `exp1/20261011-002549_a203d3a2` | 142 s | 210 | 0 | batch_size 8. Versus the unbatched `20261010-235522`: 210/210 identical record keys, 186/186 identical prompts, outputs and evaluations; 65 in-batch duplicates generated once. Slower than unbatched (94 s) on CPU. |
| `exp0/20261011-002812_6c9a495a` | 491 s | 75 | 0 | First Exp0 run with the current code (batched answers; extraction unbatched). 420/420 finite retrieval scores. |

**Preflight on this laptop:** `wsh preflight --config configs/pilot.yaml --batch-check 16` on MPS gave 16/16 identical outputs, with 27 s unbatched vs 52 s batched. One earlier attempt exited with code 120 and empty output, consistent with a stdout-flush failure. It did not recur and was not investigated further.

**Frozen-set structure (data only):**
- R5 = R1 identical in 25/100 MuSiQue, 56/100 2Wiki and 36/50 HotpotQA questions.
- R4 = R5 identical in 0/100 MuSiQue, 29/100 2Wiki and 25/50 HotpotQA questions.
- Protocol A violations: 0/250.
- Maximum evidence length: 1,603 tokens (Qwen2.5 tokenizer).

**Tests:** 156 passed, 1 skipped (opt-in real-model test; run separately: 30/30).
