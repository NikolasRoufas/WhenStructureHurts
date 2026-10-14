# Internal review report (revision-2, 2026-10-14)

Three simulated, deliberately critical ACL/ARR reviewers read `paper/main.pdf` (8 pages + appendix). Recommendations use the ARR overall scale (1–5); they are our honest guesses, not predictions of acceptance. After the reports we list what we fixed with the available artefacts and what remains open.

---

## Reviewer 1: experimental validity

**Strengths.**
- Facts are held identical per question with verified digests, and byte-identical prompts are counted.
- The interventions are clean. R4P_FO_CN changes one word per affected line. The filler control keeps line count and nearly the token length. Blocks without contradiction lines give exact zeros (a built-in placebo).
- The central exploratory finding was turned into a **pre-specified confirmatory test** on untouched questions, frozen and published before sampling. It confirmed on 2Wiki and on HotpotQA, a dataset not used to form the hypothesis.
- There is a leakage guard on every prompt, deterministic decoding, and prediction hashes with a claims audit.

**Weaknesses.**
1. *Population of the confirmatory test.* The primary population (questions with at least one contradiction line) is defined by an input property and is identical across conditions. It is not representative of all questions, though: over all questions the effect is −4.4 / −1.8 points. The paper reports both.
2. *Controls reuse inspected questions.* Every intervention except the confirmatory one runs on `confirm_v1`, whose R4P−R4 result motivated it. That is acknowledged, but the label-vs-filler distinction itself is exploratory.
3. *Small implementation asymmetries.* Removing lines can admit lines cut by the 40-line cap (19 questions), and relabelling merges duplicates (442 questions). Sensitivity analyses leave the estimates unchanged, but these should be fixed in code for a release.
4. *Exact match for a verbose reader.* Mistral's EM is low on MuSiQue (0.09). The lenient metric was fixed before its run, which helps, but EM comparisons across readers are not meaningful. The paper compares within-reader contrasts only.

**Questions.** Does the effect survive a different relation predictor (an LLM extractor) that produces fewer spurious contradictions? Does a format that shows contradiction lines with an explicit hedge ("possible conflict") behave differently?

**Reproducibility.** Strong: frozen sets, configs, commits, hashes, and analysis scripts that read only predictions. Raw predictions are not public (size); the authors should deposit them.

**Recommendation: 3.5 (Findings-level, borderline main).** *What would change it:* confirming that the harm depends on falsity (human labels plus the verified-false-only intervention), and a relation predictor that practitioners use.

## Reviewer 2: novelty and contribution

**Strengths.**
- The paper isolates presentation from retrieval. That is a different question from Nishida et al. (TACL 2026), who show noisy triples hurt GraphRAG through retrieval and clustering.
- The "label, not line" result is specific and actionable: relation extractors should not assert contradictions between consistent evidence, or readers should be told not to trust them.
- Reporting transitions (abstain vs wrong) is a useful methodological point for the GraphRAG evaluation literature.

**Weaknesses.**
1. *Expected?* Telling a model that two sources contradict each other and observing more abstention may strike reviewers as unsurprising. The contribution is the measurement under strict control, its size, and the fact that half the loss becomes wrong answers on fresh data. It is not a surprising mechanism.
2. *Narrow structure.* Structure here is (a) annotation-derived dependencies and (b) a small NLI cross-encoder plus a title heuristic. Modern GraphRAG uses LLM triple extraction, community summaries and paths. The null for derived structure may not transfer to the structures people actually deploy.
3. *Sentence units.* The title suggests "transformations" broadly. The experiments segment dataset sentences and do not test LLM proposition extraction except in a pilot with unequal budgets.

**Questions.** Would contradiction lines extracted by GPT-class models occur at the same rate? Is there any condition in which structure *helped*?

**Recommendation: 3 (Findings).** *What would change it:* one deployed-style pipeline (e.g. LLM-extracted triples), showing the same label effect at realistic contradiction rates; and a positive case where correct structure helps on incomplete evidence.

## Reviewer 3: generalisation and evaluation

**Strengths.**
- There are two confirmatory samples, including a dataset outside the hypothesis-generating set.
- A second reader from another family (Mistral-7B) replicates the contradiction cost and *fails* to replicate the sentence-item cost. The paper reports this honestly as reader dependence.
- Retrieved-evidence and abstention-policy checks bound the scope.

**Weaknesses.**
1. Both readers are 7B instruction-tuned models; there is no larger or reasoning-tuned model. Abstention behaviour is known to vary strongly with scale and alignment.
2. Gold evidence everywhere except one 1,000-question exploratory sample. Correct structure on incomplete evidence is untested because derived edges do not survive retrieval.
3. No human verification of any relation. "False contradiction" is an inference from automatic triage. The 300-pair package is prepared but unlabelled.
4. The abstention policy is a single prompt family with one stricter variant.

**Questions.** Does a 70B model, or a model trained to reason, ignore spurious contradiction lines? What happens when the contradiction is genuine?

**Recommendation: 3 (Findings; main-track uncertain).** *What would change it:* a third, larger reader, plus human labels for the contradiction package.

---

## Meta-assessment

All three reviewers accept the soundness of the confirmatory result. The decisive concerns are external validity (7B readers, NLI-predicted relations, gold evidence) and the unverified falsity of the contradictions. Likely outcome: **Findings**, with main-track acceptance possible if a reviewer values the methodology.

## Objections addressed with available artefacts and authorised compute (this revision)

| objection | action |
|---|---|
| R4P confounds order, line count and labels | fixed-order controls plus targeted relabel and length-matched filler (Table 3) |
| Post-hoc mechanism on inspected questions | confirmatory protocol 2 on 6,400 untouched questions, frozen and published first (Table 4) |
| Single reader | Mistral-7B second reader (Table 14); reader dependence of segmentation reported |
| Effects may be prompt artefacts | three abstention policies (Table 15); the contradiction cost persists under stricter guidance; the direct-answer policy raises wrong answers by 12–19 points |
| Implementation asymmetries | quantified; sensitivity analyses (`docs/ACL_REVISION_AUDIT.md` §4) |
| Fallback anchors | anchor-stratified contrasts (Table 18): null in both strata |
| Serialisation overhead | full accounting (Table 17); equal-token retrieved-evidence analysis |
| Clustered questions | cluster bootstrap by source title: intervals unchanged |
| Novelty vs Nishida et al. | `docs/ACL_NOVELTY_AUDIT.md`; claims narrowed accordingly |

## Not resolvable now

1. **Human labels** for the 300-pair package. These need two annotators, about 3–4 hours each; the importer validates them and computes κ.
2. **A larger or third reader.** Not authorised; about 4.4 GPU-hours remain, which is not enough for a 70B model on one 32 GB GPU.
3. **LLM-extracted relations.** A new experiment and protocol.
4. **The intervention removing only verified-false contradictions (C4).** It requires item 1.
