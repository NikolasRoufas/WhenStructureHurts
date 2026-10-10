# Research plan — *When Structure Hurts: Understanding Evidence Loss in Retrieval-Augmented Reasoning*

Target: ACL / EMNLP 2027 main conference. Status: infrastructure built and smoke-tested; **no scientific results yet.**

## Question

How do evidence transformations — raw passages → atomic claims → reasoning paths → evidence graphs — affect retrieval-augmented reasoning, and when do they introduce errors that outweigh their benefits?

## Motivation (from the predecessor paper, EG-RAG)

The EG-RAG evaluation (25 examples/benchmark, Qwen2.5-3B/7B, Qwen3.5-9B) found 53.3% example-run failures, that full EG-RAG did not beat a flat claim-only baseline in the only adequately sized paired comparisons, and that much of the failure came from evaluation and engineering defects (citation-ID copying, truncation, FEVER label mismatch, duplicate claim IDs). These observations **motivate** the questions below. They are not evidence that graphs hurt in general: the sample was tiny, the confounds were large, and the comparison was system-level rather than controlled.

## Hypotheses (all falsifiable)

| | Hypothesis | Falsified if |
|---|---|---|
| H1 | Representation of identical evidence measurably changes correctness/grounding | The planned primary contrasts (Exp1, gold evidence, Protocol A: R1−R0, R5−R1, R4−R5 on MuSiQue and 2Wiki; docs/PILOT_PROTOCOL.md) have CIs within a pre-registered equivalence margin (±0.02 EM) at adequate n; a CI containing 0 alone is *inconclusive*, not support for H0. (Wording of the criterion updated 2026-10-10, before any pilot run: F1→EM, budget modes→Protocol A.) |
| H2 | Errors in extraction, relations, or selection propagate to answers | Exp3: replacing a verified component with a predicted one does not lower F1 relative to the oracle, *or* degradations are not associated with measured evidence loss |
| H3 | Structured representations are more sensitive to specific evidence errors than flat ones | Exp2: perturbation × representation interaction (Δ sensitivity R4 vs R0/R1) is not different from 0 for any pre-specified perturbation |
| H4 | Query/evidence-dependent representation choice beats any fixed choice | Exp4 (only if H1–H3 give a reproducible effect): a deployable selector does not beat the best fixed policy on held-out questions, after counting feature cost |

## Expected diagnostic outcomes and what each would mean

- **Representation effect without perturbation (H1 true), but no extra sensitivity (H3 false):** structure acts as a *format* effect; the paper becomes a format-sensitivity study with R5/R3 controls isolating edge labels and step markers.
- **No H1 effect, strong H2 effect:** "structure hurts" through *construction errors*, not through presentation. This is the most likely publishable outcome given the predecessor's results, and Exp3's attribution table becomes the central figure.
- **H3 true:** structured inputs amplify specific errors (e.g. wrong edges, P2; removed claims, P1). This motivates evidence-preserving adaptive selection (H4).
- **Everything null at adequate n with strong generators:** report it. Combined with the predecessor's findings, a well-powered null is still informative about the cost of graph machinery.

## Phasing

1. **Done:** Experiments 0–3 implemented; Exp4 scaffolded; 78 unit tests; bounded real-model smoke test (0.5B), validated and audited (EXPERIMENT_LOG.md).
2. **Pilot (compute environment):** `configs/pilot.yaml` (~700 questions). Goals: debug at scale, measure variance, estimate effect sizes, and choose n for the confirmatory study by power analysis. Pilot results are exploratory and will not be reported as confirmatory.
3. **Freeze:** primary metric, contrasts, equivalence margins, n, and models, written into `EXPERIMENT_SPEC.md §Preregistration` and committed *before* the full run.
4. **Full / confirmatory:** `configs/full.yaml` with a fresh sample seed, ≥2 generator families/sizes (e.g. Qwen2.5-7B and another family), only after explicit authorisation.
5. **Exp4:** only if step 4 shows a reproducible effect.

## Main risks

- **Small-model floor:** the 0.5B model is near floor on multi-hop QA, so smoke numbers carry no information. Representation effects may only appear with capable generators.
- **"Verified" annotations are dataset-derived, not human-verified.** Exp3's oracle quality depends on rules R-MSQ/R-2WK/R-HPQ/R-ANCHOR. A human audit of a sample of derived edges is needed (see COMPUTE_HANDOFF).
- **Relation types other than DEPENDS_ON have no gold annotations,** so SUPPORTS/CONTRADICTS prediction quality cannot be measured directly.
- **Prior art (StructRAG, Han et al. 2025, TCR-QF):** see NOVELTY_AND_BASELINES.md.
