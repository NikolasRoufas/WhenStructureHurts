# Reproducibility checklist

Every headline claim in `paper/main.pdf`, mapped from claim → analysis output → run → config → predictions (sha256). Raw predictions stay on the server (`/data/roufas/wsh_campaign/results/…`) and are not pushed; the hashes identify them. Analysis outputs are under `research_outputs/` in this repository.

## Runs

| label | run directory | config | commit | predictions sha256 |
|---|---|---|---|---|
| `F_exp1` (confirmatory) | `full/exp1/20261012-125639_49dfe135` | `configs/confirm.yaml` | `ed7c391` | in `research_outputs/analysis/provenance.json` |
| `C_exp1`, `C_exp2`, `C_exp0`, `A_exp0` (pilot) | see `research_outputs/experiments/runs.json` | `configs/gpu_pilot*.yaml` | `dea50b3` / `ed7c391` | in `provenance.json` |
| `R_ctrl` (revision, fixed-order controls) | `revision/exp1/20261012-200925_a2e6e3a8` | `configs/revision_relation_controls.yaml` | `ceb8802` | `43c2ae29fe4e241ee83284ccad66e682580a3fa03663305f163fae205e3bef46` |
| `R_retr` (revision, retrieved evidence) | `revision/exp1/20261012-210958_37616258` | `configs/revision_retrieval.yaml` | `8423203` | `0608b2a6257dcb10de4c1794fa742175f31deb234dffd7668e5bbbef2d0f3a41` |
| `C2` (**confirmatory 2**) | `full/exp1/20261013-005305_1ded82bb` | `configs/confirm2.yaml` (protocol `docs/CONFIRMATORY_PROTOCOL_2.md`) | `46ae87e` | `55589124fa5023f7cdef358177a405679b55da64a73c5424ce8e56e35a4dd764` |
| `R2_ctrl` (revision-2 controls) | `revision/exp1/20261013-022332_df336d0b` | `configs/revision2_controls.yaml` | `46ae87e` | `0d668f3375d407df28a8bd212c194ee751c4c3bc36612c64c4998916d680798c` |
| `R2_cons` (revision-2 conservative prompt) | `revision/exp1/20261013-030726_a3469c77` | `configs/revision2_conservative.yaml` | `46ae87e` | `39a11632a9c0da1d3f7246607752949858ef5eea9e4b1923ce6f9a30fc0958ab` |
| `R2_mistral` (second reader) | `revision/exp1/20261013-033400_145ae2a1` | `configs/revision_second_reader.yaml` (Mistral-7B-Instruct-v0.3 `c170c708`) | `46ae87e` | `49c9801f524ba9fd8796f1f735c70b33268b22eb025117c9e3c3997d1a7d6a27` |
| `R_noabst` (revision, prompt factor) | `revision/exp1/20261012-221036_8a903b43` | `configs/revision_noabst.yaml` | `8423203` | `5cb9240ba9ce6af9936780a24d2f8bc4ef5d9325338b1108f1f982eba3499080` |

Frozen question sets: `confirm2_v1.json` (sha256 `53fecd59…`), `confirm_v1.json` (sha256 `d7b49cb3…`), `pilot_v1.json` (`67e81564…`), `retr_v1.json` (`8c32d7ed…`), `confirm_v1_2wiki_sub1000.json` (seed 4).

## Claims

| claim (paper) | analysis output | run |
|---|---|---|
| Six confirmatory tests, Table 2; 2Wiki R1−R0 −0.017 [−0.029, −0.005], p_Holm 0.018 | `research_outputs/analysis/F_exp1_contrasts.csv` | `F_exp1` |
| Holm-TOST agrees with per-test 90 % CI rule | `docs/STATISTICAL_REVIEW.md`; `research_outputs/revision/audit/audit.json` | `F_exp1` |
| Transitions (Table 12): 2Wiki R1−R0 C→A 87, W→A 163 | `research_outputs/revision/analysis/F_exp1_transitions.csv` | `F_exp1` |
| Contradiction lines on vs off: −0.033 on both datasets, +6 pts abstention (Table 3, Fig. 4) | `research_outputs/revision/controls/relation_control_effects.csv` | `R_ctrl` |
| Typed vs neutral labels −0.037 / −0.030; order-only +0.002 / +0.018 | same | `R_ctrl` |
| No-contradiction stratum ≈ 0; 1–2 lines −0.069 / −0.053 (Table 13) | `research_outputs/revision/controls/relation_control_strata.csv` | `R_ctrl` |
| C→A 89 vs A→C 9 (2Wiki), 52 vs 2 (MuSiQue) | `research_outputs/revision/controls/controls_transitions.csv` | `R_ctrl` |
| 12,816 predicted CONTRADICTS edges, 12,372 rendered; triage shares (Table 15) | `research_outputs/revision/contradictions/contradictions_summary.json` | `F_exp1` (R4P renderings) |
| Retrieved evidence: R4P−R4 −0.036 / −0.030; contradiction lines −0.022 / −0.024; R5 = R1 for 498/500 2Wiki (Tables 4, 16, 17) | `research_outputs/revision/retrieval/retrieval_contrasts.csv`, `retrieval_strata_counts.json` | `R_retr` |
| Prompt factor: noabst R1−R0 −0.004, R4P−R4 −0.017; prompt effect +0.078 to +0.128; abstention < 1 % (Table 14) | `research_outputs/revision/noabst/noabst_contrasts.csv`, `noabst_transitions.csv` | `R_noabst` (+ `F_exp1` for qa-v2 cells) |
| Exp0 budgets and costs (Table 18) | `research_outputs/revision/analysis/C_exp0_costs.csv` | `C_exp0` |
| Confirmatory 2: −0.077 / −0.053 among affected questions, p_Holm < 0.001 (Table 4) | `research_outputs/revision2/confirm2/confirm2_summary.json` (`scripts/revision/confirm2_analysis.py`) | `C2` |
| Targeted relabel / filler controls (Table 3 rows 2–3) | `research_outputs/revision2/r2/controls2.csv` (`scripts/revision/r2_analysis.py`) | `R2_ctrl` + `R_ctrl` |
| Second reader (Table 14) | `research_outputs/revision2/r2/reader2.csv` | `R2_mistral` + `R_ctrl` + `F_exp1` |
| Abstention policy (Table 15) | `research_outputs/revision2/r2/prompt3.csv` (`--questions-from` the noabst run) | `R2_cons` + `R_noabst` + `F_exp1` |
| Serialisation and anchor strata (Tables 17–18) | `research_outputs/revision2/serialization/` (`scripts/revision/serialization_audit.py`) | `F_exp1` + `R_ctrl` |
| About 20 GPU-hours | `docs/REVISION_EXPERIMENT_LOG.md` ledger; `/data/roufas/wsh_campaign/status.log` | all |

## Rebuild

```bash
# on the server, analysis clone, read-only on predictions
cd /data/roufas/wsh_analysis
PY="nice -n 15 /data/roufas/when-structure-hurts/.venv/bin/python"
RES=/data/roufas/wsh_campaign/results; R=$RES/revision/exp1; O=/data/roufas/wsh_revision
PYTHONPATH=src $PY scripts/revision/transitions.py        $RES/full/exp1/20261012-125639_49dfe135 $O/analysis/F_exp1_transitions.csv
PYTHONPATH=src $PY scripts/revision/contradictions.py effects $R/20261012-200925_a2e6e3a8 $O/controls
PYTHONPATH=src $PY scripts/revision/retrieval_analysis.py $R/20261012-210958_37616258 $O/retrieval
PYTHONPATH=src $PY scripts/revision/noabst_analysis.py    $RES/full/exp1/20261012-125639_49dfe135 $R/20261012-221036_8a903b43 $O/noabst
PYTHONPATH=src $PY scripts/revision/exp0_costs.py         $RES/gpu_pilot/exp0/20261012-183032_f123f890 $O/analysis/C_exp0_costs.csv
# tables and figures, then the PDF
python3 scripts/revision/paper_assets.py research_outputs/revision paper
cd paper && TECTONIC_CACHE_DIR=/data/roufas/tools/cache /data/roufas/tools/tectonic main.tex
```

## Checks

| item | status |
|---|---|
| Test suite (`pytest`) | 178 passed, 1 skipped |
| Fact identity per question (Protocol A) in every revision run | verified by the runner (0 pipeline errors) |
| Question-set disjointness (smoke, pilot, confirm, retr) | verified (`configs/excluded_revision.json`; 0 overlap) |
| Seeds | sampling seeds 1–4 recorded in set specs; bootstrap seed 0; generation greedy |
| Determinism | batch size 1; unbatched outputs identical run-to-run (`docs/gpu_preflight/gpu0_7b.json`) |
| Model and auxiliary revisions pinned | `configs/models.yaml` |
| Secrets, weights, raw predictions in git | none (scanned before push) |
