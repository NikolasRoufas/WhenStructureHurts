# Revision experiment log (revision-1 and revision-2)

All runs: Qwen2.5-7B-Instruct `a09a3545`, bf16, batch size 1, greedy, physical GPU 0 of `interstellar` (bus `01:00.0`, MPS bypassed), launched through `scripts/campaign/run.sh`. Stage `revision` is exploratory by construction; the reporting code stamps every output with that banner. The design of every run was committed in `docs/REVISION_PROTOCOL.md` (`34356e5`) before it was launched. Times are UTC (local time is UTC+3).

## Runs

| # | run | config (name, hash) | commit | started → finished | records (generated uncached) | wall clock | status |
|---|---|---|---|---|---|---|---|
| 1 | `revision/exp1/20261012-200925_a2e6e3a8` | `configs/revision_relation_controls.yaml` (`rev-relation-controls-v1`, `a2e6e3a8…`) | `ceb8802` | 20:09 → 21:09 | 39,808 (7,043) | 3,629 s | completed, 0 errors |
| 2 | `revision/exp1/20261012-210958_37616258` | `configs/revision_retrieval.yaml` (`rev-retrieval-v1`, `37616258…`) | `8423203` | 21:09 → 22:09 | 14,000 (7,062) | 3,584 s | completed, 0 errors |
| 3 | `revision/exp1/20261012-221036_8a903b43` | `configs/revision_noabst.yaml` (`rev-noabst-v1`, `8a903b43…`) | `8423203` | 22:10 → 22:37 | 4,000 (3,457) | 1,638 s | completed, 0 errors |
| — | second reader (Mistral-7B-Instruct-v0.3 or OLMo-2-1124-7B-Instruct) | `configs/revision_second_reader.yaml` | — | — | — | — | **not run: needs authorisation to download a new model** |

Runs 1 and 3 reuse cached generations for prompts byte-identical to earlier confirmatory prompts (R4, R5, R4P under `qa-v2`), which is why "generated uncached" is below "records".

## GPU-hour ledger (cumulative, campaign ceiling 24 h, never reset)

| item | GPU-h |
|---|---|
| campaign before revision (driver wall-clock; `docs/RUN_STATUS.md`) | 9.53 |
| run 1, fixed-order controls | 1.01 |
| run 2, retrieved evidence | 1.00 |
| run 3, prompt factor | 0.45 |
| dry runs (CPU only, `--dry-run`, no generation) | 0.00 |
| **total** | **≈ 11.99 of 24** |

## Chronology and decisions

1. **Baseline audit** (`scripts/audit/verify_claims.py`). Every confirmatory number in the draft was recomputed from saved predictions; all reproduced. Two prose errors were found and fixed (2Wiki unanswered rate 24 % → 19 %; equivalence wording). See `docs/REVISION_BASELINE_AUDIT.md`.
2. **Controls implemented** (`src/wsh/representations/relation_controls.py`; tests in `tests/test_relation_controls.py`). C4 (human-verified relations) was not built because no human labels exist.
3. **Run 1 launched** after a CPU dry run on the server.
4. **Retrieval sample drawn** (`retr_v1`, seed 3) only after `docs/REVISION_PROTOCOL.md` was committed. A dry run of the retrieval config under Protocol B crashed (`KeyError` in the fixed order once the budget dropped facts); fixed in `91a3ab2` with a regression test before run 2 was launched.
5. **Run 2 and run 3** launched back to back.
6. **Analyses:** `scripts/revision/contradictions.py effects`, `retrieval_analysis.py`, `noabst_analysis.py`, `transitions.py`, `exp0_costs.py`. A planned OLS of the contradiction effect on line counts was abandoned because the predictors are collinear (documented in `docs/CONTRADICTION_MECHANISM_AUDIT.md`); no coefficient from it is reported.
7. **Human package** (240 blinded contradiction pairs) exported; the key stays on the server. No labels collected.

## Deviations from the revision protocol

- The OLS model in §1 of the protocol was not interpretable (collinearity) and is not reported.
- Hop-count strata for the retrieval sample are uninformative for MuSiQue (459 of 500 questions are 2-hop because earlier samples exhausted the longer questions); stated in the paper's Limitations.
- The second reader (§4) was not run in revision-1; it was run in revision-2 after authorisation.

No threshold, margin, sample or contrast was changed after outcomes were seen.

## Revision-2 (2026-10-13, UTC)

Authorisations (investigator, 2026-10-13):
- download and run Mistral-7B-Instruct-v0.3;
- freeze and run a second confirmatory test on untouched questions.

All runs on physical GPU 0 through `scripts/campaign/run.sh`, sequentially from the queue `/data/roufas/wsh_revision/queue_r2.sh`.

| # | run | config | commit | started → finished | records (uncached) | wall clock | status |
|---|---|---|---|---|---|---|---|
| 4 | `revision/exp1/20261013-005215_27027ee0` | `revision_second_reader_smoke.yaml` (6 excluded questions, not analysed) | `46ae87e` | 00:52 → 00:52 | 36 (27) | 33 s | completed |
| 5 | `full/exp1/20261013-005305_1ded82bb` | `confirm2.yaml` (**confirmatory 2**) | `46ae87e` | 00:52 → 02:23 | 12,800 (9,185) | 5,427 s | completed, 0 errors |
| 6 | `revision/exp1/20261013-022332_df336d0b` | `revision2_controls.yaml` | `46ae87e` | 02:23 → 03:07 | 19,904 (5,169) | 2,635 s | completed, 0 errors |
| 7 | `revision/exp1/20261013-030726_a3469c77` | `revision2_conservative.yaml` | `46ae87e` | 03:07 → 03:33 | 4,000 (3,457) | 1,591 s | completed, 0 errors |
| 8 | `revision/exp1/20261013-033400_145ae2a1` | `revision_second_reader.yaml` (Mistral) | `46ae87e` | 03:33 → 08:29 | 29,856 (21,698) | 17,757 s | completed, 0 errors |

Prediction sha256:
- run 5: `55589124fa5023f7cdef358177a405679b55da64a73c5424ce8e56e35a4dd764`
- run 6: `0d668f3375d407df28a8bd212c194ee751c4c3bc36612c64c4998916d680798c`
- run 7: `39a11632a9c0da1d3f7246607752949858ef5eea9e4b1923ce6f9a30fc0958ab`
- run 8: `49c9801f524ba9fd8796f1f735c70b33268b22eb025117c9e3c3997d1a7d6a27`

### GPU-hour ledger (cumulative; ceiling 24 h, never reset)

| item | GPU-h |
|---|---|
| before revision-2 | 11.99 |
| run 4 (smoke) | 0.01 |
| run 5 (confirmatory 2) | 1.51 |
| run 6 (controls) | 0.73 |
| run 7 (conservative prompt) | 0.44 |
| run 8 (Mistral) | 4.93 |
| **total** | **≈ 19.61 of 24** |

### Chronology and decisions

1. Mistral downloaded at its pinned revision (sharded safetensors only, 14.5 GB, `/data/roufas/hf_cache`). It is ungated and Apache-2.0.
2. `CONFIRMATORY_PROTOCOL_2.md` committed and pushed (`6648eef`, 00:39 UTC). The sample `confirm2_v1` was then drawn (`6ccdc8b`). One deviation, logged before generation: a 2Wiki type rebalance.
3. Filler line changed before any generation: "(line intentionally left blank)" (5 tokens) became "(this line is intentionally left blank)" (7 tokens), closer to a contradiction line (8–9 tokens). Commit `96d1544`.
4. Smoke run of Mistral:
   - Format, parsing, GPU routing and speed are OK.
   - Mistral often gives sentence answers, so a lenient metric was fixed in `REVISION2_PROTOCOL.md` §3 before the full run.
5. Confirmatory 2 analysed with the frozen script, unchanged. Both hypotheses were confirmed.
6. Post-hoc audit findings in the revision-1 controls (40-line cap: 19 questions; duplicate merging under neutral relabelling: 442 questions). Sensitivity analyses leave the estimates unchanged (`docs/ACL_REVISION_AUDIT.md` §4).
7. The prompt-variant contrasts were first computed over all 3,232 2Wiki questions for the frozen prompt. That was corrected to the 1,000-question subset (`--questions-from`) before any number entered the paper.

No threshold, margin, sample or contrast was changed after outcomes were seen.
