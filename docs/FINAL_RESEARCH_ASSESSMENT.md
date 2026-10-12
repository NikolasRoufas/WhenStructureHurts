# Final research assessment (revision-1, 2026-10-13)

**Verdict: PROMISING_BUT_ADDITIONAL_VALIDATION_REQUIRED**

The confirmatory test is valid, complete and fully reproduced by an independent audit. The revision added three exploratory experiments (about 2.5 GPU-hours) that turn the draft's most interesting secondary observation into a located, intervention-based finding: predicted *contradiction* relations, shown next to fixed and correct evidence, make Qwen2.5-7B-Instruct abstain, costing about 3 EM points; the order and the number of relation lines do not. The finding replicated on 1,000 fresh questions with real retrieval, and it shrank when the abstention option was removed. Two things keep this below READY_FOR_INTERNAL_REVIEW as a main-track paper: everything comes from **one reader**, and the claim that the contradictions are **false** rests on automatic triage, not human judgement. Both have prepared, ready-to-run remedies (a configured second reader; a blinded 240-pair annotation package).

Sources: `paper/CLAIMS_EVIDENCE_AUDIT.md`, `docs/REPRODUCIBILITY_CHECKLIST.md`, `docs/REVISION_EXPERIMENT_LOG.md`, and the per-topic reports listed at the end.

---

**1. What did we actually discover?**

*Confirmatory* (six pre-specified tests, Qwen2.5-7B-Instruct, gold evidence, n = 1,744 MuSiQue / 3,232 2Wiki, Holm over 6):
- Sentence items lower 2Wiki EM by 0.017 [−0.029, −0.005], p_Holm 0.018; on MuSiQue −0.001, equivalent to zero within ±0.02.
- Graph-derived order and derived relation lines: not significant on either dataset; on 2Wiki equivalent to zero within ±0.02 (per-test rule and Holm-TOST agree).

*Exploratory, interventions on the confirmatory questions:*
- The sentence-item cost is abstention: +5.2 points abstention, accuracy among questions answered under both formats unchanged (+0.002).
- With order and line count fixed, showing predicted CONTRADICTS lines costs 3.3 EM points on both datasets (CIs exclude zero by ≥ 2.3 points) and raises abstention by 6 points. Replacing all labels with a neutral `RELATED_TO` at the same pairs and line count recovers a similar amount. Predicted order alone: +0.002 / +0.018. With no contradiction line in the block, relabelling changes nothing (−0.003).

*Exploratory, fresh retrieved-evidence sample (500 + 500):* predicted relations −3.6 / −3.0 points, contradiction lines −2.2 / −2.4, largest when retrieval was complete; sentence items inconclusive (2Wiki −0.026 [−0.054, +0.002]).

*Exploratory, prompt factor (1,000 2Wiki):* removing the "insufficient evidence" line cuts abstention from 20–33 % to under 1 %, raises EM 8–13 points for every format, and shrinks R1−R0 to −0.004 and R4P−R4 to −0.017 (interactions +0.019, CIs touch or include 0).

**2. Did explicit graph structure improve reasoning?**

No. Derived relation lines at fixed order: +0.010 (MuSiQue), +0.006 (2Wiki, equivalent to zero). They slightly raise accuracy among answered questions (+0.014) but also abstention, and the two cancel. Predicted relations hurt.

**3. Did ordered claims perform differently from graphs?**

No detectable difference. R5−R1 −0.011 / −0.008; R3−R5 −0.007 / −0.004; R4−R5 +0.010 / +0.006, none significant. Shuffling hurt on 2Wiki only (R2−R1 −0.024). Predicted order (R5P−R5) +0.002 / +0.018.

**4. How much evidence was lost through representation transformations?**

None under Protocol A (verified per question, 0 violations in all runs). Under a 1.0× content-token budget (pilot), passages keep 0.81–0.83 of the facts against 0.62–0.65 for itemised formats; answer string present 0.85 vs 0.64–0.66 (2Wiki). On fresh retrieved evidence, R0 keeps 0.82–0.84 vs 0.67–0.68 for R1. In Exp0, B2–B4 cost about 15 extraction calls and about 24 s per question, and budgets are unequal, so no architectural conclusion is drawn.

**5. Which perturbations caused the largest failures?**

Pilot, rate 0.4, label-preserving: hard distractors (P4, up to −0.16 EM, negative in every QA cell) and relation corruption on 2Wiki R4 (−0.10). Removing required facts (P1) produced the largest behavioural change (abstention 0.43 → 0.72 MuSiQue). Among the revision interventions, asserting contradictions is the largest presentation-only harm (−3.3, up to −13 points with 6+ lines on MuSiQue).

**6. Which results were statistically inconclusive?**

- Confirmatory: R5−R1 and R4−R5 on MuSiQue.
- Revision: retrieved-evidence R1−R0 on both datasets; both prompt × representation interactions; noabst R4P−R4 (upper bound 0.000); small strata (e.g. 6+ lines on 2Wiki, −0.020 [−0.043, +0.002]).
- Pilot: almost all Protocol B and Exp2 cells, Exp0 B2/B3 vs B1, HoVer and FEVER throughout.
- The revision contrasts are not multiplicity-corrected; only the main contradiction contrast is robust to any reasonable correction.

**7. What do our results establish beyond existing GraphRAG studies?**

Nishida et al. (TACL 2026) show that noisy extracted triples hurt GraphRAG *through retrieval and clustering*. GraphRAG-Bench, Han et al. and Zhou et al. compare whole pipelines. We add: (i) a fact-identical, pre-specified null for derived order and relation lines with a 7B reader; (ii) intervention evidence that incorrect relations hurt even when merely *displayed* next to fixed correct evidence, located in the contradiction label, not in order or line count; (iii) the channel: abstention under an instruction that permits it; (iv) formatting overhead quantified as evidence loss. The increment is clear but narrow; see `docs/NOVELTY_AND_RELATED_WORK_AUDIT.md`.

**8. Which experiments remain incomplete?**

| item | status | what unblocks it |
|---|---|---|
| Second reader (cross-family replication) | configured, not run | your authorisation to download Mistral-7B-Instruct-v0.3 (or OLMo-2-1124-7B-Instruct); about 5.5 GPU-h, ≈ 12 h remain |
| Human labels for 240 contradiction pairs | package ready, no labels | 2–3 annotator-hours; importer validates |
| Human structure verification; Exp3; control C4 | not run | the 50-question verification package |
| LLM-extracted relations instead of NLI | not designed | new protocol |
| Confirmatory test of the contradiction effect | not run | fresh sample + new pre-specified protocol |
| Protocol B / Exp0 / Exp2 at scale | pilot only | compute |

**9. How strong is the paper for an ACL/EMNLP main conference?**

Borderline. Soundness is above the norm for the area (pre-specification, verification, audit, interventions); excitement is moderate. Simulated reviewers (`paper/REVIEWER_SELF_CRITIQUE.md`) give soundness 3.5–4 and excitement 2.5–3; the likely outcome today is Findings. A second reader that reproduces the contradiction effect, plus human labels showing the contradictions are false, would move it to a competitive main-track submission.

**10. What additional work would most improve its scientific contribution?**

1. Second reader on the confirmatory questions with the fixed-order controls (needs your authorisation; about 5.5 GPU-h; fits the ceiling).
2. Human labels for the 240 blinded contradiction pairs (no compute).
3. A fresh-sample, pre-specified test of contradiction lines on vs off (about 1 GPU-h), making the main finding confirmatory.
4. LLM-extracted relations as the predictor, to show the effect is not an artefact of a small NLI model.
5. Human-verified structure, enabling Exp3 and control C4.

## Reports written in this revision

`docs/REVISION_BASELINE_AUDIT.md`, `docs/CONTRADICTION_MECHANISM_AUDIT.md`, `docs/RETRIEVAL_GENERALIZATION_REPORT.md`, `docs/STATISTICAL_REVIEW.md`, `docs/NOVELTY_AND_RELATED_WORK_AUDIT.md`, `docs/REVISION_EXPERIMENT_LOG.md`, `docs/REMAINING_HUMAN_VERIFICATION.md`, `docs/REPRODUCIBILITY_CHECKLIST.md`, `docs/REVISION_PROTOCOL.md`; `paper/CLAIMS_EVIDENCE_AUDIT.md`, `paper/REVIEWER_SELF_CRITIQUE.md`, `paper/SUBMISSION_READINESS.md`.
