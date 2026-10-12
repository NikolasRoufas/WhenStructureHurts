# Final research assessment (2026-10-12)

**Verdict: PROMISING_BUT_MORE_EXPERIMENTS_NEEDED**

The confirmatory test of the pre-registered primary contrasts is valid and complete. However:
- the study rests on a single generator and a prompt that permits abstention;
- its most interesting finding (predicted relations hurt through spurious contradictions) is a secondary contrast whose mechanism was analysed after the fact;
- structure is derived, not verified.

The draft is truthful and complete as an internal-review manuscript. It does not yet support an ACL/EMNLP main-track claim.

**Sources:**
- Run directories and provenance: `research_outputs/experiments/runs.json` and `research_outputs/analysis/provenance.json`.
- Claims audit: `paper/CLAIMS_EVIDENCE_AUDIT.md`.
- Compute: `docs/RUN_STATUS.md`.

---

**1. What did we actually discover?**

All findings below are for Qwen2.5-7B-Instruct (bf16, greedy decoding, one prompt), with gold evidence on MuSiQue and 2WikiMultiHopQA.

*Confirmatory* (six pre-registered tests, n = 1,744 / 3,232, Holm over 6):
- Splitting passages into sentence items lowers 2Wiki EM by **0.017** [−0.029, −0.005], p_Holm = 0.018.
- On MuSiQue the same contrast is **−0.001** [−0.014, +0.014], equivalent to zero within ±0.02.
- Graph-derived order (R5−R1) and explicit derived relations (R4−R5) are **not significant** on either dataset. On 2Wiki both are **equivalent to zero within ±0.02**; on MuSiQue they are inconclusive.

*Exploratory, on the confirmatory sample:*
- The 2Wiki R1−R0 effect is almost entirely abstention: the R1 format abstained on 250 questions that R0 answered, against 81 the other way. Accuracy on questions answered under both is unchanged (+0.001).
- Predicted relations (R4P) instead of derived ones lower EM by **0.036** (2Wiki) and **0.045** (MuSiQue), with coverage down 6–9 points. The loss is concentrated in prompts where the NLI predictor writes CONTRADICTS lines between compatible gold facts; such lines appear in 63 % of 2Wiki prompts.

*Exploratory, pilot (n = 100 per dataset):*
- Under a token budget, structured formats keep 15–20 percentage points fewer facts and drop 1.5–3× more answer-bearing facts than passages; the EM differences are inconclusive.
- Hard distractors lower EM in every QA cell.
- Corrupting 40 % of derived relations lowers 2Wiki EM by about 0.10.
- Our EG-RAG reconstruction loses accuracy at its budgeted selection step.

**2. Did explicit graph structure improve reasoning?**

No detectable improvement. With identical facts, derived relation lines changed EM by +0.010 [−0.003, +0.024] (MuSiQue) and +0.006 [−0.002, +0.015] (2Wiki); the 2Wiki result is equivalent to zero within ±0.02. In pilot case studies, relation lines occasionally stopped the model from returning the bridge entity, but these are anecdotes, not an effect. *Predicted* (noisy) relations clearly hurt.

**3. Did ordered claims perform differently from graphs?**

| comparison | MuSiQue | 2Wiki |
|---|---|---|
| graph-derived order vs dataset order (R5−R1) | −0.011 | −0.008 |
| step-grouped vs graph-ordered (R3−R5) | −0.007 | −0.004 |
| graph with relations vs graph order alone (R4−R5) | +0.010 | +0.006 |

None is significant. Shuffling (R2−R1) hurt on 2Wiki (−0.024 [−0.036, −0.012]) but not on MuSiQue (+0.013, inconclusive). Order matters on 2Wiki; *which* principled order is used does not detectably matter.

**4. How much evidence was lost through representation transformations?**

- **Protocol A (information-controlled):** none, by construction and verification. There were 0 information-equivalence violations across 44,784 confirmatory records.
- **Protocol B, 1.0× content-token budget, per-representation policy:**
  - Facts kept: R0 0.83 / 0.81 against R1, R4 and R5 0.62–0.65 (2Wiki / MuSiQue).
  - Answer-bearing facts dropped per question: 0.11 against 0.33–0.34 (2Wiki); 0.19 against 0.28–0.35 (MuSiQue).
  - Answer string present: 0.85 against 0.64–0.66 (2Wiki).
- **0.5× budget:** every representation keeps only 27–39 % of the facts, and EM falls to 0.08–0.19.
- **Retrieved setting:**
  - LLM claim extraction preserved the answer string as often as the passages it came from (0.78 / 0.44).
  - The EG-RAG reconstruction's selection kept it less often (0.56 / 0.31).

**5. Which perturbations caused the largest failures?**

These are exploratory pilot results at rate 0.4, on label-preserving cases.
- **Hard distractors (P4)** are the most consistent: HotpotQA R1 −0.16 [−0.28, −0.04], MuSiQue R1 −0.09 [−0.17, −0.01], and negative in every QA cell.
- **Relation corruption (P2)** on 2Wiki R4: −0.10 [−0.18, −0.01].
- **Removing required facts (P1)** is not label-preserving, so no EM change is computed. It produced the largest behavioural change: abstention 0.43 → 0.72 (MuSiQue) and 0.24 → 0.48 (2Wiki), with answers changed in 37–46 % of questions.
- **Reordering (P3) and title stripping (P5)** were small and of mixed sign.
- **HoVer and FEVER** were nearly insensitive.

**6. Which results were statistically inconclusive?**

- **Confirmatory:** R5−R1 and R4−R5 on MuSiQue (neither significant nor equivalent).
- **Pilot:** every primary pilot contrast; nearly every Protocol B contrast; HotpotQA contrasts; most Exp2 cells; Exp0 B2/B3 vs B1; and 2Wiki B1−B0.
- **Secondary datasets:** HoVer and FEVER cannot discriminate representations at all. Representations are identical (no derived structure) or near ceiling (FEVER 0.96).

**7. What do our results establish beyond existing GraphRAG studies?**

System-level studies (GraphRAG-Bench, RAG vs GraphRAG, the unified graph-RAG framework) compare whole pipelines. We add:
- a fact-identical, pre-registered comparison showing that, for this reader, *derived* structure contributes at most about ±1–2 EM points when the facts are complete;
- the first evidence we know of, though exploratory, that *noisy predicted* relations reduce accuracy through a specific mechanism: spurious contradictions trigger abstention;
- an accounting of serialisation overhead as evidence loss under a budget.

The increment is real but narrow.

**8. Which experiments remain incomplete?**

| item | status |
|---|---|
| Exp3 (component attribution) | not executed: no human-verified annotations. See `research_outputs/reports/EXPERIMENT_3_LIMITATIONS.md` |
| Exp4 (adaptive selector) | not justified: no representation property predicts a consistent gain |
| P7 (temporal conflicts) | no verified data |
| Protocol B, Exp0, Exp2 | only at pilot scale |
| second generator | none |
| human verification of relations | not done |
| clean ablation of predicted contradiction lines | not done |

**9. How strong is the paper for an ACL/EMNLP main conference?**

**Below the main-track bar as is; plausible for Findings or a workshop.** Methodological rigour is a strength, as is the honest null with a confirmed small effect. Against it:
- a single generator;
- effects mediated by an abstention option in the prompt;
- the key mechanism is post hoc and secondary;
- no verified structure;
- gold evidence only at scale.

See `paper/REVIEWER_SELF_CRITIQUE.md`.

**10. What additional work would most improve its scientific contribution?**

In order of value per GPU-hour, given about 14 of the 24 authorised hours remain:
1. **A second generator family** at a similar size (e.g. the registered Qwen3.5-9B, after its loading preflight, or a Llama/Mistral model if authorised), re-running the confirmatory Protocol A on the frozen `confirm_v1` set. Estimated 5–6 GPU-hours per model.
2. **A pre-registered R4P ablation:** predicted relations with the CONTRADICTS lines removed, and predicted relations with the derived order. This isolates misleading relations from order and line count. It reuses the confirmatory questions and costs about 2 GPU-hours.
3. **A no-abstention prompt variant** as a pre-specified sensitivity analysis, to separate representation effects from abstention calibration. About 3 GPU-hours.
4. **Completing the 50-question human verification** (3–5 annotator-hours), then running Exp3 and a verified-structure stratum.
5. **Retrieved-evidence Protocol A at scale:** the same facts drawn from retrieved, partial evidence.

Items 1–3 fit in the remaining authorised compute but change the design. Under the campaign rules they need a new pre-registration, and therefore your approval before they are run.
