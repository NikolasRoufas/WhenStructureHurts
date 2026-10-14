# Final research assessment (revision-2, 2026-10-14)

**Verdict: FINDINGS_COMPETITIVE_BUT_MAIN_UNCERTAIN**

The central result now rests on a confirmatory test:
- its protocol was frozen and published before sampling;
- it ran on 6,400 untouched questions;
- it was confirmed on both datasets, including one that played no role in forming the hypothesis.

Intervention controls locate the effect precisely, and a second model family reproduces it. Main-track acceptance remains uncertain, because:
- the structures tested are narrow (annotation-derived dependencies; a small NLI relation predictor);
- both readers are 7B models;
- no relation is human-verified, so the "false" in "false contradiction" rests on automatic triage.

This is a qualitative judgement, not a prediction of acceptance.

Evidence trail: `paper/CLAIMS_EVIDENCE_AUDIT.md`, `docs/REPRODUCIBILITY_CHECKLIST.md`, `docs/REVISION_EXPERIMENT_LOG.md`, `docs/STATISTICAL_VALIDITY_REVIEW.md`, `docs/FALSE_CONTRADICTION_ANALYSIS.md`, `docs/RETRIEVAL_EVIDENCE_STUDY.md`, `docs/ACL_NOVELTY_AUDIT.md`, `docs/ACL_REVISION_AUDIT.md`, `paper/INTERNAL_REVIEW_REPORT.md`.

---

**1. Did we eliminate the major methodological confounds?**

Largely, for the relation question.
- R4P−R4 changed order, line count and labels together. The fixed-order controls change one factor at a time on identical facts:
  - removal of contradiction lines;
  - relabelling only the contradiction lines (same pairs, positions, count, other labels);
  - a filler of the same count and nearly the same length (7 vs 8–9 tokens);
  - all-neutral labels;
  - order only.
- Two small asymmetries remain in the code: the 40-line cap (19 questions) and duplicate merging under neutral relabelling (442 questions). They are quantified, and sensitivity analyses leave the estimates unchanged.
- Remaining confounds:
  - the relation *predictor* is fixed, so we cannot separate "a CONTRADICTS line" from "a CONTRADICTS line produced by this NLI model on these pairs";
  - derived structure is unverified.

**2. Are false contradiction relationships causally associated with reduced accuracy under controlled interventions?**

*Displayed* predicted contradictions causally reduce accuracy: interventions on identical facts and order, confirmed prospectively.
- On `confirm_v1`, among questions with at least one contradiction line, showing them costs 5.3 points (2Wiki) and 5.6 points (MuSiQue).
- Confirmatory test 2, on untouched questions: 2Wiki −7.7 points [−9.5, −6.1] and HotpotQA −5.3 points [−6.7, −3.9], p_Holm < 0.001 for both.

That the harmful lines are *false* is supported only by automatic triage: 40 % concern different entities and 20 % different dates. Human labels are pending. So the causal claim is about *asserting* a contradiction. Whether falsity is required is not established.

**3. Does removing harmful relation information restore correct answers?**

Yes.
- Removing or relabelling the contradiction lines recovers 3.3–4.2 points (all questions) on both datasets.
- Relabelling restored 141 correct 2Wiki answers (80 from abstentions, 61 from wrong answers) and lost 21. On MuSiQue it restored 62 and lost 4.
- Relabelling the remaining (non-contradiction) labels adds nothing.

**4. Do the findings replicate with a second model?**

Partly, and informatively. Mistral-7B-Instruct-v0.3 was run on the same 4,976 questions.

| finding | Qwen2.5-7B (EM) | Mistral-7B (EM) | Mistral (lenient) | replicates? |
|---|---|---|---|---|
| contradiction lines on − off | −3.3 / −3.3 | −3.4 [−4.3, −2.5] / −1.5 [−2.3, −0.7] | −5.0 / −3.3 | yes, with 5–6 points more abstention |
| predicted − derived lines (fixed order) | −3.6 / −5.5 | −4.1 / −2.5 | — | yes |
| derived order and derived relation lines | null | null | — | yes (null both) |
| sentence items (R1−R0) | −1.7 (2Wiki, confirmed) / −0.1 | −0.1 / **+2.2** [+1.2, +3.3] | — | **no**: reader-specific |

Pairs are 2Wiki / MuSiQue. Two readers do not establish model-family generality.

**5. Does the effect hold with realistically retrieved evidence?**

Yes, exploratory. On 1,000 fresh questions where every format renders the same four reranked passages:
- predicted relations cost 3.6 / 3.0 points;
- contradiction lines cost 2.2 / 2.4 points;
- the cost is largest when retrieval returned all supporting sentences (R4P−R4: −9.4 / −4.2) and zero when it returned none.

Correct (derived) structure on incomplete evidence could not be tested, because annotation edges rarely survive top-4 retrieval.

**6. Are the results statistically credible?**

Yes, for the claims made.
- **Confirmatory 1:** six pre-specified tests with Holm and equivalence (Holm-TOST agrees). It was reproduced byte-identically by an independent re-execution.
- **Confirmatory 2:** frozen, published before sampling, Holm over two datasets.
  - Realised power for half the exploratory effect was about 0.75–0.88, and the observed effects are 2–3 times larger.
  - A cluster bootstrap by source title leaves the intervals unchanged.
- **Exploratory analyses** are labelled, uncorrected, and never pooled with confirmatory ones. Only patterns that recur across datasets and readers are emphasised.

**7. Is the contribution novel relative to the closest GraphRAG papers?**

Moderately, and in a well-defined way (`docs/ACL_NOVELTY_AUDIT.md`).
- Nishida et al. (TACL 2026) show that noisy triples hurt GraphRAG *through retrieval*. Their study uses one answering model (GPT-4o), point estimates and no presentation-only controls.
- GraphRAG-Bench, Han et al. and Zhou et al. compare whole systems.
- We isolate presentation with content verified identical, show that one asserted label carries the cost, separate abstention from wrong answers, and confirm prospectively.
- We do not claim to be first to show that structure can hurt, or that noisy relations hurt.

**8. What are the strongest remaining rejection risks?**

1. "Unsurprising": telling a model that sources conflict makes it cautious.
2. Narrow structures: annotation-derived dependencies and a small NLI predictor, not deployed LLM-extracted graphs.
3. Two 7B readers only.
4. "False contradiction" not human-verified.
5. Gold evidence for all confirmatory results.
6. The sentence-item result does not generalise across readers, which a reviewer may read as weakening the first confirmatory test.

**9. Which studies or human annotations remain incomplete?**

- Human labels: package v2 (300 pairs, two independent annotators, sentence-only and with-context labels) and the 50-question structure-verification package.
- The verified-false-only removal intervention (C4); component attribution (Exp3).
- LLM-extracted relations as the predictor; a larger third reader (not authorised; about 4.4 GPU-hours remain).
- Protocol B, Exp0 and Exp2 at scale (pilot only).
- Matched-budget B2–B4 (not run; the matched comparison is the retrieved-evidence study).
- Authorship, the AI-use disclosure text, licence verification and the Responsible NLP checklist (`docs/ACL_2027_SUBMISSION_CHECKLIST.md`).

**10. Is the paper scientifically ready for internal submission review?**

Yes.
- The manuscript compiles cleanly (22 pages; the main text ends on page 8; no overfull boxes or undefined references), and every page was inspected.
- Every number is traced to a run with prediction hashes.
- Exploratory and confirmatory evidence are separated throughout.

It is not yet ready for external submission. The authors must:
- fill in authorship;
- verify licences and complete the AI-assistance disclosure;
- decide whether to collect the human labels before the 4 January 2027 ARR deadline. Those labels are the single highest-value addition.
