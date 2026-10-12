# Reviewer self-critique (revision-1, 2026-10-13)

Three simulated ACL/EMNLP reviewers read the revised draft (`paper/main.pdf`, 8 pages + appendix). Each scores on the ARR scale (soundness 1–5, excitement 1–5) and gives the strongest argument for rejection. Afterwards we list what we changed in response and what cannot be fixed without new data or authorisation.

## Reviewer A: methodology

**Summary.** The paper holds gold evidence fixed and varies its presentation; a pre-specified test on 4,976 questions finds no effect of order or derived relation lines and a small abstention-driven cost of sentence items; exploratory fixed-order controls attribute the cost of predicted relations to contradiction lines.

**Strengths.** Per-question fact-identity verification; byte-identical pair counts; one-factor controls (on/off contradiction lines at fixed order; typed vs neutral labels at the same pairs and line count) are proper interventions, not correlational strata; the zero-contradiction stratum acts as a built-in placebo (exactly 0 change).

**Weaknesses.**
1. *Single reader.* Every effect is from Qwen2.5-7B-Instruct. The mechanism (abstention) is plausibly model- and instruction-specific; the prompt-factor experiment shows it largely is.
2. *Are the contradictions false?* The paper argues the harm comes from asserting conflicts the sources do not contain, but the falsity is established only by heuristic triage. If many predicted conflicts are real (e.g. different dates of one event), the finding becomes "showing conflicts makes the model cautious", which is less surprising.
3. *Derived structure is the "good structure".* With 25–33 % fallback anchors and no human verification, the null for derived relations is a null for *this* structure, not for correct structure.
4. *Retrieved evidence.* The replication is 500 questions/dataset, and annotation structure almost never survives retrieval, so "correct structure on incomplete evidence" is untested.

**Soundness 3.5 / Excitement 3.** **Strongest rejection argument:** the main positive finding is an abstention artefact of one model under one instruction, demonstrated on post-hoc controls.

## Reviewer B: novelty and positioning

**Summary.** A controlled study of evidence presentation in RAG, positioned against GraphRAG analyses.

**Strengths.** The closest work (Nishida et al., TACL 2026) measures extraction noise through the retrieval pipeline; this paper isolates the *presentation* of incorrect relations next to fixed, correct evidence. That is a distinct, cleanly separated question. The budget accounting (formatting overhead as evidence loss) is useful and seldom reported.

**Weaknesses.**
1. "Structure does not help when the facts are complete" may be seen as expected; GraphRAG-Bench and Han et al. already report task-dependent or absent gains.
2. "Noisy relations hurt" is known in spirit (Nishida et al.; LinearRAG's motivation). The incremental claim is the *channel* (abstention) and the *locus* (contradiction labels, not order or line count).
3. The NLI relation predictor is a weak, simple choice; modern GraphRAG systems extract relations with LLMs. Would LLM-extracted relations show the same contradiction behaviour?
4. Sentence units are not propositions; the title promises more about "transformations" than sentence segmentation delivers.

**Soundness 3.5 / Excitement 2.5.** **Strongest rejection argument:** a careful but narrow increment over Nishida et al. 2026 and GraphRAG-Bench, with a weak relation predictor that practitioners do not use.

## Reviewer C: statistics and reproducibility

**Strengths.** Confirmatory family fixed before sampling and committed to version control; power from the pilot; Holm correction; equivalence margin fixed in advance and now checked with Holm-TOST too; exploratory work labelled as such throughout; paired bootstrap with recorded seed; every number mapped to a file and run with prediction hashes; raw predictions retained.

**Weaknesses.**
1. "Pre-specified", not pre-registered with a third party; the paper says this correctly.
2. The fixed-order controls reuse the confirmatory questions after their R4P−R4 result was seen; their CIs are not multiplicity-corrected (about 12 contrasts). The main contradiction contrast would survive any reasonable correction (CI upper bound −0.023 / −0.025), but the smaller ones (order-only +0.018 on MuSiQue) would not be safe.
3. The prompt × representation interactions are inconclusive (CIs touch or include 0), so "largely vanished" rests on point estimates of within-prompt contrasts. The paper should say "shrank" and give the intervals (it does).
4. The pilot overestimated the confirmed effect fourfold; pilot-only results (Protocol B, Exp0, Exp2) should carry little weight. They are in the appendix.
5. Greedy decoding at batch size 1 is deterministic for this reader, but other hardware may differ slightly; the preflight shows batching changed 3 of 8 outputs.

**Soundness 4 / Excitement 3.** **Strongest rejection argument:** none on statistics alone; the reviewer would defer to A on generality.

## Meta-review simulation

Likely outcome at a main track: *borderline, leaning Findings*. The design and reporting are above average; generality (one reader) and the unverified falsity of the contradictions are the decisive concerns.

## What we changed in response (this revision)

| concern | change |
|---|---|
| R4P confounds order, line count and labels | fixed-order controls R4P_FO, R4P_FO_NC, R4N_FO, R5P, R4P_NC run (§6.3, Table 3, Fig. 4) |
| Effects may be abstention artefacts | transition analysis (Table 12); prompt factor without the abstention line (§6.5, Table 14); claims rephrased as conditional on the instruction |
| Gold evidence only | retrieved-evidence replication on 1,000 fresh, disjoint questions (§6.4, Tables 4, 16, 17) |
| Exp0 unequal budgets | budgets and costs explicit (Table 18); no architectural conclusion drawn |
| Novelty vs Nishida et al. 2026 | cited and positioned in Intro and Related Work; claim narrowed to presentation of relations with content fixed |
| "Propositions" overclaim | text says *sentence items*; Limitations "Sentence units, not propositions" |
| Equivalence wording | per-test 90 % CI rule (pre-specified) plus Holm-TOST (added; agrees) |
| Overfull boxes, crowded appendix | fixed; long source paths break; three appendix tables widened |

## What cannot be fixed without new data or authorisation

1. **Second reader.** Configured (`configs/revision_second_reader.yaml`; Mistral-7B-Instruct-v0.3 or OLMo-2-1124-7B-Instruct, pinned revisions) but needs explicit authorisation to download and about 5.5 GPU-hours (≈ 12 h of the 24 h ceiling remain).
2. **Human labels** for the 240 blinded contradiction pairs and the structure-verification package (`docs/REMAINING_HUMAN_VERIFICATION.md`). Until then, "the contradictions are false" stays an inference.
3. **LLM-extracted relations** in place of the NLI predictor (Reviewer B.3): a new experiment, not yet designed.
4. **A genuinely confirmatory test** of the contradiction effect would need a fresh sample and a new pre-specified protocol.
