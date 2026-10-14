# When Structure Hurts

Research code for controlled experiments on **evidence representations in retrieval-augmented question answering**. The framework presents the same supporting facts to a language model in different formats — passages, sentence items, ordered items, items with derived or predicted relation lines — and measures how each change affects answers, abstention and evidence retention.

## What it implements

- **Representations of identical evidence** (`src/wsh/representations/`): R0 passages, R1 sentence items, R2 shuffled, R3 step-grouped, R5 graph-ordered, R4 with derived relation lines, R4P with predicted relations, and fixed-order relation controls. The controls are:
  - R4P_FO: predicted lines at the derived order;
  - R4P_FO_NC: without CONTRADICTS lines;
  - R4P_FO_CN: CONTRADICTS relabelled neutral;
  - R4P_FO_NCPAD: CONTRADICTS lines replaced by length-matched filler;
  - R4N_FO: all labels neutral;
  - R5P: predicted order only.
- **Two evaluation protocols**:
  - *Protocol A* verifies per question that every representation shows the same fact set (identifier and text digests).
  - *Protocol B* applies a representation-independent fact ranking and a token budget, and records which facts each format keeps.
- **Gold or retrieved evidence**: BM25, dense retrieval and cross-encoder reranking (`retrieval/`), with optional relation edges derived from annotations.
- **Relation prediction** with an NLI cross-encoder and a title-mention heuristic (`extraction/`).
- **Baselines B0–B4**, including a documented reconstruction of the EG-RAG evidence-graph pipeline (`egrag/`, [docs/EGRAG_RECONSTRUCTION.md](docs/EGRAG_RECONSTRUCTION.md)).
- **Controlled perturbations** P1–P7 with change records (`interventions/`).
- **Evaluation** (`evaluation/`): exact match, token F1, abstention parsing, citations, coverage, outcome transitions, paired bootstrap statistics with Holm correction and equivalence tests.
- **Prompt variants**: the frozen `qa-v2` prompt, a variant without the abstention option, and a stricter-abstention variant.
- **Run management**: frozen question sets, per-run manifests (code commit, config hash, package versions, dataset hashes), resumable runs and a generation cache.

## Installation

Python ≥ 3.11.

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
# exact versions used for the reported runs:
.venv/bin/pip install -r requirements-pinned.txt
```

Datasets (MuSiQue, 2WikiMultiHopQA, HotpotQA, HoVer, FEVER; development splits) and models are fetched at pinned revisions, and their hashes are checked against `data/raw/MANIFEST.json` and `configs/models.yaml`:

```bash
for d in musique 2wikimultihopqa hotpotqa hover fever; do .venv/bin/wsh data fetch --dataset $d; done
.venv/bin/wsh models fetch Qwen/Qwen2.5-0.5B-Instruct --stage smoke
```

Model downloads go through an allowlist with size and resource checks. The `smoke` and `pilot` stages are capped at 1B parameters; the `gpu_pilot`, `revision` and `full` stages require `WSH_COMPUTE_AUTHORIZED=1` and `--authorized-compute`. Paths can be redirected with `WSH_DATA_ROOT`, `WSH_RESULTS_ROOT`, `WSH_CACHE_PATH` and `HF_HOME`.

## Running experiments

```bash
.venv/bin/python -m pytest -q                         # test suite
scripts/run_smoke.sh                                  # bounded end-to-end check with a 0.5B model

.venv/bin/wsh run exp0 --config configs/smoke.yaml    # retrieved-evidence baselines B0–B4
.venv/bin/wsh run exp1 --config configs/smoke.yaml    # representations, Protocols A and B
.venv/bin/wsh run exp2 --config configs/smoke.yaml    # perturbations
.venv/bin/wsh run exp1 --config <cfg> --resume <run_dir>
.venv/bin/wsh report <run_dir>                        # recompute aggregates from predictions
.venv/bin/wsh preflight --config <cfg>                # machine, data and model checks; runs nothing
.venv/bin/wsh questions freeze --spec <spec.yaml> --out <set.json>
```

Each run writes a new directory `results/<stage>/<experiment>/<timestamp>_<confighash>/` with `config.resolved.yaml`, `manifest.json`, `predictions.jsonl` (one self-contained record per question and condition), `metrics.json`, `summary.csv` and `report.md`. Existing run directories are never overwritten.

### Configurations of the reported runs

All runs use Qwen2.5-7B-Instruct (pinned revision, bf16, greedy decoding, batch size 1) unless stated. Question sets are frozen in `configs/question_sets/`, and the exclusion lists in `configs/excluded_*.json` keep the samples disjoint.

| config | experiment |
|---|---|
| `gpu_pilot_focused.yaml`, `gpu_pilot.yaml` | exploratory pilot (Exp0–Exp2), `pilot_v1` |
| `confirm.yaml` | confirmatory test 1: six pre-specified contrasts, `confirm_v1` ([protocol](docs/CONFIRMATORY_PROTOCOL.md)) |
| `revision_relation_controls.yaml`, `revision2_controls.yaml` | fixed-order relation controls on `confirm_v1` |
| `confirm2.yaml` | confirmatory test 2: contradiction lines on vs. off, `confirm2_v1` ([protocol](docs/CONFIRMATORY_PROTOCOL_2.md)) |
| `revision_retrieval.yaml` | retrieved-evidence experiment, `retr_v1` |
| `revision_noabst.yaml`, `revision2_conservative.yaml` | abstention-policy prompt variants |
| `revision_second_reader.yaml` | second reader (Mistral-7B-Instruct-v0.3) |

`scripts/campaign/run.sh <exp> <config>` is the GPU launcher used for these runs. It is specific to our single-GPU server (physical-device and idle checks, MPS bypass, status log), so adapt it to your machine.

### Analysis

Analysis scripts read only `predictions.jsonl` files:

| script | output |
|---|---|
| `scripts/analysis/build.py` | per-run tables, paired contrasts with bootstrap CIs and Holm correction, figures |
| `scripts/revision/confirm2_analysis.py` | the pre-specified analysis of confirmatory test 2 |
| `scripts/revision/r2_analysis.py` | generic paired contrasts across conditions, prompts and readers (EM, F1, lenient match, abstention, wrong answers, transitions) |
| `scripts/revision/transitions.py`, `contradictions.py`, `false_contradictions.py`, `retrieval_analysis.py`, `serialization_audit.py`, `exp0_costs.py` | outcome transitions, relation-control effects and annotation packages, retrieval strata, token accounting, baseline costs |
| `scripts/audit/verify_claims.py` | independent re-derivation of the confirmatory statistics |

## Repository layout

```
src/wsh/        data, retrieval, extraction, representations, egrag, interventions, models, evaluation, experiments, cli
configs/        experiment configs, frozen question sets, exclusion lists, dataset and model pins
scripts/        launcher, smoke test, preflight, analysis and audit scripts
tests/          unit and integration tests (mock generator; data-dependent tests skip without datasets)
docs/           experiment specification, methodological guards, frozen protocols, baseline reconstruction
data/raw/       MANIFEST.json only (datasets are fetched, not committed)
```

## Safeguards

- Test splits are refused. Larger runs use only frozen question files and refuse smoke and prompt-development questions.
- Every prompt is checked to equal the template filled with the evidence and question, so no gold content can enter through another channel.
- Every claim, edge and path carries a status (`dataset_supplied`, `deterministic_derived`, `human_verified`, `model_predicted`, `corrupted`, `unavailable`). Conditions that need missing annotations are recorded as unavailable, never imputed.
- Deterministic seeds (`derive_seed`), greedy decoding, and a cache keyed by model, revision, full prompt and decoding parameters.

## License

Apache-2.0 (see `LICENSE`).
