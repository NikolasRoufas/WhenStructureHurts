# Revision baseline audit (revision-1, 2026-10-12)

**Baseline.** Git tag `pre-revision-baseline` = commit `d18cf77` (on `main` and GitHub). That paper draft and its outputs are kept unchanged at that tag. All revision work is on branch `revision-1`.

**Method.** `scripts/audit/verify_claims.py` re-derives every central number from the saved predictions on the server, independently of `scripts/analysis/build.py`. It uses its own record loading, per-question aggregation, a re-implementation of the frozen bootstrap, an independent numpy bootstrap (seed 12345, 20,000 resamples), its own Holm, a TOST and an exact McNemar. Outputs: `research_outputs/revision/audit/audit.json` and `claims_check.csv`. Exp0 and Exp2 claims were re-checked with a separate inline script (same algorithms). The run directories and their predictions sha256 are listed in `audit.json`.

## 1. Data integrity

| check | result |
|---|---|
| Question counts | pilot 350 (100/100/50/50/50); confirmatory 4,976 (1,744 MuSiQue + 3,232 2Wiki); every question unique within its set |
| Split | `dev` for every record of every run |
| Disjointness | pilot ∩ confirmatory = 0; smoke ∩ confirmatory = 0; smoke ∩ pilot = 0. The confirmatory run's questions equal `confirm_v1` exactly; the pilot run's questions equal `pilot_v1` exactly |
| Records | 7 runs, 0 duplicate record keys, 0 corrupt lines; status `completed` for all |
| Model and decoding | one generator signature in every run: Qwen/Qwen2.5-7B-Instruct `a09a35458c70…`, bf16, greedy (`do_sample=False`, `num_beams=1`), batch size 1, prompt `qa-v2`, `max_time_s` 60 |
| Hardware | every run on PCI bus 1 (physical GPU 0), no MPS pipe |
| Cache reuse | prompts reused across runs are byte-identical, and no prompt has more than one output within a run (0 divergent). Cached shares: F_exp1 5,043 / 44,784 (identical prompts across representations); C_exp1 13,312 / 15,750 (the 200 focused questions from A_exp1) |
| Failed or missing conditions | 0 generation errors. Unavailable by design: C_exp1 500 (R3 on HoVer/FEVER), C_exp2 2,664 (P7; P2 on R1 or without edges; P3 with a single item; P4 without a pool; P6 without a negation), C_exp3 1,750 (no human-verified structure). F_exp1: 0 unavailable |
| Protocol A fact identity | for each of the 4,976 confirmatory and 350 pilot questions, every representation showed one identical fact digest (0 violations). `passage_chars_outside_facts` = 0 for every Protocol A record, so R0 shows no text that R1 does not |
| Protocol B accounting | recomputed from `budget_accounting`. At 1.0×, per-representation: kept 0.834 / 0.806 (R0, 2Wiki / MuSiQue) vs R1 0.644 / 0.654, R4 0.632 / 0.620, R5 0.644 / 0.654. Answer-bearing facts dropped: 0.11 / 0.19 vs 0.33–0.34 / 0.28–0.35 |
| GPU time | run manifests 9.48 h; driver wall-clock (including model loading) 9.53 h; preflight < 0.1 h. Remaining under the 24 GPU-h ceiling at the start of revision-1: about 14.4 h |

## 2. Timeline: what was frozen before which outcome

| artefact | commit (time, +03:00) | first outcome it could have seen |
|---|---|---|
| `docs/PILOT_PROTOCOL.md`, `pilot_v1.json` | `7311217` (2026-10-11 00:05) | pilot runs began 2026-10-12 09:52 UTC = 12:52 +03:00. **Frozen before the pilot.** No changes to PILOT_PROTOCOL after the first pilot run (the batch-size deviation entry `7f61ac3` predates it) |
| `docs/CONFIRMATORY_PROTOCOL.md` | `0850982` (2026-10-12 13:36:01) | written after the focused pilot (designed from its variance), **before** the confirmatory sample existed |
| `confirm_v1.json`, `configs/confirm.yaml` | `508b199` (13:36:48) | drawn after the protocol commit; the confirmatory run started 12:56 UTC = 15:56 +03:00. **Frozen before the confirmatory outcomes** |

The six primary contrasts, the metric (EM), Protocol A and the Holm family were fixed in PILOT_PROTOCOL before any generation. The ±0.02 equivalence margin was "proposed" there and fixed as a secondary check in CONFIRMATORY_PROTOCOL. The confirmatory sample size was set from pilot data, as pre-specified. **Correction:** "pre-registered" in the draft overstates this. The protocols were committed to our own version-controlled repository with timestamps, not to an external registry, so the revision says "pre-specified".

## 3. Claim → artefact table (draft at `d18cf77`)

| paper claim (location) | value in draft | recomputed | artefact | status |
|---|---|---|---|---|
| 2Wiki R1−R0 ΔEM (abstract, §6.1) | −0.017 [−0.029, −0.005] | −0.0167 [−0.0288, −0.0046]; numpy [−0.0291, −0.0040] | F_exp1 predictions | ✓ |
| 2Wiki R1−R0 p_Holm | 0.018 | 0.018 (p_boot 0.003 × 6) | F_exp1 | ✓ |
| MuSiQue R1−R0 | −0.001 [−0.014, +0.014] | −0.0006 [−0.0138, +0.0138] | F_exp1 | ✓ |
| R5−R1 MuSiQue / 2Wiki | −0.011 / −0.008 | −0.0115 / −0.0080 | F_exp1 | ✓ |
| R4−R5 MuSiQue / 2Wiki | +0.010 / +0.006 | +0.0103 / +0.0059 | F_exp1 | ✓ |
| Equivalence within ±0.02 (MuSiQue R1−R0; 2Wiki R5−R1, R4−R5) | yes / yes / yes | bootstrap 90 % CI inside ±0.02: yes / yes (upper bound 0.000) / yes. Paired TOST, normal approximation, Holm over 6: p = 0.011 / 0.041 / 0.0025 | F_exp1 | ✓, but the procedure needs wording (§4) |
| R4P−R4 2Wiki / MuSiQue | −0.036 / −0.045 | −0.0359 / −0.0447 | F_exp1 | ✓ numerically; **interpretation confounded** (§4) |
| R2−R1 2Wiki | −0.024 [−0.036, −0.012] | −0.0243 | F_exp1 | ✓ |
| Decomposition: 2Wiki R1−R0 abstention 250 / 81 | 250 / 81 | transition matrix: C→A 87, W→A 163 (250 total); A→C 29, A→W 52 (81) | F_exp1 | ✓ |
| 9,688 CONTRADICTS lines in 2Wiki prompts | 9,688 | 9,697 rendered `Ea CONTRADICTS Eb` lines (12,816 predicted edges, 12,372 rendered; the rest were cut by the 40-line cap) | F_exp1 | **minor discrepancy (0.1 %)**: the earlier regex missed lines; corrected to 9,697 |
| 63 % of 2Wiki R4P prompts with ≥1 contradiction line | 63 % | 2,034 / 3,232 = 62.9 % | F_exp1 | ✓ |
| Pilot budget: structured formats keep 15–20 pp fewer facts | 15–20 pp | R0 − {R1, R4, R5}: 2Wiki 0.190–0.202, MuSiQue 0.152–0.186 | C_exp1 | ✓ (pilot only; the abstract omitted "pilot", **corrected**) |
| Exp0 B4−B1 2Wiki / MuSiQue | −0.15 [−0.23, −0.07] / −0.09 [−0.15, −0.04] | identical | A_exp0 | ✓ |
| Exp0 tokens: B2/B3 1,390–1,711; B1 501–538; B4 442–489 | as stated | identical | A_exp0 | ✓ |
| Exp2 P2 2Wiki R4 rate 0.4 | −0.10 [−0.18, −0.01], n = 71 | −0.0986 [−0.1831, −0.0141], n = 71 | C_exp2 | ✓ |
| Exp2 P4 HotpotQA R1 / MuSiQue R1 at 0.4 | −0.16 / −0.09 | −0.16 [−0.28, −0.04] / −0.09 [−0.17, −0.01] | C_exp2 | ✓ |
| Compute about 10 GPU-hours | about 10 | 9.48–9.53 (+ < 0.1 preflight) | manifests | ✓ |
| "Dissecting GraphRAG could not be found" (paper README, references.bib comment) | not cited | **wrong**: Nishida et al., TACL 14:627–655 (2026), doi 10.1162/tacl.a.615, exists. This was a search failure on our side | ACL Anthology | **corrected**, now cited |

## 4. Discrepancies and interpretation problems

1. **R4P−R4 is not a relation-quality effect.** R4P recomputes the item order from the predicted graph and has a different number of relation lines. The draft's "loss concentrated where the predictor marked compatible facts as contradictory" was a correlational subset analysis.
   - Fix: fixed-order factorial controls (`relation_controls.py`; `docs/CONTRADICTION_MECHANISM_AUDIT.md`).
2. **"Pre-registered"** → "pre-specified (committed before sampling)".
3. **Equivalence wording.** The draft applied a bootstrap 90 % CI inside ±0.02 per test, without multiplicity adjustment. The stricter Holm-adjusted TOST over the six tests gives the same conclusions (all three p_Holm < 0.05), so the claims stand. The paper now states the procedure. See `docs/STATISTICAL_REVIEW.md`.
4. **"Sentence items" vs "claims".** R1 units are dataset sentences, some of them context-dependent (for example, pronoun-initial). The draft mostly said "sentence items", but the title framing and some sentences ("claims, reasoning paths and graphs") suggested LLM claim extraction. The revision narrows this language.
5. **Budget results are pilot-only** (n = 100 per dataset). The abstract presented them without that qualifier; corrected.
6. **CONTRADICTS line count** 9,688 → 9,697.
7. **Missing closest related work** (Nishida et al., TACL 2026); added.

No confirmatory number changed.
