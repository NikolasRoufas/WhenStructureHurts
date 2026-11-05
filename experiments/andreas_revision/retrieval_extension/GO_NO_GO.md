# Experiment D: retrieved-evidence extension, GO/NO-GO (2026-11-05)

**Decision: NO-GO for a new large retrieval run now (deferred, not rejected).** No retrieval inference was run
for this decision.

## Evidence used

**The existing retrieval run** (`retr_v1`): 500 MuSiQue + 500 2Wiki questions on fresh samples. The pipeline is
BM25 → cross-encoder → top 4 passages, fixed per question. Run `results/revision/exp1/20261012-210958_37616258`;
outputs `research_outputs/revision/retrieval/` in tag `research-record-revision2`.

**The unused-question count** (`audits/expD_unused_pool.json`), computed with the project's eligibility rules,
excluding every earlier sample:

| | dev questions | used by earlier samples | unused and eligible |
|---|---|---|---|
| MuSiQue | 2,417 | 2,347 | **70** (all 2-hop) |
| 2Wiki | 12,576 | 6,435 | **5,057** (2,771 compositional, 1,288 comparison, 998 bridge-comparison; no inference) |
| HotpotQA | 7,405 | 3,853 | **2,193** (bridge only; comparison exhausted) |

## The gate criteria

| criterion | finding |
|---|---|
| Unused, non-leaking questions | Enough for 2Wiki and HotpotQA. **None usable for MuSiQue** (70). The remaining pools are type-skewed: HotpotQA is bridge only, and 2Wiki has no inference questions. |
| Retrieval recall / supporting-evidence coverage | Support coverage 0.61 (MuSiQue), 0.78 (2Wiki); complete support for 149/500 and 262/500 questions; partial for 311 and 238; none for 40 MuSiQue questions. |
| Questions with predicted contradiction lines | High: R4P ≠ R4P_NC for 369/500 (MuSiQue) and 390/500 (2Wiki) questions, i.e. 74 % and 78 %. |
| Is the phenomenon visible under retrieval? | Yes, already. R4P − R4P_NC (contradiction lines on − off, same order): **−0.022 [−0.038, −0.008]** (MuSiQue) and **−0.024 [−0.046, −0.004]** (2Wiki). Abstention is +4.0 and +6.8 points. |
| Complete vs partial evidence | MuSiQue complete −0.047 [−0.094, −0.007] vs partial −0.013 [−0.026, −0.003]. 2Wiki complete −0.019 [−0.050, +0.011] vs partial −0.029 [−0.055, −0.008]. The subgroups are too small for a clean comparison. |
| Expected precision of a new run | With 1,000 2Wiki + 1,000 HotpotQA questions, about 75 % affected and a paired SD of about 0.25, the 95 % CI half-width is about ±1.8 points per dataset (about ±2.5 points within the complete-support stratum). |
| Cost | Four conditions × 2,000 questions ≈ 6,000 uncached Qwen generations plus retrieval and NLI: about 2–3 GPU-hours on GPU 1. |

## Reasoning

1. **The question the extension would answer is already answered in direction and approximate size.** Under
   real retrieval, contradiction lines lower EM by 2–2.5 points on both datasets, with CIs excluding 0. A larger
   run would mostly narrow intervals around a known effect.
2. **The open questions for the journal version are elsewhere.** They are whether the predicted contradictions
   are genuine (A), whether removing the false ones restores accuracy (B), and whether the effect holds for
   another model family (C). D cannot address A or B: there are no human labels for retrieved pairs.
3. **No MuSiQue questions remain,** and the HotpotQA pool is bridge-only. A new run would therefore not
   replicate the MuSiQue retrieval result, and its HotpotQA population would differ from confirm2's.
4. GPU time is better reserved for Experiment B once labels exist.

## Conditional GO (if a reviewer or the supervisor asks for it)

The design below is specified now, so that a later run is prospective. It must be frozen in the protocol
before the sample is drawn.

- **Sample:** 1,000 2Wiki (stratified by type over the three remaining types) + 1,000 HotpotQA (bridge).
  Seed 13, drawn with `wsh questions freeze`, excluding `excluded_confirm2.json` plus `confirm2_v1`.
- **Retrieval:** the `retr_v1` pipeline unchanged. Passages are retrieved once per question, and the same
  passages and order are used in every condition.
- **Conditions:** R5 (retrieved sentences, no relation lines); R4P_FO (predicted relations at that order);
  R4P_FO_NC; R4P_FO_CN (contradiction labels → RELATED_TO).
- **Primary:** R4P_FO − R4P_FO_NC EM on affected questions, Holm over the 2 datasets.
- **Secondary:** R4P_FO − R5 and R4P_FO_CN − R4P_FO_NC, with abstention and wrong-answer rates; strata by
  complete / partial / no support (gold labels used only to stratify); token counts per condition.
- **Status:** a prospective exploratory replication on fresh questions. It is not part of any confirmatory family.
