# Final server handoff (2026-10-11)

This audit was made from the repository itself: code, git history, configs, artefacts and fresh test runs. No pilot, GPU run, or model above 1B has been executed. No weights of the 3B/7B/9B models have been downloaded. For Qwen3.5-9B only three small text metadata files were read: `config.json`, `chat_template.jinja`, and the weight index listing parameter names.

---

## A. OVERALL READINESS

# **READY_WITH_RESTRICTIONS**

The code can be transferred and the GPU pilot of **Experiment 1** (and Exp2 and Exp0 as secondary experiments) can start once:
1. you authorise a generator in writing;
2. `wsh preflight --tiny-generation --batch-check` passes on the server for that model.

Restrictions:
- Experiment 3 stays disabled until human-verified annotations exist.
- Experiment 4 stays disabled.
- Graph-structure results are "automatically derived structure" results, reported by annotation stratum.
- Citation metrics are not interpretable until a generator actually cites.

---

## B. EXPERIMENT STATUS

| exp | implemented | tested | scientifically usable | remaining limitations |
|---|---|---|---|---|
| **Exp0** baselines B0–B4 | yes | unit tests; real 0.5B smoke (batched, current code): 75 records, 0 pipeline errors, 420/420 retrieval scores finite, 491 s | **secondary**, exploratory | B4 is a labelled *reconstruction* of EG-RAG (our features and weights); claim extraction is unbatched and is the slowest step |
| **Exp1** representations R0–R5, R4P; Protocol A (information-controlled) + B (budget-controlled) | yes | unit + integration tests; real 0.5B smoke: 210 records, 0 pipeline errors, 0 equivalence violations; batched rerun identical to unbatched (186/186) | **primary.** R1−R0 usable now. R5−R1 and R4−R5 usable as effects of *automatically derived* structure, reported per stratum. | Identical-prompt dilution (R5 = R1 in 25% of MuSiQue and 56% of 2Wiki); fallback-anchored relation lines (stratum C); lexical sufficiency proxy |
| **Exp2** perturbations P1–P7 | yes | unit tests; real 0.5B smoke: 480 records, 0 pipeline errors, 0 introduced answers | **secondary** | P7 is unavailable without verified temporal data; length changes (P1/P4) must be read alongside `evidence_tokens` |
| **Exp3** component substitution | yes | unit tests; real 0.5B smoke (derived statuses accepted *for the smoke only*): 75 records, 0 errors | **not usable yet.** The pilot config accepts only `human_verified`, so every question is reported unavailable by design. | Needs the annotation package completed; LLM-extracted claims for C1/C4 must be audited for the generator actually used |
| **Exp4** adaptive selection | scaffold | leakage-guard unit tests; plumbing check only | **disabled** (`exp4.enabled: false`; the CLI refuses without it) | Gated on reproducible Exp1–3 effects in the full study |

---

## C. MODEL STATUS

Revisions, parameter counts and licences were verified against the Hugging Face Hub API on 2026-10-11. **The VRAM column is an estimate, not a measurement:** bf16 weights plus KV cache for 8 × about 2,000 tokens plus about 1–2 GB of runtime overhead. Measure it with `--batch-check`.

| model | revision | parameters | precision | supported by code | actually tested | VRAM (**estimate**) |
|---|---|---|---|---|---|---|
| Qwen/Qwen2.5-0.5B-Instruct (dev/smoke) | `7ae557604adf67be50417f59c2c2f167def9a775` | 494,032,768 | fp32 (CPU/MPS); bf16 possible on GPU | yes | **yes**: CPU and MPS; batched = unbatched | ~2–4 GB |
| Qwen/Qwen2.5-3B-Instruct | `aa8e72537993ba99e69dfaafa59ed015b17504d1` | 3,085,938,688 | bf16 | yes (`qwen2`, `Qwen2ForCausalLM`, same family as 0.5B) | **no** | ~8–10 GB |
| Qwen/Qwen2.5-7B-Instruct | `a09a35458c702b33eeacc393d103063234e8bc28` | 7,615,616,512 | bf16 | yes (`qwen2`) | **no** | ~17–20 GB |
| Qwen/Qwen3.5-9B | `c202236235762e1c871ad0ccb60c8ee5ba337b9a` | 9,653,104,368 (Hub total, incl. vision tower) | bf16 | **in principle** (see notes) | **no** | ~20–24 GB |

Licences:
- Qwen2.5-7B and Qwen3.5-9B: Apache-2.0.
- **Qwen2.5-3B: the Qwen Research License (non-commercial).** Check its terms before releasing outputs.

Notes on Qwen3.5-9B:
- **Multimodal checkpoint.** The repo is `Qwen3_5ForConditionalGeneration` (image-text-to-text); there is no `-Instruct` repo.
- **Loading is expected to work but has never been executed.** Transformers 5.12.1 maps it to the text-only `Qwen3_5ForCausalLM`, which ignores the `model.visual.*` and `mtp.*` weights and remaps the `language_model` prefix.
- **Thinking mode is disabled.** The default chat template opens a `<think>` block, so the registry sets `chat_template_kwargs: {enable_thinking: false}`, and this is unit-tested.
- **Hybrid attention.** It mixes linear-attention (Gated DeltaNet) and full-attention layers (8 of 32 are full attention), so the batched-vs-unbatched check is essential.
- **Optional kernels.** Fast linear-attention kernels (`flash-linear-attention`, `causal-conv1d`) are optional; without them transformers uses slower PyTorch paths.

**Policy:**
- Every model above 1B is blocked in `smoke` and `pilot`, even with the environment variable set.
- In `gpu_pilot` (exploratory, frozen pilot questions) and `full` (confirmatory), it is allowed only with **`WSH_COMPUTE_AUTHORIZED=1` and `--authorized-compute`** (unit-tested).
- Authorisation only unlocks the policy; nothing launches by itself.

---

## D. SERVER REQUIREMENTS (what I need from you)

1. **Written authorisation:** which generator(s) for the exploratory GPU pilot, in which order, and a GPU-hour budget.
2. **The full output of `wsh preflight --config configs/gpu_pilot.yaml --authorized-compute --tiny-generation --batch-check 16`** for each authorised model, plus `nvidia-smi`.
3. **GPU:** model, count, memory per GPU, driver and CUDA version, bf16 support, MIG or sharing.
4. **CPU, RAM, and free disk** on the HF cache, results and SQLite-cache paths (local or network filesystem; SQLite should be on local disk).
5. **Software:** OS and distribution, Python version available, whether `pip` can install a CUDA build of PyTorch, and whether internet access exists (for dataset/model fetching) or files must be staged.
6. **Scheduling:** maximum job length, preemption, whether `tmux`/`screen` or Slurm is available.
7. **Paths** you want for `HF_HOME`, `WSH_DATA_ROOT`, `WSH_RESULTS_ROOT`, `WSH_CACHE_PATH`.
8. **Annotation:** whether, and when, the human verification package can be completed (see G).

---

## E. EXECUTION PLAN (prepared; NOT executed)

```bash
# 1. Install the project on the server
git clone <your-remote-or-copied-repo> when-structure-hurts && cd when-structure-hurts
git checkout final-server-handoff                 # tag of the audited commit
python3.12 -m venv .venv && source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/<cuXXX>   # build matching the server's CUDA
pip install -r requirements-pinned.txt && pip install -e .
export HF_HOME=/data/hf WSH_DATA_ROOT=/data/wsh/raw WSH_RESULTS_ROOT=/data/wsh/results WSH_CACHE_PATH=/data/wsh/cache/wsh.sqlite
for d in musique 2wikimultihopqa hotpotqa hover fever; do wsh data fetch --dataset $d; done
for m in Qwen/Qwen2.5-0.5B-Instruct cross-encoder/ms-marco-MiniLM-L6-v2 cross-encoder/nli-deberta-v3-xsmall \
         cross-encoder/nli-deberta-v3-small BAAI/bge-small-en-v1.5; do wsh models fetch $m --stage pilot; done
python -m pytest -q                                # expect: 156 passed, 1 skipped (the opt-in real-model test)

# 2. Server preflight (no experiment is run)
wsh preflight --config configs/pilot.yaml --set model.device=cuda --tiny-generation --batch-check 16

# 3. Tiny GPU integration test (0.5B, 15 smoke questions, about minutes; pipeline check only)
WSH_RUN_SLOW=1 WSH_TEST_DEVICE=cuda WSH_TEST_DTYPE=bfloat16 python -m pytest -q -s tests/test_batching.py -k real
wsh run exp1 --config configs/smoke.yaml --set model.device=cuda model.batch_size=8

# 4. First controlled exploratory pilot: Exp1, one authorised generator (after your written go-ahead)
export WSH_COMPUTE_AUTHORIZED=1
M=Qwen/Qwen2.5-7B-Instruct
wsh models fetch $M --stage gpu_pilot --authorized-compute
wsh preflight --config configs/gpu_pilot.yaml --authorized-compute --set model.model_id=$M --tiny-generation --batch-check 16
wsh run exp1 --config configs/gpu_pilot.yaml --authorized-compute --set model.model_id=$M
#    (if batch-check fails: append  model.batch_size=1  to --set)

# 5. Resume an interrupted experiment (same config and --set values; the config hash must match)
wsh run exp1 --config configs/gpu_pilot.yaml --authorized-compute --set model.model_id=$M \
    --resume $WSH_RESULTS_ROOT/gpu_pilot/exp1/<run_id>

# 6. Statistical reports (recomputed from predictions.jsonl; written into the run directory)
wsh report $WSH_RESULTS_ROOT/gpu_pilot/exp1/<run_id>      # -> report.md, metrics.json, summary.csv
```

---

## F. SCIENTIFIC BLOCKERS (before pilot results can be trusted)

No implementation defect is known that invalidates the primary comparisons. What must hold before trusting the results:

1. **Batch equivalence on the server.** `--batch-check` must report 16/16 identical outputs for the model and device actually used; otherwise use `batch_size 1`. It is verified so far only on CPU and MPS with the 0.5B model.
2. **Qwen3.5-9B** must load and generate correctly as text-only, with thinking off: check `--tiny-generation` output and the first records. **Run it last.**
3. **Graph contrasts (R1−R5, R5−R4)** must be described as effects of *automatically derived* structure. They become effects of *verified* structure only on human-verified (stratum A) questions.
4. **Read every contrast with its `n_identical_evidence`, informative-pairs estimate and coverage difference.** An EM difference that comes with a coverage difference is a format/generation effect, not a reasoning effect.
5. **Citation and grounding metrics** must not be interpreted for any generator that rarely cites. The 0.5B cited in 5 of 671 answered smoke records.

**Validity of the three primary comparisons:**

| comparison | status | why |
|---|---|---|
| **R0 vs R1** (passages vs claims) | **valid now** | Identical facts verified on all 250 frozen MuSiQue/2Wiki/HotpotQA questions (0 violations). No annotation dependency. R1 repeats the source title per claim; this is measured overhead, not new information. Context-dependent sentences (85–96% of questions) are part of the treatment and are recorded. |
| **R1 vs R5** (graph-derived ordering) | **valid as a derived-structure effect** | R5's order comes from passage-level dependencies derived from dataset decompositions. Fallback anchors change only claim-level endpoints, not passage order. Diluted: identical prompts in 25/100 MuSiQue and 56/100 2Wiki; informative pairs are reported. |
| **R5 vs R4** (explicit relations) | **valid for stratum B; stratum C needs human verification** | R4 shows explicit sentence-to-sentence DEPENDS_ON lines. For fallback-anchored edges (33% of MuSiQue and 25% of 2Wiki pilot questions) those endpoints are guesses, so they are reported separately. On 2Wiki and HotpotQA comparison questions there are no edges (R4 = R5). Only DEPENDS_ON is shown for gold structure; R4P's predicted SUPPORTS/CONTRADICTS labels are secondary. |

**Statistics.**
- Question-level paired bootstrap (2,000 resamples), on the same questions only.
- R2 seeds are averaged within question.
- Holm correction over the 6 planned primary tests, at stage `full` only. Every `pilot` and `gpu_pilot` result is labelled exploratory.
- The bootstrap p-value is an approximation; the CIs are primary.

---

## G. HUMAN ANNOTATIONS

- **Location:** `annotations/verification_v1/`. Start with `GUIDE.md`. Fill in `paths.csv`, `edges.csv` and `claims.csv`; `review.md` is the readable view.
- **Outstanding:** 50 of 50 questions (MuSiQue 20, 2Wiki 15, HotpotQA 15):
  - 50 path judgements;
  - 64 edge verdicts (42 exact-anchor, 22 fallback-anchor);
  - 178 claim items.
  - **0 completed.** All fields are blank (unit-tested). Estimated effort: 3–5 hours.
- **Import:** `wsh annotations import --package annotations/verification_v1 --out annotations/verified/verification_v1.jsonl`. It validates entries, links them to the dataset by content digest, and never overwrites. Then set `verified_annotations:` in the config.

| needs human-verified annotations | why |
|---|---|
| **Exp3** (all conditions) | The pilot accepts only `human_verified` as ground truth |
| R5−R4 and R1−R5 described as effects of **verified** structure (stratum A) | Derived edges are not ground truth |
| C2 relation-prediction accuracy | HotpotQA labels are circular; other derived labels share surface cues |
| Claim-faithfulness statements (C1/C4) | Rule and LLM extraction quality must be audited; LLM claims must come from the generator actually used |
| P7 temporal conflicts | Needs a verified temporal specification (not part of the package) |

Not needed to *start* Exp1 Protocol A, Exp1 Protocol B, Exp2 (P1–P6) or Exp0.

---

## H. FINAL RECOMMENDATION

1. **Is the code ready to be transferred to the GPU server?** **Yes.** 156 tests pass, 0 fail, 1 skipped (the opt-in real-model test, run separately: passed). The repository is a clean local git commit with tag `final-server-handoff`; nothing has been pushed. No Mac-specific paths remain: macOS memory probing is guarded with a Linux `/proc/meminfo` fallback, and the smoke script is portable.
2. **Is batching implemented and tested?** **Yes, on CPU and MPS.**
   - Implemented: configurable `model.batch_size`, left padding with attention masks, length-sorted chunks, de-duplication of identical prompts, request-order results, out-of-memory splitting, batch-size-specific cache keys, a runner queue with resume, and budget caps.
   - Tested: 12 dedicated tests; real 0.5B 30/30 on CPU and 16/16 on MPS; end-to-end Exp1 186/186 identical to unbatched.
   - **Not yet verified on CUDA/bf16 or for the 3B/7B/9B models.** `--batch-check` does that on the server.
   - Batching was *slower* than unbatched on CPU and MPS, so measure throughput on the GPU.
3. **Remaining software blockers?** None known. Two items need checking on the server, not code changes: batch equivalence on CUDA, and Qwen3.5-9B text-only loading.
4. **Remaining methodological blockers?**
   - None for Exp1 R0−R1 or for the derived-structure versions of R1−R5 and R5−R4.
   - **Blocked until annotation:** verified-structure claims and Exp3.
   - **Blocked until a model that cites:** citation and grounding claims.
5. **Should we run the initial GPU pilot now?**
   - Transfer the code and run steps E1–E3 (install, preflight, tiny 0.5B GPU check) now.
   - Run the exploratory GPU pilot (E4) **after** three things: your written authorisation of the generator, a passing preflight/batch-check on the server, and your sign-off on `docs/PILOT_PROTOCOL.md`, which freezes at the first pilot generation.
6. **Which experiment first?** **Experiment 1** (primary question; Protocol A and B). Then Exp2, then Exp0. Exp3 only after annotations are imported.
7. **Which model first, and why?** **Qwen2.5-7B-Instruct.**
   - Apache-2.0 licence.
   - Standard `qwen2` text architecture, the same family and template as the 0.5B model, where batching and the whole pipeline are verified.
   - No thinking mode and no multimodal loading path.
   - Estimated to fit a single 24 GB GPU in bf16.
   - Used in the predecessor EG-RAG evaluation.
   
   Then Qwen2.5-3B-Instruct (cheaper; research licence). Then **Qwen3.5-9B last**: text-only loading is unverified, it has hybrid linear attention, and thinking must stay off.
8. **Which experiments must remain disabled?**
   - Exp4.
   - Exp3, until human-verified annotations are imported.
   - P7 (no verified temporal data).
   - The `full` (confirmatory) stage, until the pilot is analysed, sample sizes are set and a fresh frozen question set is drawn.
9. **What information do I need before launching?** Everything in section D:
   - authorised generator(s) and GPU-hour budget;
   - the server preflight output;
   - GPU and server specifications;
   - paths and scheduler limits;
   - the annotation plan;
   - your sign-off on PILOT_PROTOCOL.md.

---

### Reproducibility facts (this audit)

- **Tests:** `pytest -q` → **156 passed, 0 failed, 1 skipped** (`test_real_qwen05b_batched_matches_unbatched_on_smoke_prompts`, opt-in via `WSH_RUN_SLOW=1`; run separately on CPU: passed, 30/30).
- **Experiments actually executed** (all smoke stage, Qwen2.5-0.5B, the same 15 smoke questions, pipeline checks only):
  - Exp0: `20261010-124651` (INVALID: reranker NaN), `20261010-210157` (superseded), `20261011-002812` (valid, batched, current code).
  - Exp1: `20261010-125634` (superseded), `20261010-235522` (valid), `20261011-002549` (valid, batched).
  - Exp2: `20261010-125836` (superseded), `20261010-235657` (valid).
  - Exp3: `20261010-130025` (superseded), `20261010-235838` (valid).
  - Exp4: plumbing check only.
- **Never executed:**
  - any `pilot`, `gpu_pilot` or `full` run;
  - any CUDA run;
  - the 3B/7B/9B models;
  - Exp1 with retrieved evidence;
  - Exp3 with human-verified annotations;
  - P7 with data;
  - Exp4 training;
  - human annotation.
- **Commit:** see `git log -1` (tag `final-server-handoff`). Uncommitted changes at handoff: none.
