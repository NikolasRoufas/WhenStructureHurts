# ACL revision audit (revision-2, 2026-10-13)

This audit checks the paper's quantitative claims against the raw saved predictions. It extends `docs/REVISION_BASELINE_AUDIT.md` (revision-1), which holds the claim-by-claim table for the original draft. Nothing in the historical confirmatory analysis was modified: the original outputs are at tag `pre-revision-baseline` (`d18cf77`), and every revision output is written to new files.

## 1. Independent re-execution

`scripts/audit/verify_claims.py` re-derives every central number from `predictions.jsonl`, independently of the analysis pipeline (`scripts/analysis/build.py`). It has its own record loader and per-question aggregation, a re-implementation of the frozen percentile bootstrap, an independent numpy bootstrap (seed 12345, 20,000 resamples), its own Holm adjustment, a paired TOST with Holm and an exact McNemar test. It was **re-executed on 2026-10-13** (`/data/roufas/wsh_revision/audit2/`). Its `audit.json` and `claims_check.csv` are **byte-identical** to the revision-1 outputs (`research_outputs/revision/audit/`), apart from the timestamp.

| quantity | value (recomputed) |
|---|---|
| confirmatory questions | 4,976 unique (1,744 MuSiQue + 3,232 2Wiki); equal to `confirm_v1.json` |
| generation records | 44,784 (9 conditions × 4,976); 0 duplicate keys; 0 corrupt lines |
| uncached generations | 39,741; 5,043 served from the cache because the prompts were byte-identical |
| generation failures | 0 generation errors, 0 pipeline errors, 0 unavailable; 42 answers truncated at 64 tokens (scored, kept) |
| Protocol A fact identity | 0 violations: one fact digest per question across all representations |
| paired questions per contrast | 1,744 / 3,232 (all questions available in both conditions; no availability loss) |
| identical prompts | R1−R0: 3 / 44; R5−R1: 522 / 1,858; R4−R5: 0 / 879 (MuSiQue / 2Wiki) |
| 2Wiki R1−R0 | −0.0167 [−0.0288, −0.0046] (frozen bootstrap); numpy [−0.0291, −0.0040]; p_boot 0.003; p_Holm 0.018 |
| MuSiQue R1−R0 | −0.0006 [−0.0138, +0.0138]; 90 % CI inside ±0.02; TOST-Holm p 0.011 |
| R5−R1 (MuSiQue / 2Wiki) | −0.0115 / −0.0080; p_Holm 0.535 / 0.535; equivalence: no / yes (TOST-Holm 0.233 / 0.041) |
| R4−R5 (MuSiQue / 2Wiki) | +0.0103 / +0.0059; p_Holm 0.535 / 0.535; equivalence: no / yes (TOST-Holm 0.212 / 0.0025) |
| R4P−R4 (secondary) | −0.0447 / −0.0359 |
| GPU time before revision-1 | 9.48 h (manifests) / 9.53 h (driver wall-clock) |

Every number in the baseline list of the task brief reproduces: 4,976 questions; 44,784 records; six primary contrasts; the 1.7-point 2Wiki decline; null structure effects; −3.6 to −4.5 for R4P−R4; abstention as the main channel; pilot-level budget loss.

## 2. Chronology (git commit times, +03:00; run times from manifests, UTC)

| artefact | commit / time | relation to outcomes |
|---|---|---|
| `PILOT_PROTOCOL.md`, `pilot_v1.json` | `7311217`, 2026-10-11 00:05 | before every GPU run (first pilot run 2026-10-12 09:52 UTC) |
| `CONFIRMATORY_PROTOCOL.md` | `0850982`, 2026-10-12 13:36:01 (10:36 UTC) | after the focused pilot; before the confirmatory sample existed |
| `confirm_v1.json`, `confirm.yaml` | `508b199`, 13:36:48 | sample drawn after the protocol commit |
| confirmatory run `full/exp1/20261012-125639_49dfe135` | 12:56 → 18:30 UTC | started 2 h 20 min after the protocol was frozen. `CONFIRMATORY_PROTOCOL.md` has **no later commit**, so it was never edited after outcomes were seen |
| revision-1 protocol `REVISION_PROTOCOL.md` | `34356e5`, before `retr_v1` was drawn | exploratory; designed after the confirmatory result |
| revision-1 runs (controls, retrieval, no-abstention prompt) | 2026-10-12 20:09 → 22:37 UTC | exploratory |
| `CONFIRMATORY_PROTOCOL_2.md` | `6648eef`, 2026-10-13 03:39 (00:39 UTC), pushed to GitHub | before `confirm2_v1` was drawn (`6ccdc8b`) and before any generation on it |
| revision-2 runs | from 2026-10-13 00:52 UTC | see `docs/REVISION_EXPERIMENT_LOG.md` |

**Conclusion.** The original confirmatory protocol was frozen before any confirmatory output existed. It was "pre-specified" in our own version-controlled repository, not registered externally; the paper uses that wording.

## 3. Statistical implementation (checked)

- **Unit and test.** The sampling unit is the question. Each paired difference is a difference in question-level EM; R2 seeds are averaged within a question before pairing.
- **Bootstrap.** Percentile CI, 2,000 resamples, seed 0. The two-sided p-value is computed as 2·min(P(d* ≤ 0), P(d* ≥ 0)). When no resample crosses zero this gives p = 0; we report that as p < 0.0005 (= 1/2,000).
- **Holm family.** Exactly the six pre-specified tests. Equivalence (±0.02) was pre-specified as a per-test 90 % CI rule; the stricter Holm-TOST, added in revision-1, agrees for every test.
- **Identical prompts.** Identical-prompt pairs stay in the estimate, as their difference is 0 by construction, and are counted in every table. The *informative* estimate restricted to non-identical pairs is reported alongside.
- **Exclusions.** Smoke and prompt-development questions (15) and the pilot (350) are excluded from the confirmatory set; there are no post-hoc exclusions.
- **Determinism.** Greedy decoding at batch size 1; unbatched outputs were identical across runs in the preflight. No prompt has two different outputs in any run.

## 4. New findings of this audit (revision-2)

1. **Fixed-order controls: two small implementation asymmetries**, found by `scripts/revision/serialization_audit.py` and quantified in `research_outputs/revision2/serialization/`.
   - *Contradiction removal.* R4P_FO_NC is a pure deletion of R4P_FO's contradiction lines in 4,044 / 4,976 questions. In another 913 every relation line was a contradiction, so the `Relations:` header disappears as well. In 19 (0.4 %), removing contradiction lines admitted lines that the 40-line cap had cut from R4P_FO.
   - *Neutral labels.* In 442 questions R4N_FO has 1–3 fewer lines than R4P_FO, because relabelling to `RELATED_TO` makes two lines on the same ordered pair identical, and the layout deduplicates them.
   - *Sensitivity.* Excluding these questions leaves the contrasts unchanged:

     | contrast | 2Wiki | MuSiQue |
     |---|---|---|
     | contradiction lines on − off, all questions | −0.0334 | −0.0327 |
     | same, excluding the 19 cap-affected questions | −0.0339 | −0.0327 |
     | typed − neutral labels, all questions | −0.0371 | −0.0298 |
     | same, excluding the 442 deduplicated questions | −0.0333 | −0.0292 |

     Source: `control_sensitivity.json`. The paper's wording "the same pairs and number of lines" for R4N_FO is corrected to "the same pairs (1–3 fewer lines in 9 % of questions)".
2. **Provenance repetition.** R0 shows a source title once per passage (2.5–2.8 per prompt), while the item formats repeat it for every sentence (10.7–12.5). This is part of what "sentence items" means in our design, not a leak: titles are identical in content across formats, and answer-in-evidence is the same for all Protocol A formats.
3. **No other discrepancy.** Every confirmatory, exploratory and revision-1 number in the current manuscript traces to a file listed in `paper/CLAIMS_EVIDENCE_AUDIT.md`.
