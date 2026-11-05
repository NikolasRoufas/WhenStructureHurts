# Final experimental report: journal-revision experiments

*When Structure Hurts: Understanding Evidence Loss in Retrieval-Augmented Reasoning*. Prepared for
Prof. Andreas Kanavos, 2026-11-05. Branch `experiments/andreas-journal-revision`; the commit is given in §6.

## Executive summary

| experiment | status | what it establishes |
|---|---|---|
| **A** human verification of predicted contradictions | **Prepared; human labels pending.** Package v2 (300 pairs) audited and reused unchanged; tools, guidelines, agreement / adjudication / precision pipeline and tests done. | Nothing yet about precision. No label has been produced by any model or heuristic. |
| **B** selective removal of verified-false contradictions | **Prepared; blocked on human labels.** Tier-1 selection (300 confirm2 questions) frozen; package v3 (666 pairs) built and verified; the conditions R4P_FO_SC / R4P_FO_SN implemented and tested; run config and analysis written. | Nothing yet. |
| **C** third reader (OLMo-2-1124-7B-Instruct) on confirm2_v1 | **Executed on the server** (6,400 questions × 2 conditions, GPU 1). | Contradiction lines **lower accuracy for a third, independently trained reader too**. EM: −3.2 pts (2Wiki) and −2.1 pts (HotpotQA), both confirmed. Lenient: −1.9 (2Wiki, Holm p = 0.050, so inconclusive) and −5.8 (HotpotQA, confirmed). The effect is smaller than Qwen's on 2Wiki and the same size on HotpotQA. |
| **D** retrieved-evidence extension | **NO-GO (deferred)**, decided from the existing retrieval results; no inference spent. A conditional design is specified. | The existing retrieval run already shows the contradiction-line effect: about −2.3 EM points on both datasets, CIs excluding 0. |

## 1. Repository and server inventory

Full details: `audits/INVENTORY.md`.

**Repository**
- Start: `main` at `3fb2080`, the code-only release. The research record is tag `research-record-revision2`
  (`9bfae0e`).
- The manuscript's artifact paths exist in that tag under `research_outputs/`. The `revision-1` branch named in
  the README does not exist on the remote.

**Server: `interstellar`**
- 2 × RTX 5000 Ada, 32 GB each. All new inference ran on **physical GPU 1 via MPS**, UUID-checked; GPU 0 was
  not used.
- torch 2.12.1+cu130, transformers 5.12.1, Python 3.12.
- New outputs: `/data/roufas/wsh_andreas/`. Original outputs: `/data/roufas/wsh_campaign/results/`.

**Originals unchanged.** The 91 original output files (all 15 `predictions.jsonl`, manifests, metrics, the
revision analysis directory and the annotation keys) were hashed at the start and re-verified before the push
(§6).

**Stage-0 audit** (`audits/stage0_audit.json`):
- Relation prediction is deterministic: R4P_FO prompts were byte-identical across two independent earlier runs
  for 4,976 of 4,976 questions.
- The earlier Mistral run had 1 condition-dependent overflow and 139 / 157 answers cut at 64 tokens; this was
  not previously reported.

## 2. Experiment A: human contradiction verification

**Status: annotation pending (genuine external dependency).** 0 of 300 pairs are labelled in either annotator file.

**Package v2, reused unchanged.** The audit found it valid and representative of a defined population:

- **Population.** 7,721 unordered fact pairs joined by a CONTRADICTS line rendered in a Qwen R4P_FO prompt on
  confirm_v1, in 2,425 questions: 6,820 in 2Wiki and 901 in MuSiQue.
- **Sample.** 300 pairs in 252 questions (1–5 per question), drawn as 5 strata × 2 datasets × 30.
  - Strata: restored, abstained_other, top and bottom NLI-confidence quartiles, no-failure control.
  - Several strata are defined by downstream outcomes (annotators are blind to them), and MuSiQue is
    over-represented.
- **Reproducible.** Re-running the sampler with seed 0 reproduces all 300 pairs exactly.
- **Inclusion probabilities.** Estimated from 2,000 simulations of the same sampler; every sampled pair has
  π̂ > 0, ranging 0.005–0.60.
  - 1,181 population pairs (15 %, almost all 2Wiki) lie in no stratum.
  - So the design-weighted estimate covers the other 85 %, which is stated in the output.
- **Integrity.** Hashes match the record, there are 0 duplicate ids and 0 empty contexts. 179 of 300 are
  same-passage pairs. 33 text pairs recur across questions; they are labelled independently.

**What is ready:**
- `annotation/ANNOTATION_GUIDELINES.md`: three-class definitions, worked examples (entity identity, dates,
  numbers, negation, coreference, context), an optional error-category tag, and a no-AI rule.
- `annotation/annotation_tools.py`:
  - `validate`: refuses invalid, unsigned or non-independent labels.
  - `agreement`: raw agreement and Cohen's κ, 3-class, with question-clustered CIs; 3×3 and 7×7 confusion
    matrices; the adjudication package.
  - `finalize`: refuses unresolved disagreements.
  - `precision`: strict, excluding-ambiguous, and bounds versions; per stratum with Wilson CIs; design-weighted
    Hájek estimate with a cluster bootstrap; error categories, described only when n < 20.

**Workload.** Two annotators label 300 pairs (v2) and 666 pairs (v3), 966 pairs each, plus adjudication. At
about 1 minute per pair (both steps), that is roughly 16 hours per annotator.

## 3. Experiment B: selective removal

**Status: blocked on adjudicated human labels for package v3.** No Experiment-B generation was run.

**Population and selection**
- Eligible: confirm2 questions with ≥ 1 rendered CONTRADICTS line in Qwen R4P_FO and the 40-line relation cap
  not binding. That is 1,481 2Wiki questions (9 excluded by the cap) and 1,295 HotpotQA questions.
- Selection used evidence fields only (no outcome was read): a seed-11 permutation, giving Tier 1 = 150 + 150
  questions and Tier 2 = the next 150 + 150.
- Package v3 holds all 666 Tier-1 pairs (441 2Wiki, 225 HotpotQA).
  - Context passages are the full dataset passages, independently checked against the loader: 1,332 / 1,332
    match.
  - There is no overlap with package v2.

**Conditions**, implemented in `src/wsh/representations/relation_controls.py`:

| | condition | relation lines |
|---|---|---|
| A | R4P_FO | all predicted lines |
| B | R4P_FO_SC | minus the lines adjudicated *false* |
| C | R4P_FO_NC | minus every CONTRADICTS line |
| D | R4P_FO_SN | false lines relabelled RELATED_TO (sensitivity) |

Both new conditions refuse any question with an unlabelled pair or a binding cap. Tests and the analysis assert:
- identical question, facts, order and id map;
- only the intended relation lines differ;
- B ≡ A when no line is false, and B ≡ C when all lines are false.

A and C are regenerated in the same run and compared with the original confirm2 outputs.

**Analysis** (`selective_removal/analysis.py`, written before any label exists):
- primary family: B−A, C−A, C−B, pooled with resampling within dataset, Holm over the 3 tests;
- secondary: per dataset, D−A, D−B, abstention, wrong-answer rate, coverage, full 3×3 transitions;
- observational: by label composition.

**Expected precision** (Tier 1, n = 300, paired SD ≈ 0.3): the CI half-width is about ±3.4 EM points.

## 4. Experiment C: replication with OLMo-2-1124-7B-Instruct

**Status: executed on the server.**
- **Run:** 12,800 / 12,800 records (6,400 questions × 2 conditions), 0 generation errors, 0 prompt overflows.
  Run `/data/roufas/wsh_andreas/results/revision/exp1/20261105-073845_99c9a978`.
- **Hardware and time:** physical GPU 1 (RTX 5000 Ada, via MPS), 9,185 uncached generations, **3.39 GPU-hours**,
  2026-11-05 07:38–11:02 UTC. The two smoke runs took about 3 more minutes.
- **Code:** `54a1c73` (recorded as `-dirty` because of one untracked helper script). The recorded `src/` +
  `configs/` tree hash `bce1a4a2…` equals that of the pushed branch.

### Configuration

| item | value |
|---|---|
| model | `allenai/OLMo-2-1124-7B-Instruct`, revision `470b1fba1ae01581f270116362ee4aa1b97f4c84`, 7,298,617,344 parameters (checked after loading), Apache-2.0, ungated |
| why this model | Different lineage from Qwen and Mistral; registered as a second-reader candidate since revision-1. Llama-3.1-8B-Instruct and Gemma-3-12B-it are gated (HTTP 401, no token on the server). |
| precision | bf16, no quantisation |
| decoding | greedy (`do_sample=False`, 1 beam), batch size 1, `max_new_tokens` 64, `max_time` 60 s; torch seed 0, cuDNN deterministic, `CUBLAS_WORKSPACE_CONFIG=:4096:8` |
| input limit | 4,032 tokens (4,096 positions − 64). Longest prompt: 3,329 OLMo tokens, so no prompt was skipped (`audits/expC_token_preflight.json`). |
| prompt | frozen `qa-v2` through the OLMo chat template (native system role), plus the `Answer:` prefill |
| questions | `confirm2_v1` unchanged: 2,600 2Wiki + 3,800 HotpotQA |
| conditions | R4P_FO and R4P_FO_NC |
| software | Python 3.12.3, torch 2.12.1+cu130, transformers 5.12.1, tokenizers 0.22.2 |

**Integrity**
- Every user prompt is **byte-identical to the Qwen confirm2 prompt** for the same question and condition:
  2Wiki 2,600 / 2,600 and HotpotQA 3,800 / 3,800 in both conditions.
- Prompts are identical between the two conditions exactly when no CONTRADICTS line is rendered (asserted).
- Preflight: two independent smoke runs were byte-identical (80 / 80).

**Measurement note.** OLMo-2 often ignores the two-line format (full sentences, `Evidence:` on the answer
line), and the frozen parser counts those answers wrong. EM is therefore near its floor: 4–12 %, against 46–61 %
lenient. This was seen in the preflight, before any contrast was computed, and handled by the dated amendment
(protocol §7): EM kept as specified, lenient match added as a second primary family.

### Primary results: affected questions

Questions with ≥ 1 CONTRADICTS line. Δ = R4P_FO − R4P_FO_NC; paired bootstrap 95 % CI; Holm over the 2
datasets within each family.

| dataset | n | family | lines off | lines on | Δ | 95 % CI | Holm p | decision |
|---|---|---|---|---|---|---|---|---|
| 2Wiki | 1,490 | EM | 0.0705 | 0.0389 | **−0.0315** | [−0.0436, −0.0201] | < 0.001 | confirmed |
| 2Wiki | 1,490 | lenient | 0.4819 | 0.4624 | −0.0195 | [−0.0383, −0.0007] | 0.050 | inconclusive (p not < 0.05) |
| HotpotQA | 1,295 | EM | 0.1104 | 0.0896 | **−0.0208** | [−0.0363, −0.0054] | 0.008 | confirmed |
| HotpotQA | 1,295 | lenient | 0.6062 | 0.5483 | **−0.0579** | [−0.0772, −0.0386] | < 0.001 | confirmed |

"< 0.001" means no bootstrap resample crossed 0 (p_boot = 0 at 2,000 resamples).

### Secondary metrics

Affected questions:

| dataset | abstention off → on | Δ abstention | wrong off → on | Δ wrong | coverage off → on | Δ EM, answered under both |
|---|---|---|---|---|---|---|
| 2Wiki | 0.113 → 0.136 | +0.022 [+0.005, +0.039] | 0.816 → 0.826 | +0.009 [−0.011, +0.030] | 0.887 → 0.864 | −0.040 [−0.053, −0.028] (n = 1,220) |
| HotpotQA | 0.058 → 0.134 | **+0.076 [+0.058, +0.095]** | 0.832 → 0.776 | −0.056 [−0.078, −0.034] | 0.942 → 0.866 | −0.026 [−0.042, −0.009] (n = 1,092) |

All questions, including those whose two prompts are byte-identical:

| dataset | n | Δ EM | Δ lenient | Δ abstention |
|---|---|---|---|---|
| 2Wiki | 2,600 | −0.018 [−0.025, −0.012] | −0.011 [−0.022, −0.001] | +0.013 [+0.003, +0.022] |
| HotpotQA | 3,800 | −0.007 [−0.012, −0.002] | −0.020 [−0.027, −0.012] | +0.026 [+0.020, +0.033] |

**Transitions on affected questions** (off → on; C = correct, W = wrong, A = abstained). Full tables, including
the all-questions population, are in `model_replication/results/analysis/expC_olmo2_transitions.csv`.

| dataset | scoring | C→C | C→W | C→A | W→C | W→W | W→A | A→C | A→W | A→A |
|---|---|---|---|---|---|---|---|---|---|---|
| 2Wiki | EM | 42 | 59 | 4 | 10 | 1,109 | 97 | 6 | 62 | 101 |
| 2Wiki | lenient | 599 | 64 | 55 | 67 | 490 | 46 | 23 | 45 | 101 |
| HotpotQA | EM | 79 | 56 | 8 | 28 | 929 | 120 | 9 | 20 | 46 |
| HotpotQA | lenient | 657 | 45 | 83 | 42 | 348 | 45 | 11 | 18 | 46 |

Under lenient scoring, the loss comes mainly from correct answers becoming abstentions: C→A 55 vs A→C 23
(2Wiki), and 83 vs 11 (HotpotQA). C→W and W→C are nearly balanced. The EM transitions also show C→W ≫ W→C
(59 vs 10; 56 vs 28). With lines shown, OLMo more often answers in a form the frozen parser rejects.

**Sensitivity: questions with no answer cut at 64 tokens.** Truncation was frequent: 2Wiki 359 (off) / 405 (on),
HotpotQA 143 / 170. Excluding every affected question truncated in either condition (555 2Wiki and 263 HotpotQA
questions) gives:
- 2Wiki: EM −0.025 [−0.039, −0.010]; lenient **−0.026 [−0.048, −0.006]**; abstention +0.034;
- HotpotQA: EM −0.023 [−0.040, −0.008]; lenient −0.054 [−0.078, −0.031]; abstention +0.077.

All are negative. The 2Wiki lenient estimate is slightly larger once truncated answers are removed.

### Comparison with the other readers (not pooled)

| reader | questions | 2Wiki Δ EM | 2Wiki Δ lenient | 2Wiki Δ abst | second dataset Δ EM | Δ lenient | Δ abst |
|---|---|---|---|---|---|---|---|
| Qwen2.5-7B (confirmatory test 2) | confirm2_v1 (same questions) | −0.077 [−0.095, −0.061] | −0.079 [−0.097, −0.062] | +0.089 | HotpotQA −0.053 [−0.067, −0.039] | −0.060 [−0.074, −0.045] | +0.076 |
| **OLMo-2-7B (this work)** | confirm2_v1 | −0.032 [−0.044, −0.020] | −0.019 [−0.038, −0.001] | +0.022 | HotpotQA −0.021 [−0.036, −0.005] | −0.058 [−0.077, −0.039] | +0.076 |
| OLMo − Qwen (paired, same questions; exploratory) | | +0.046 [+0.026, +0.065] | +0.059 [+0.036, +0.084] | −0.066 [−0.089, −0.044] | +0.032 [+0.012, +0.053] | +0.002 [−0.023, +0.026] | 0.000 [−0.024, +0.024] |
| Mistral-7B-v0.3 (revision-2) | confirm_v1 (different questions) | −0.054 [−0.069, −0.039] | −0.079 [−0.097, −0.063] | +0.081 | MuSiQue −0.026 [−0.041, −0.010] | −0.057 [−0.079, −0.036] | +0.105 |

Qwen numbers come from the original confirm2 run (re-derived by this analysis; they equal the published
`confirm2_summary.json`). Mistral numbers come from `research_outputs/revision2/r2/reader2.csv` (affected
questions, `contra_lines>=1`).

**Reading**
- **Direction.** All three readers lose accuracy and abstain more when the predicted CONTRADICTS lines are shown.
  For OLMo this holds on every metric and both datasets, and in the truncation sensitivity analysis.
- **Size.**
  - On HotpotQA, OLMo's lenient and abstention effects equal Qwen's on the same questions: interaction
    +0.002 [−0.023, +0.026], which is not evidence of equality but is a near-zero point estimate.
  - On 2Wiki, OLMo's effect is clearly smaller than Qwen's: interaction +4.6 EM points, mainly because OLMo's
    abstention rises much less (+2.2 vs +8.9 points).
- **Limits.**
  - This is a new reader on reused questions, not an independent sample.
  - OLMo's EM is near its floor, so its EM effects are compressed. The lenient family is the more informative
    one for this reader.


## 5. Experiment D: retrieved evidence

**Decision: NO-GO now (deferred).** Full analysis in `retrieval_extension/GO_NO_GO.md`.

- **Already shown:** the existing retrieval run (500 MuSiQue + 500 2Wiki, top-4 BM25 + reranker) shows the
  contradiction-line effect. R4P − R4P_NC: −0.022 [−0.038, −0.008] and −0.024 [−0.046, −0.004]. 74–78 % of
  questions carry a contradiction line.
- **Pools:** unused eligible questions number 70 for MuSiQue, 5,057 for 2Wiki and 2,193 for HotpotQA (bridge
  only).
- **Little new information:** a new run would mostly narrow intervals around a known effect, cannot replicate
  MuSiQue, and does not address the open questions (A, B).
- **If requested:** a 1,000 + 1,000 fixed-order design (R5, R4P_FO, R4P_FO_NC, R4P_FO_CN) is specified for a
  later prospective run. It would cost about 2–3 GPU-hours.

## 6. Reproducibility audit

**Commit and branch**
- Branch `experiments/andreas-journal-revision`. Commits are listed with `git log 3fb2080..HEAD`; the final SHA
  is in the closing message.
- Every result file named here is in the branch under `experiments/andreas_revision/`.

**Experiment C artifacts** (`model_replication/results/`)

| file | content | sha256 (first 16) |
|---|---|---|
| `predictions_full.jsonl.gz` | complete raw records; decompresses to the server's `predictions.jsonl` | gz `1dd6f8576fc2a63f`; jsonl `ce2701f19dc2c691` |
| `expC_olmo2_outputs.jsonl.gz` | compact per-record outputs (text, parsed answer, EM, lenient, state, tokens, finish reason, prompt hash) | `e3de1fc2e4dc99b0` |
| `analysis/expC_olmo2_summary.json`, `…_contrasts.csv`, `…_transitions.csv` | this report's tables | |
| `confirm2_analysis_em/` | output of the unchanged `scripts/revision/confirm2_analysis.py` | |
| `run_20261105-073845_99c9a978/` | manifest (environment, packages, GPU, determinism, timings), resolved config, metrics | |
| `smoke_runs/`, `../../audits/expC_smoke_check.json`, `../../audits/expC_token_preflight.json` | preflight | |
| `status.log`, `gpu_exp1_20261105-073840.csv` | launcher log and GPU utilisation every 30 s | |

**Other inputs and outputs**
- **Inputs:** `configs/question_sets/confirm2_v1.json` (unchanged); Qwen confirm2 predictions sha256
  `55589124fa5023f7…`.
- **Annotation:**

| file | sha256 (first 16) | note |
|---|---|---|
| package v2 CSVs | `2278363bd657a7ce` / `344b5d20503ecf3d` | equal to the research record |
| package v3 CSVs | `827310af674c8d3e` / `10845f6982ae64e8` | |
| v2 key | `626855cd6b9a7ebf` | server only |
| v3 key | `b06c064a528bf2f7` | server only |
| v2 population / inclusion-probability file | `89389290ab655730` | server only until labelling ends |

- **Experiment B selection:** `selective_removal/expB_tier{1,2}_qids.json`; Tier 1 sha256 `4467650627e566c7`.
- **Originals:** `audits/verify_originals.py verify audits/original_artifact_hashes.json` reports 0 of 91 files
  changed or missing (run before the push).
- **Tests:** 186 passed, 13 skipped (the skipped ones need local datasets).
  - The new tests cover: the selective-removal conditions (facts, order and question identical; only target lines
    change; incomplete labels and a binding cap refused); the importer's refusals; agreement and adjudication;
    design-weighted precision against a hand calculation; and that selection reads no outcome field.
  - They also check that the bootstrap reproduces the project's `paired_bootstrap` exactly, and that the
    Experiment-B analysis accepts pipeline-rendered records and rejects tampered ones.
- **Commands:** `experiments/andreas_revision/README.md`.


## 7. Scientific conclusions

| original claim | status after this work |
|---|---|
| Showing predicted CONTRADICTS lines lowers EM (confirmatory test 2, Qwen) | **Strengthened.** It generalises to a third, independently trained reader on the same questions. OLMo-2: 3 of 4 pre-specified tests confirmed in the predicted direction; the fourth (2Wiki lenient) is negative with a CI just excluding 0 but Holm p = 0.050. No opposite-direction result. |
| The effect works mainly through abstention | **Supported for OLMo-2**, more weakly on 2Wiki: abstention +2.2 / +7.6 points; under lenient scoring, correct → abstain transitions dominate. |
| The effect has a similar size across readers | **Qualified.** On HotpotQA OLMo-2 matches Qwen closely. On 2Wiki it is less than half of Qwen's (paired interaction +4.6 EM points, CI excluding 0). The size depends on the reader. |
| The harmful contradiction lines are mostly *false* contradictions | **Unverified.** No human label exists yet (Experiments A, B). Nothing here supports or contradicts it. |
| Removing only false contradictions would restore accuracy | **Unverified.** Experiment B is ready but needs adjudicated labels. |
| The effect holds under real retrieval | **Unchanged.** Supported by the existing exploratory retrieval run; no new retrieval run (D: NO-GO). |


## 8. Remaining limitations

- **No human labels yet.** Experiments A and B cannot report any precision or causal result. Nothing in this
  report should be read as evidence that predicted contradictions are mostly false or mostly genuine.
- **Experiment C reuses questions.** It is a cross-reader replication on the same questions as confirm2 (Qwen),
  not an independent sample.
  - Its reader often ignores the answer format, so EM is near its floor. This was handled by the pre-run
    amendment (lenient match as a second primary family), but EM-based comparisons with Qwen and Mistral should
    be read with that in mind.
- **Gated models not run.** Llama-3.1 and Gemma-3, Andreas's preferred readers, are gated, and no Hugging Face
  access exists on the server.
- **Different hardware path.** New runs used GPU 1 via MPS; the originals used GPU 0 directly. Within-run
  comparisons are unaffected; Experiment B regenerates its own A and C for that reason.
- **Raw predictions live only on the server** (not in Git or LFS); hashes are recorded.

## 9. Recommendations

1. **Recruit two annotators now and start package v2 (300 pairs), then v3 (666 pairs).**
   - This is the only remaining blocker for the paper's central causal question: are the harmful contradictions
     false, and does removing only those help?
   - Budget about 16 hours per annotator, plus adjudication.
   - Everything else (validation, agreement, adjudication, precision, the Experiment B run and its analysis) runs
     with one command each. The Experiment B run takes about 0.5 GPU-hours.
2. **Run Experiment B on Tier 1 once v3 is adjudicated.** Add Tier 2 only if the decision is made before any
   label is inspected.
3. **For the manuscript** (not changed in this phase): Experiment C can be reported as a cross-reader replication
   on reused questions. Report both scoring families, the format-compliance caveat for OLMo-2, the smaller 2Wiki
   effect, and the 64-token truncation.
4. **If a gated model is wanted** (Llama-3.1-8B or Gemma-3-12B): accept its licence on Hugging Face, put a
   read token on the server, and rerun `model_replication/configs/olmo2_confirm2_full.yaml` with `model_id`
   changed (about 3.5 GPU-hours).
   - For Gemma-3-12B, check memory: about 24 GB in bf16 fits the 32 GB GPU.
5. **Archive the original raw predictions off the server** (3.3 GB; currently their only copy), for example as a
   release asset or institutional storage, and record the location in the README. Also fix the README's
   reference to a non-existent `revision-1` branch.
6. **Journal choice.** Decide after Experiments A and B. With them, the paper makes a causal claim about relation
   errors that suits TACL or TMLR. Without them, it is a well-replicated empirical finding with an open mechanism,
   which fits IP&M or KAIS better.

