# Run status: Qwen2.5-7B GPU campaign (authorised 2026-10-12)

**Authorisation and constraints:**
- Compute ceiling: 24 GPU-hours of new computation on physical GPU 0 of `interstellar`.
- Model: Qwen2.5-7B-Instruct `a09a3545` (cached), bf16, batch size 1.
- Questions: frozen sets only; smoke and pilot exclusions enforced.

**Where everything lives (server, all under `/data/roufas/`):**
- Campaign root: `wsh_campaign/`.
- Runs: `wsh_campaign/results/<stage>/<exp>/<run_dir>/`, each with `manifest.json`, `config.resolved.yaml` and `predictions.jsonl`.
- Shared generation cache: `wsh_campaign/cache/gen.sqlite`.
- Logs and 30-second GPU traces: `wsh_campaign/logs/`.
- Start/end lines: `wsh_campaign/status.log`.
- Analysis outputs: `wsh_campaign/research_outputs/` (built by `scripts/analysis/build.py` in the separate analysis clone `/data/roufas/wsh_analysis`).
- Jobs run in tmux session `wsh`: window 0 is Stage A, window `stageC` is the queued Stage C and confirmatory runs.
- Every job goes through `scripts/campaign/run.sh`, which checks before each run that the device is bus `01:00.0`, reached directly with no MPS routing, and that the GPU is idle.

GPU-hours are counted as the wall-clock time a run holds GPU 0 (one process at a time).

## Stages

| stage | run | config @ commit | status | records | errors | wall clock / GPU-h |
|---|---|---|---|---|---|---|
| A | Exp1, focused 200 questions — `gpu_pilot/exp1/20261012-095222_797a0644` | `gpu_pilot_focused.yaml` @ `dea50b3` | **completed** 10:29 UTC | 9,000 (4,956 generated, the rest identical prompts served from cache) | 0 generation / 0 pipeline / 0 unavailable | 2,243 s / **0.62** |
| A | Exp0, focused 200 questions — `gpu_pilot/exp0/20261012-102947_8dad35aa` | `gpu_pilot_focused.yaml` @ `dea50b3` | **completed** 12:06 UTC | 1,000 | 0 generation / 0 pipeline; 30 answers cut at max_new_tokens, 2 context overflows (both scored, kept in the denominator) | 5,783 s / **1.61** |
| B | decision gate | `research_outputs/reports/DECISION_GATE_STAGE_B.md` | **done: proceed** | | | 0 |
| C | Exp1, 350 questions — `gpu_pilot/exp1/20261012-120617_d4f7f61d` | `gpu_pilot.yaml` @ `ed7c391` | **completed** 12:21 UTC | 15,750 (the 200 focused questions served from cache) | 0 / 0; 500 unavailable by design (R3 on HoVer and FEVER: no reasoning path) | 932 s / **0.26** |
| C | Exp2, 350 questions — `gpu_pilot/exp2/20261012-122150_20896430` | `gpu_pilot.yaml` @ `ed7c391` | **completed** 12:56 UTC | 14,000 | 0 / 0; 2,664 unavailable by design (P7 without verified temporal data; P2 on R1 and on questions without edges; interventions with nothing eligible) | 2,093 s / **0.58** |
| confirmatory | Exp1, 1,744 MuSiQue + 3,232 2Wiki, Protocol A — `full/exp1/20261012-125639_49dfe135` | `confirm.yaml` @ `ed7c391` | running since 12:56 UTC (about 130 records/min) | 1,044 / 44,784 at 13:04 UTC | 0 so far | est. 5.7 (finish ≈ 18:40 UTC) |
| C | Exp3, 350 questions | `gpu_pilot.yaml` | queued (expected: every question unavailable, since there are no human-verified annotations) | | | est. < 0.1 |
| C | Exp0, 350 questions (the 200 already done come from cache) | `gpu_pilot.yaml` | queued last | | | est. 1.2 |

## GPU-hour ledger

| item | GPU-h |
|---|---|
| preflight (2026-10-12, bounded) | < 0.1 |
| Stage A Exp1 | 0.62 |
| Stage A Exp0 | 1.61 |
| Stage C Exp1 | 0.26 |
| Stage C Exp2 | 0.58 |
| **total completed** | **≈ 3.1** |
| projected total once every queued item finishes | ≈ 10 (ceiling 24) |

**Analysis outputs:**
- `research_outputs/analysis/` (A_exp1, A_exp0, C_exp1, C_exp2) and `research_outputs/figures/`.
- `results/analysis/FOCUSED_PILOT_REPORT.md`.
- Built at commit `33bbbd8` from the run directories listed in `research_outputs/experiments/runs.json`.

## Frozen artefacts used

- Pilot set: `configs/question_sets/pilot_v1.json`, sha256 `67e81564…`.
- Confirmatory set: `configs/question_sets/confirm_v1.json`, sha256 `d7b49cb3…`. Drawn after `docs/CONFIRMATORY_PROTOCOL.md` was committed (`0850982`), and disjoint from the pilot and smoke sets.

## Notes

- 2026-10-12: the Mac's disk is nearly full. All analysis and LaTeX compilation run on the server (`/data/roufas/tools/tectonic`, with its cache in `/data/roufas/tools/cache`); only text files and small outputs are kept locally.
- 10:20 UTC: a local SSH watcher dropped (exit 255). The tmux jobs were unaffected; watchers now reconnect on every poll.
