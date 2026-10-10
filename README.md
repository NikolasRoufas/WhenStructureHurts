# When Structure Hurts: Understanding Evidence Loss in Retrieval-Augmented Reasoning

Research framework for studying how evidence transformations (passages → atomic claims → reasoning paths → evidence graphs) affect retrieval-augmented reasoning, and when the errors they introduce outweigh their benefits.

**Status (2026-10-11, pre-GPU preflight complete):** 133/133 tests passing. Exp1 redesigned into Protocol A (information-controlled) and Protocol B (budget-controlled). Pilot design frozen ([docs/PILOT_PROTOCOL.md](docs/PILOT_PROTOCOL.md)). Frozen pilot question set; human-verification package prepared, not yet annotated. Corrected pipeline smoke-tested on the 0.5B model. **No scientific results yet**: smoke scores are pipeline checks, not evidence for any hypothesis. Readiness verdict: [docs/PRE_GPU_READINESS.md](docs/PRE_GPU_READINESS.md).

## Documents

| | |
|---|---|
| [docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md) | questions, hypotheses H1–H4, falsification criteria, phasing |
| [docs/EXPERIMENT_SPEC.md](docs/EXPERIMENT_SPEC.md) | every condition, control, metric, contrast; preregistration checklist |
| [docs/NOVELTY_AND_BASELINES.md](docs/NOVELTY_AND_BASELINES.md) | related work, baselines, EG-RAG reconstruction ledger |
| [docs/EXPERIMENT_LOG.md](docs/EXPERIMENT_LOG.md) | what was actually executed, results of the smoke test, problems found |
| [docs/PILOT_PROTOCOL.md](docs/PILOT_PROTOCOL.md) | frozen pilot design: primary question, comparisons, metric, statistics, expansion rules |
| [docs/METHODOLOGICAL_AUDIT.md](docs/METHODOLOGICAL_AUDIT.md) | every validity risk: fixed / controlled / needs human verification / needs stronger model / unresolved |
| [docs/SERVER_SETUP.md](docs/SERVER_SETUP.md) | GPU server installation, preflight, pilot command templates, resumption, artefacts |
| [docs/PRE_GPU_READINESS.md](docs/PRE_GPU_READINESS.md) | readiness gate and verdict |
| [annotations/verification_v1/GUIDE.md](annotations/verification_v1/GUIDE.md) | human verification package (50 questions) and annotation guide |
| [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) | versions, seeds, commands, artefacts |
| [docs/COMPUTE_HANDOFF.md](docs/COMPUTE_HANDOFF.md) | what is needed for pilot/full runs and the prepared commands |

## Architecture

```
src/wsh/
  data/            schemas (annotation status + span provenance), loaders (5 datasets), validation, provenance ids
  retrieval/       BM25, dense (bge-small) + Eq.2 fusion, cross-encoder reranking
  extraction/      claim extractors (sentence / rule / LLM), relation classifier (NLI + heuristics)
  representations/ gold/retrieved evidence bundles, R0-R5 layouts, serialization, Exp1 protocols A/B (protocols.py)
  egrag/           reconstructed EG-RAG: belief (Eq.5-8), conflicts, subgraph selection (Eq.9-10), pipeline
  interventions/   P1-P7 controlled perturbations with change records and label effects
  models/          generator protocol, local HF generator, encoders, prompts, size policy
  evaluation/      parsing, answer metrics, citations/coverage/groundedness, failure taxonomy, statistics, reports
  experiments/     exp0 baselines, exp1 representations, exp2 perturbations, exp3 components, exp4 (gated scaffold)
  systems.py       B0-B4; artifacts.py run dirs/manifests/resume; cache.py; config.py; cli.py; preflight.py
configs/           smoke / pilot / full configs; question_sets/ (frozen samples); excluded_questions.json; models.yaml (allowlist + policy)
annotations/       human verification package(s); src/wsh/annotations.py exports/imports/applies them
tests/             133 unit/integration tests (the mock generator lives only here)
scripts/run_smoke.sh
results/<stage>/<exp>/<run_id>/   per-run artefacts (never overwritten)
```

Layers are kept separate: data → retrieval → evidence transformation → serialization → generation → evaluation → orchestration. Each experiment is runnable on its own.

## Quick start

```bash
uv venv --python python3 --system-site-packages .venv && uv pip install --python .venv/bin/python -e .
for d in musique 2wikimultihopqa hotpotqa hover fever; do .venv/bin/wsh data fetch --dataset $d; done
.venv/bin/wsh models fetch Qwen/Qwen2.5-0.5B-Instruct --stage smoke      # policy + disk/RAM checks first
.venv/bin/python -m pytest -q
scripts/run_smoke.sh
```

Individual experiments:

```bash
.venv/bin/wsh run exp0 --config configs/smoke.yaml   # B0-B4 baselines (retrieved evidence)
.venv/bin/wsh run exp1 --config configs/smoke.yaml   # R0-R5, Protocol A (same facts) and B (token budget)
.venv/bin/wsh run exp2 --config configs/smoke.yaml   # P1-P7 perturbations
.venv/bin/wsh run exp3 --config configs/smoke.yaml   # oracle vs C1-C4 component substitution
.venv/bin/wsh exp4 --config configs/smoke.yaml --source-run <exp1 run> --plumbing-check
.venv/bin/wsh report <run_dir>                       # recompute aggregates
.venv/bin/wsh data inspect --dataset musique --n 2   # look at parsed questions and annotation statuses
.venv/bin/wsh preflight --config configs/pilot.yaml  # machine/data/model checks; no experiment is run
.venv/bin/wsh questions freeze --spec <spec.yaml> --out <frozen.json>
.venv/bin/wsh annotations export|import ...         # human verification package
```

## Execution safeguards

- Model allowlist with pinned revisions; smoke/pilot capped at 1B parameters (checked before download and again after load). The `full` stage needs `WSH_COMPUTE_AUTHORIZED=1` **and** `--authorized-compute`.
- Stage limits on examples and generations; a wall-clock cap; per-call `max_new_tokens` and `max_time`.
- Test splits are refused. Pilot/full runs use only frozen question files and refuse smoke/prompt-development questions. New runs never overwrite existing directories; `--resume` checks the config hash.
- Every prompt is checked to be exactly template + evidence + question (no hidden gold content).
- No annotation is fabricated. Every claim, edge and path carries a status (`dataset_supplied`, `deterministic_derived`, `human_verified`, `model_predicted`, `corrupted`, `unavailable`). Conditions that would need missing annotations are recorded as `unavailable`.
