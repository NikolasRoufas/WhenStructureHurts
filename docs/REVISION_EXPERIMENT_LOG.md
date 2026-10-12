# Revision-1 experiment log

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
- The second reader (§4) was not run.

No threshold, margin, sample or contrast was changed after outcomes were seen.
