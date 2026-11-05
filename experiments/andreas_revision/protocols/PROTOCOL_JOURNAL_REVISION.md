# Journal-revision experiments: pre-specified protocol (frozen 2026-11-05)

**Status: FROZEN before any new generation and before any human label exists.** Written after the stage-0 audit
(`audits/stage0_audit.json`), which reads only existing artifacts; for Experiment B it reads only evidence
fields (contradiction-pair counts), never outcomes. Changes after freezing go to §7 with date and reason;
a change after data collection never alters a primary analysis.

The original confirmatory runs, their outputs and the manuscript are frozen and are not modified.

Common settings: frozen prompt `qa-v2`; greedy decoding; batch size 1; `max_new_tokens` 64; bf16; Protocol A
(identical fact sets, verified per question); relation predictor and thresholds as in the confirmatory runs.
Statistics: paired percentile bootstrap over questions, 2,000 resamples, seed 0, 95 % CI, two-sided bootstrap p
(`wsh.evaluation.statistics.paired_bootstrap`). An outcome state is C (EM = 1), W (answered, EM = 0) or
A (abstained, unparseable, or generation error, as in `scripts/revision/confirm2_analysis.py`). A CI containing 0
is "inconclusive", never "no effect" or "equivalent".

Compute: physical GPU 1 through the shared MPS daemon (the inference GPU); GPU 0 is not used. Each run goes
through `experiments/andreas_revision/scripts/run_gpu1.sh` in tmux with resumable output.

---

## Experiment A: human verification of predicted contradictions

**Material.** The existing package `human_package_v2` (300 pairs; `research_outputs/revision2/false_contra/`,
tag `research-record-revision2`). The stage-0 audit found it valid: hashes match, 0 duplicate pair ids,
0 empty contexts, 0 labels filled in. The sampler reproduces the package exactly from seed 0. It is reused
unchanged, and no new package is drawn.

**Population represented.** Unordered pairs of facts joined by at least one predicted CONTRADICTS line that is
rendered in an R4P_FO prompt of the Qwen fixed-order controls run on `confirm_v1` (MuSiQue + 2Wiki;
`revision/exp1/20261012-200925_a2e6e3a8`). This population has 7,721 pairs in 2,425 questions. The sample is **stratified and enriched**: 5 strata ×
2 datasets × 30 pairs. The strata are restored, abstained_other, high-confidence quartile, low-confidence quartile and
no-failure control, and some of them are defined by downstream outcomes (annotators never see them). MuSiQue is
over-represented (150 of 300 vs 901 of 7,721). 1,181 population pairs (15 %) belong to no stratum, so they have
inclusion probability 0.

**Annotation.** Two independent annotators label all 300 pairs with the package's 7 labels, first from the
sentences only and then with the passages. Guidelines: `annotation/ANNOTATION_GUIDELINES.md` (an addendum to
the package GUIDE, adding examples and an optional error-category tag in `notes`; the CSVs are unchanged). The
**primary label is `label_with_context`**. It maps to the three classes requested:

| 3-class | package labels |
|---|---|
| genuine | `genuine_contradiction` |
| false | `compatible_different_entities`, `compatible_different_times_or_values`, `coreference_or_entity_resolution_error`, `compatible_other` |
| ambiguous | `context_ambiguity`, `uncertain` |

**Agreement** (3-class, with context; the sentence-only labels are reported as secondary):
- raw agreement and Cohen's κ, each with a 95 % CI from a bootstrap over questions;
- the 3×3 confusion matrix (and the 7×7 matrix, descriptive).

Every 3-class disagreement goes to an adjudication package. The adjudicator sees both labels and notes, but no
outcome, stratum or score. The adjudicated label is final; agreed items keep the agreed label.

**Precision** of predicted contradictions = share of pairs that are genuine. It is always reported with its
denominator and three ways of handling ambiguous pairs:
- strict: genuine / all;
- excluding ambiguous: genuine / (genuine + false);
- bounds: [genuine / all, (genuine + ambiguous) / all].

Estimators:
1. the **sample proportion**, which describes the 300 enriched pairs only;
2. **per dataset × stratum** proportions with Wilson intervals;
3. a **design-weighted (Hájek) estimate** for the population. It weights each pair by 1/π̂, where π̂ is the
   pair's inclusion probability: the share of 2,000 simulations of the exact sampler, run with other seeds, that
   select the pair (`audits/package_v2_population_*.csv`, kept on the server until labelling ends). It covers
   only the 85 % of pairs in at least one stratum, which is stated. The CI comes from a bootstrap that resamples
   questions within each dataset.

Error categories (the 7-label categories plus the optional notes tag) are reported with counts and Wilson
intervals, and only described when n < 20. The automatic heuristic category in the key is shown alongside,
labelled as automatic, and is never treated as a human judgement.

**Human-label integrity.** No label is produced by an LLM, a heuristic or the experimenter on behalf of an
annotator. The importer refuses blank, invalid or unsigned labels and identical annotator ids. If labels do not
arrive, Experiment A is reported as *prepared, annotation pending*.

---

## Experiment B: selective removal of human-verified false contradictions

**Population.** `confirm2_v1` questions whose Qwen R4P_FO prompt renders at least one CONTRADICTS line. The
40-line relation cap must not bind, so that removing lines cannot uncover non-target lines. Eligible questions:
2Wiki 1,481 (9 excluded by the cap), with 4,052 pairs; HotpotQA 1,295, with 1,854 pairs.

**Selection** (input-only; fixed now): per dataset, a random permutation of the eligible question uids with
seed 11 (`selective_removal/select_questions.py`), taken in order.
- **Tier 1:** the first 150 questions per dataset (300 questions; about 410 + 215 pairs expected).
- **Tier 2** (if annotator time allows; decided before any label is seen): the next 150 per dataset.
- Every predicted contradiction pair of a selected question is labelled (package v3, same format and guide as
  v2, two annotators plus adjudication). A question enters the analysis only if **all** its pairs have a final
  adjudicated label.
- Incomplete questions are reported, never analysed as cleaned. A question stays in its tier whatever its
  labels turn out to be.

**Conditions** (one new run, Qwen2.5-7B-Instruct at revision `a09a3545`, the confirmatory reader):

| | condition | relation lines |
|---|---|---|
| A | R4P_FO | all predicted lines |
| B | R4P_FO_SC | minus the lines whose pair is adjudicated *false* (genuine and ambiguous lines are kept) |
| C | R4P_FO_NC | minus every CONTRADICTS line |
| D | R4P_FO_SN (sensitivity) | false lines relabelled RELATED_TO (same endpoints, position and count) |

A and C are re-generated in the same run so that all four conditions share hardware and software. Their agreement
with the original confirm2 outputs is reported as a reproducibility check.

**Programmatic checks**, enforced in code and tests (`tests/test_selective_removal.py`; the analysis re-checks each
from the records):
- identical facts, order and question across conditions;
- only target lines differ;
- B = A when no line is false, and B = C when every line is false;
- no unlabelled pair;
- token counts per condition are logged.

**Primary family** (Holm, 3 tests): paired EM differences over Tier 1 questions, pooled over datasets
(bootstrap resampling questions within dataset):
- B − A: does removing only false lines help?
- C − A: the original contrast on this subset;
- C − B: what removing the remaining genuine/ambiguous lines adds.

**Secondary:**
- the same three contrasts per dataset;
- D − A and D − B;
- abstention and wrong-answer rates;
- coverage;
- full 3×3 transition tables for every contrast.

**Descriptive, observational** (label composition is not randomised; only the presentation is):
- questions whose lines are all false, all genuine, mixed, or include an ambiguous line. In all-false questions
  B ≡ C; in all-genuine questions B ≡ A.
- the C − A effect in all-genuine vs all-false questions, reported with n and CIs and no causal reading;
- the share of the C − A effect recovered by B, (B − A)/(C − A), reported only if the C − A CI excludes 0.

**Interpretation rule.** Differences are EM(later) − EM(earlier), so a positive B − A means removing the false
lines raised EM. "Removing false contradictions restores accuracy" may be stated only if B − A > 0 with Holm
p < 0.05. "The degradation is attributable to false contradictions" additionally requires C − B to be
inconclusive and its point estimate smaller than that of B − A. If C − B is also significantly positive, genuine or ambiguous lines contribute too. If B − A is
inconclusive, no causal attribution to false contradictions is made.

**Dependency.** Experiment B cannot run before the package v3 labels are adjudicated. Until then only the code,
the package and the selection are delivered.

---

## Experiment C: replication with a third reader

**Model.** `allenai/OLMo-2-1124-7B-Instruct` at revision `470b1fba1ae01581f270116362ee4aa1b97f4c84`, bf16, with no
quantisation. It is registered in `configs/models.yaml` since revision-1 as a second-reader candidate, is
Apache-2.0 and ungated, and comes from a training lineage different from Qwen and Mistral (AllenAI, open data,
Tülu-3 post-training). Llama-3.1-8B-Instruct and Gemma-3-12B-it were preferred by the supervisor, but both are
gated (HTTP 401 without an accepted licence and token, checked 2026-11-05), and no Hugging Face token exists on the
server. They can be run later with the same config by changing `model_id`, once access is granted.

**Questions.** `confirm2_v1` unchanged: 2,600 2Wiki + 3,800 HotpotQA. This is a **new reader on reused questions**,
not an independent confirmatory sample.

**Conditions.** R4P_FO and R4P_FO_NC, regenerated by the audited pipeline. Relation prediction is deterministic:
the stage-0 audit found the R4P_FO prompts of two independent earlier runs byte-identical for 4,976 of 4,976
questions. The analysis checks that each OLMo `prompt.user` equals the Qwen confirm2 `prompt.user` for the same
question and condition. A mismatch is reported, and the primary analysis is then repeated on the identical subset.

**Context limit.** OLMo-2 has 4,096 positions. `max_input_tokens` = 4,032 (= 4,096 − 64), so that prompt plus
answer fits; the original 4,096 input limit would allow an overflow of the position range. The longest Qwen
prompt in confirm2 is 3,366 tokens. Before the run, every prompt is counted with the OLMo tokenizer; the overflow
count per condition is reported, and any condition-dependent overflow is analysed as a sensitivity.

**Preflight** (smoke config, 20 questions per dataset × 2 conditions, outputs not analysed):
- the model loads with the expected parameter count;
- prompts render through the OLMo chat template;
- answers parse;
- a repeat of the smoke run gives byte-identical outputs.

**Analysis.** First, `scripts/revision/confirm2_analysis.py`, unchanged:
- **primary:** paired EM difference R4P_FO − R4P_FO_NC on affected questions, Holm over the two datasets;
- **secondary:** abstention, and EM over all questions.

Then `model_replication/analysis.py`, for affected and complete populations, per dataset:
- EM and lenient match (as in `r2_analysis.py`);
- coverage, abstention and wrong-answer rate;
- paired differences with CIs;
- the 3×3 transitions, including C→W, C→A, W→C and A→C.

Comparison with the other readers is side by side and never pooled:
- with the Qwen confirm2 result on the same questions, with an exploratory paired interaction
  (OLMo effect − Qwen effect, over the same questions);
- with Mistral, whose run was on `confirm_v1` (different questions); that comparison is qualitative only.

**Decision rule** (as protocol 2):
- confirmed: Holm p < 0.05 with a negative estimate;
- opposite direction: Holm p < 0.05 with a positive estimate;
- otherwise inconclusive.

All outcomes are reported.

---

## Experiment D: retrieved-evidence extension (GO/NO-GO)

The decision is made in `retrieval_extension/GO_NO_GO.md` from the existing retrieval run (`retr_v1`), before any
new retrieval inference.

---

## 7. Changes after freezing

- **2026-11-05, Experiment C: after the preflight, before the full run.**

  *What the preflight showed* (`audits/expC_smoke_check.json`; 40 questions × 2 conditions; mechanics only, no
  contrast between conditions computed):
  - two independent runs are byte-identical (80/80);
  - the user prompts equal those of the Qwen confirm2 run (80/80);
  - there are no errors.

  *The problem.* OLMo-2 often ignores the two-line answer format. It writes full sentences and puts `Evidence:` on
  the answer line, and 11/80 outputs reach the 64-token limit. The frozen parser therefore scores many correct
  answers as EM = 0: pooled over both conditions, EM was 9/80 and the pre-specified lenient match 47/80. EM is
  near its floor for this reader for reasons unrelated to the contradiction lines.

  *Change.*
  - The EM analysis stays exactly as specified (frozen parser, `confirm2_analysis.py` unchanged).
  - **Lenient match** (definition unchanged from `scripts/revision/r2_analysis.py`, pre-specified in revision-2) is
    added as a **second primary family**: paired difference R4P_FO − R4P_FO_NC on affected questions, Holm over
    the two datasets, same decision rule.
  - Both families are reported. If they disagree, the disagreement is reported, and no conclusion is drawn from
    the more favourable one.
  - Answers stopped by the 64-token limit are reported per condition.

  Prompt, parser, token limits and sample are unchanged.
