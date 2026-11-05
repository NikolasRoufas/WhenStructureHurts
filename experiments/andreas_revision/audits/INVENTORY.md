# Stage 0: repository, artifact and server inventory (2026-11-05)

## Repository

- **Remote:** `https://github.com/NikolasRoufas/WhenStructureHurts` (private).
  - Branches: `main`, and this work's `experiments/andreas-journal-revision`.
  - Tags: `final-server-handoff`, `final-server-handoff-v2`, `pre-revision-baseline`, `research-record-revision2`.
- **Starting point:** `main` at `3fb2080` ("Code-only release … at revision-2"). It holds code, configs, frozen
  question sets and protocols, but no outputs.
- **Research record:** tag `research-record-revision2` (commit `9bfae0e`) holds the manuscript, reports,
  analysis outputs and annotation packages.
  - The README and `docs/README.md` also mention a `revision-1` branch; **no such branch exists on the remote**,
    only the tags.
  - The manuscript's artifact paths exist in the tag under a `research_outputs/` prefix:

| path cited in the manuscript | actual path (tag `research-record-revision2`) | sha256 (first 16) |
|---|---|---|
| `docs/CONFIRMATORY_PROTOCOL.md` | same (also on `main`) | `260a0e7b199622a6` |
| `revision2/confirm2/confirm2_summary.json` | `research_outputs/revision2/confirm2/confirm2_summary.json` | `6301a4046d06e17a` |
| `revision2/r2/controls2.csv` | `research_outputs/revision2/r2/controls2.csv` | `2044f069903c2aa3` |
| `revision2/r2/reader2.csv` | `research_outputs/revision2/r2/reader2.csv` | `2b88a51c817f2494` |
| `revision/retrieval/retrieval_contrasts.csv` | `research_outputs/revision/retrieval/retrieval_contrasts.csv` | `7092727d3782412e` |

- **Local checkout:** `~/Developer/WhenStructureHurts`, cloned fresh on 2026-11-05. No earlier local copy or
  uncommitted work existed.
- **Server checkout:** `/data/roufas/when-structure-hurts` at `46ae87e` with its `.venv`. It is untouched; this
  work uses its own checkout at `/data/roufas/wsh_andreas/repo`.
  - Code is synced from the Mac by `git bundle`, because the repo is private and the server has no GitHub
    credentials.
  - Datasets are symlinked from the original checkout, and the `MANIFEST.json` files are byte-identical.

## Server (`interstellar`)

| item | value |
|---|---|
| GPUs | 2 × NVIDIA RTX 5000 Ada (32 GB). GPU 0 (bus 01:00.0) is in Default mode. GPU 1 (bus 02:00.0, UUID `GPU-42ddde80…`) is in Exclusive_Process mode behind the user's MPS daemon. |
| Use in this work | **GPU 1 only, via MPS** (`scripts/run_gpu1.sh` checks the UUID and refuses if any other process is on GPU 1). The original campaign used GPU 0 with MPS bypassed; that is no longer authorised outside the ACL 2027 program. |
| Software | Python 3.12, torch 2.12.1+cu130 (CUDA 13.0), transformers 5.12.1 (the `requirements-pinned.txt` versions), the original checkout's venv |
| Memory / disk | 188 GB RAM; `/` 100 % full (unused); `/data` 1.6 TB with 988 GB free |
| Scheduler | none (single-user server; tmux sessions plus a status log, as in the original campaign) |
| HF cache | `/data/roufas/hf_cache`: Qwen2.5-7B-Instruct, Mistral-7B-Instruct-v0.3, the NLI and retrieval encoders, and (new, 2026-11-05) OLMo-2-1124-7B-Instruct at the pinned revision. No HF token. |

## Original runs (frozen; outputs only on the server, under `/data/roufas/wsh_campaign/results/`)

| run | config | reader | questions | conditions |
|---|---|---|---|---|
| `full/exp1/20261012-125639_49dfe135` | confirm.yaml | Qwen | confirm_v1 (4,976: MuSiQue + 2Wiki) | confirmatory test 1 |
| `revision/exp1/20261012-200925_a2e6e3a8` | revision_relation_controls.yaml | Qwen | confirm_v1 | fixed-order controls incl. R4P_FO, R4P_FO_NC |
| `revision/exp1/20261012-210958_37616258` | revision_retrieval.yaml | Qwen | retr_v1 (500 + 500) | retrieved evidence |
| `full/exp1/20261013-005305_1ded82bb` | confirm2.yaml | Qwen | **confirm2_v1 (2,600 2Wiki + 3,800 HotpotQA)** | R4P_FO, R4P_FO_NC (confirmatory test 2) |
| `revision/exp1/20261013-022332_df336d0b` | revision2_controls.yaml | Qwen | confirm_v1 | R4P_FO_CN, R4P_FO_NCPAD |
| `revision/exp1/20261013-033400_145ae2a1` | revision_second_reader.yaml | Mistral | confirm_v1 | R0, R1, R5, R4, R4P_FO, R4P_FO_NC |
| other | pilot, no-abstention, conservative prompt, smoke | Qwen | see `docs/RUN_STATUS.md` in the tag | |

SHA-256 of all 15 `predictions.jsonl` files, manifests, metrics and the revision analysis directory (91 files)
are in `original_artifact_hashes.json`. `verify_originals.py verify` re-checks them; it is run before every push.

## Annotation materials

- **`human_package_v1`** (revision-1): 240 pairs, single label column, on the R4P (not fixed-order) prompts.
  Superseded by v2 and not used here.
- **`human_package_v2`** (revision-2): 300 pairs. Two annotator files, the GUIDE, and a key outside the
  package (`/data/roufas/wsh_revision/false_contra/…KEY…json`). **0 labels filled in.** Audit
  (`stage0_audit.json`):
  - hashes match; 0 duplicate ids; 0 empty passages; 3 facts not literally contained in their passage
    (whitespace or segmentation);
  - 33 text-duplicate pairs across questions (the same sentences appear for different questions);
  - 252 questions, 1–5 pairs each; 179 of the 300 pairs are same-passage pairs;
  - the sampler reproduces the package exactly from seed 0.
- **New:** `human_package_v3` (Experiment B Tier 1): 666 pairs from 300 confirm2 questions; 0 labels; key on
  the server.

## Reproducibility weaknesses found

1. Raw predictions exist **only on the server** (3.3 GB, not in Git or Git LFS, no off-server archive found besides
   git bundles of code). Hashes are now recorded; an off-server copy is recommended (§ final report).
2. Annotation keys are outside Git by design, so annotators cannot see them. Their hashes are recorded here.
3. The README points to a `revision-1` branch that is not on the remote.
4. The Mistral run had 1 condition-dependent overflow (one R4P_FO prompt over 4,096 tokens, skipped, while its
   NC partner ran). It also had 139 (R4P_FO) and 157 (R4P_FO_NC) answers cut at 64 tokens. This was not
   discussed in the record. The Qwen confirm2 run had 0 overflows and 2 truncations.
5. Relation prediction is deterministic across runs: the R4P_FO prompts of the Qwen and Mistral runs on
   confirm_v1 are byte-identical for 4,976 of 4,976 questions.
