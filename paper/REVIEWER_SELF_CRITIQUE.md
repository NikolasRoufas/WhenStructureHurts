# Reviewer self-critique

This critique is written as a sceptical ACL/EMNLP reviewer would write it, against the draft of 2026-10-12.

## Summary of the submission

The paper presents the gold evidence of multi-hop questions in seven representations under an information-controlled protocol and a budget-controlled protocol. It pre-registers six contrasts and tests them on 4,976 held-out questions with one 7B reader. Results:
- derived structure has no detectable effect;
- sentence items slightly lower EM on one dataset, through abstention;
- predicted relations hurt, concentrated where the predictor asserts spurious contradictions.

## Strengths

- **Clean design.** Fact identity is verified per question. The budget is controlled with a fixed, gold-free ranking. Identical-evidence pairs are counted.
- **Statistical discipline that is rare in this area.** A frozen pilot, a pre-registered confirmatory protocol committed before sampling, sample sizes from the pilot variance, Holm correction, an equivalence margin, and an explicit exploratory/confirmatory split.
- **Mechanistic insight that is checkable.** The abstention decomposition, and the spurious-contradiction analysis with concrete examples.
- **Honest reporting.** Null results, the pilot overestimate (−0.07 vs −0.017), unexecuted experiments, and analyses added post hoc are all disclosed.

## Weaknesses

1. **Novelty versus the closest prior work.**
   - GraphRAG-Bench (Xiang et al., ICLR 2026), the RAG vs GraphRAG study (Han et al.) and the unified graph-RAG analysis (Zhou et al., PVLDB) already show that graphs do not uniformly help.
   - Our addition is the controlled, fact-identical comparison and the measured cost of noisy relations. That is a clear but narrow increment. A reviewer may see "structure has no effect when the facts are complete" as expected.
   - The strongest novel finding, that spurious contradictions cause abstention, rests on a *secondary* contrast. Its mechanism comes from an analysis added after the result.
2. **Single generator and single prompt.**
   - Every effect is mediated by abstention under a prompt that offers *insufficient evidence*.
   - Without a second model family, or a no-abstention prompt, the findings may be a property of Qwen2.5-7B-Instruct plus this template. This is the most likely reason for rejection.
3. **Gold evidence only for the controlled experiments.** The setting in which structure plausibly helps (scattered, partial, retrieved evidence) is tested only in the 100-question pilot (Exp0). So the null result says little about real graph-RAG pipelines.
4. **Derived, unverified structure.**
   - 25–33 % of primary questions have fallback-anchored edges.
   - The human-verification package is untouched, so "correct structure has no effect" is not established, only "derived structure of this quality".
   - Exp3 (component attribution) was not run.
5. **R4P confound.** R4P changes the relation *types*, the *number* of relation lines and the *order* at once. The "misleading relations" interpretation is plausible and supported by the P2 pilot perturbation, but it is not isolated. A clean test would remove only the CONTRADICTS lines from R4P.
6. **Baseline fairness (Exp0).**
   - B2/B3 see about 3× the tokens of B0/B1.
   - B4 is our reconstruction with many self-chosen components, a 450-token budget and at most 12 claims.
   - Exp0 is pilot-only (n = 100 per dataset).
   - Its conclusions (B4 loses evidence at selection) should not be read as statements about the original EG-RAG.
7. **Statistical power of the pilot-only parts.** Protocol B, Exp0 and Exp2 are n = 100 or 50 with about 50 cells in Exp2. Several "significant" cells are expected by chance. The paper says so, but the budget finding (H4) rests on deterministic accounting plus inconclusive EM differences.
8. **Metric.** Exact match with SQuAD normalisation and no diacritic folding is strict. A secondary check shows little impact. The NLI groundedness metric looks broken for short answers and is reported but not interpreted; a reviewer may ask why it is computed at all.
9. **Presentation.** The paper is dense. Six tables and four figures moved to the appendix to meet 8 pages. Several numbers that support Discussion claims live only in appendix tables.

## Is the evidence sufficient for an ACL/EMNLP main-track paper?

**Not yet.** In its current form it is a solid Findings or workshop paper: rigorous and honest, with one confirmed small effect, informative nulls and an interesting secondary mechanism. For the main track, a reviewer would most likely require:
1. at least one more generator family (and ideally a larger model);
2. a no-abstention prompt variant, or a reader without an abstention option, to show the effects are not just abstention calibration;
3. the clean R4P ablation (predicted relations without CONTRADICTS lines, and with the derived order held fixed), run as a pre-specified test;
4. a retrieved-evidence version of Protocol A at scale;
5. completion of the human verification, so that correct structure can be tested.

## Questions a reviewer will ask

- Why should practitioners care about representation effects of ±1 EM point when retrieval differences are an order of magnitude larger?
- Does the abstention effect survive if abstentions are excluded? (The paper reports the decomposition; conditional accuracy is nearly unchanged.)
- Are the CONTRADICTS predictions an artefact of the xsmall NLI model? Would a stronger relation classifier avoid them?
- How were the six contrasts chosen? (They are fixed in the pilot protocol before any generation, and the paper says so.)
