# Journal-revision experiments (Experiments A–D)

These experiments were requested by Prof. Andreas Kanavos for the journal version of *When Structure Hurts*.
The original experiments, their outputs and the manuscript are frozen; nothing here modifies them. The design is
fixed in [`protocols/PROTOCOL_JOURNAL_REVISION.md`](protocols/PROTOCOL_JOURNAL_REVISION.md), committed before any
new generation. Results are in [`reports/FINAL_EXPERIMENTAL_REPORT.md`](reports/FINAL_EXPERIMENTAL_REPORT.md) and
[`reports/SUMMARY_FOR_ANDREAS.md`](reports/SUMMARY_FOR_ANDREAS.md).

| dir | content |
|---|---|
| `protocols/` | the frozen protocol and its dated amendments (§7) |
| `audits/` | stage-0 inventory and audit, original-artifact hashes, preflight checks |
| `annotation/` | packages v2 (300 pairs, reused unchanged) and v3 (666 pairs, Experiment B), guidelines, tools |
| `selective_removal/` | Experiment B: selection, tier files, label conversion, run config, analysis |
| `model_replication/` | Experiment C: OLMo-2 configs, token preflight, smoke check, analysis, results |
| `retrieval_extension/` | Experiment D: GO/NO-GO decision and the unused-question count |
| `scripts/run_gpu1.sh` | GPU launcher (physical GPU 1 through MPS; refuses if anyone else is on it) |
| `arlib.py` | shared statistics and outcome helpers |

Tests: `tests/test_selective_removal.py` and `tests/test_andreas_revision.py`, plus the existing suite:
`.venv/bin/python -m pytest -q`.

## Commands

All commands run from the repository root, with `PYTHONPATH=src` and the project venv. Server paths are those
of `interstellar`.

```bash
# Stage 0 (no generation)
python experiments/andreas_revision/audits/stage0_audit.py --campaign /data/roufas/wsh_campaign \
    --revision /data/roufas/wsh_revision --out /data/roufas/wsh_andreas/audits --n-sim 2000
python experiments/andreas_revision/audits/verify_originals.py verify experiments/andreas_revision/audits/original_artifact_hashes.json

# Experiment C (run on the server, inside tmux)
python experiments/andreas_revision/model_replication/token_preflight.py <qwen_confirm2_run> <out.json>
WSH_CACHE_PATH=<fresh.sqlite> experiments/andreas_revision/scripts/run_gpu1.sh exp1 \
    experiments/andreas_revision/model_replication/configs/olmo2_confirm2_smoke.yaml        # twice, separate caches
python experiments/andreas_revision/model_replication/smoke_check.py <smoke1> <smoke2> <qwen_confirm2_run> <out.json>
experiments/andreas_revision/scripts/run_gpu1.sh exp1 experiments/andreas_revision/model_replication/configs/olmo2_confirm2_full.yaml
python scripts/revision/confirm2_analysis.py <olmo_run> <out_dir>                   # EM primary family, unchanged script
python experiments/andreas_revision/model_replication/analysis.py <olmo_run> <qwen_confirm2_run> <out_dir>

# Experiment A (after both annotators return their files)
T=experiments/andreas_revision/annotation/annotation_tools.py
python $T validate  <pkg_dir> <key.json>
python $T agreement <pkg_dir> <key.json> <out_dir>                 # writes adjudication_package.csv
python $T finalize  <pkg_dir> <key.json> <adjudication.csv|-> <out_dir>
python $T precision <out_dir>/final_labels.csv <out_dir> --population <package_v2_population_KEY…csv>

# Experiment B (after package v3 is labelled and adjudicated)
S=experiments/andreas_revision/selective_removal/select_questions.py
python $S labels <final_labels.csv> <v3_key.json> experiments/andreas_revision/selective_removal/expB_tier1_qids.json \
    experiments/andreas_revision/selective_removal/labels/expB_tier1_labels.json
experiments/andreas_revision/scripts/run_gpu1.sh exp1 experiments/andreas_revision/selective_removal/configs/expB_tier1_qwen.yaml
python experiments/andreas_revision/selective_removal/analysis.py <run> <labels.json> <qwen_confirm2_run> <out_dir>
```

Experiment C raw outputs are in Git: `model_replication/results/predictions_full.jsonl.gz` decompresses to the
server's `predictions.jsonl` (sha256 `ce2701f19dc2c6913e1671876e6a90fe19febb02e878ae7e9ca6063c4cefc8ba`).

Inputs that are not in Git:
- the datasets (`wsh data fetch`; hashes in `data/raw/MANIFEST.json`);
- the model weights (pinned revisions in `configs/models.yaml`);
- the raw `predictions.jsonl` files (server, hashes in the reports);
- the annotation keys (server, hashes in the summaries; withheld from annotators).
