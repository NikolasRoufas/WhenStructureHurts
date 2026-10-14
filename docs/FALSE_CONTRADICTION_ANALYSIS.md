# False-contradiction analysis (revision-2, 2026-10-14)

**Question.** The NLI relation predictor marks gold supporting sentences as contradicting each other. How often does this happen, and does *showing* such a line reduce accuracy?

**Status of each claim below:**
- **causal**: an intervention on identical facts and order;
- **confirmatory**: frozen protocol, untouched questions;
- **correlational**: grouping by observed properties;
- **automatic**: heuristic, not human-verified.

No human labels exist yet. The phrase "false contradiction" is used only for pairs **automatically identified** as likely compatible.

## 1. Prevalence (automatic)

Source: `research_outputs/revision/contradictions/contradictions_summary.json`, R4P on `confirm_v1`.
- **Volume:** 12,816 directed CONTRADICTS edges (9,750 unordered pairs) in 3,044 of 4,976 questions. 12,372 edges were rendered; the rest were cut by the 40-line cap.
- **Share of prompts:** at least one rendered contradiction line in 63 % of 2Wiki and 58 % of MuSiQue prompts. On the untouched confirmatory-2 sample: 57 % of 2Wiki and 34 % of HotpotQA prompts.
- **NLI confidence:** every edge ≥ 0.90 by construction; median 0.985.
- **Gold evidence for one answer is consistent by construction, so we expect few genuine contradictions.**

Automatic triage of the 9,750 pairs:

| triage category | share |
|---|---|
| different source titles (different entities) | 40 % |
| same title, different years | 20 % |
| same title, different numbers | 7 % |
| same title, pronoun-initial sentence | 8 % |
| same title, other | 26 % |

## 2. Does showing the lines cause the loss? (causal, exploratory; `confirm_v1`, fixed order)

Every row compares the same facts in the same (R5) order. Source: `research_outputs/revision2/r2/controls2.csv`.

| intervention (vs R4P_FO, which shows all predicted lines) | 2Wiki ΔEM [95 % CI] | MuSiQue ΔEM [95 % CI] | tokens removed | what stays fixed |
|---|---|---|---|---|
| remove contradiction lines (R4P_FO_NC) | +0.033 [+0.025, +0.042] | +0.033 [+0.024, +0.042] | 30 / 15 | everything but those lines |
| relabel only CONTRADICTS → RELATED_TO (R4P_FO_CN) | +0.037 [+0.029, +0.045] | +0.033 [+0.025, +0.042] | 6 / 3 | pairs, line count, positions, other labels |
| replace each contradiction line by a neutral filler line (R4P_FO_NCPAD) | +0.042 [+0.034, +0.050] | +0.037 [+0.028, +0.047] | 9 / 4 | line count, positions, ≈ length |
| relabel *all* predicted labels to neutral (R4N_FO, revision-1) | +0.037 | +0.030 | — | pairs (1–3 fewer lines in 9 % of questions) |

In questions whose block contains no contradiction line, the prompts of these conditions are byte-identical, so the effect is 0 there (built-in placebo). Among questions with at least one line, the effect is −0.053 to −0.067 (2Wiki) and −0.056 to −0.064 (MuSiQue).

**What this identifies.**
- On identical facts and order, the word CONTRADICTS asserted between two items causes the loss.
- Relabelling only those lines recovers as much as removing them, as does a filler of the same line count and near-equal length. Relabelling the other predicted labels adds nothing (R4N_FO vs R4P_FO_CN: 0.000 / +0.003).
- So neither the extra tokens, nor the number of relation lines, nor the other relation types explain the harm.

**Restoration.**
- Among questions with at least one line, relabelling turned 80 abstentions and 61 wrong answers back into correct answers (2Wiki; MuSiQue 49 and 13). It moved only 21 (2Wiki) and 4 (MuSiQue) correct answers the other way.
- Read in the "lines on" direction, these are 80 C→A and 61 C→W transitions, against 1 A→C and 20 W→C.
- Accuracy among questions answered under both conditions is also lower with the lines (−0.035 / −0.028). Abstention is the main channel, but not the only one.

## 3. Confirmation on untouched questions (confirmatory; `CONFIRMATORY_PROTOCOL_2.md`)

| | 2Wiki (n = 1,490 with lines) | HotpotQA (n = 1,295 with lines) |
|---|---|---|
| ΔEM (lines on − off) | −0.077 [−0.095, −0.061], p_Holm < 0.001 | −0.053 [−0.067, −0.039], p_Holm < 0.001 |
| ΔAbstention | +0.089 [+0.072, +0.104] | +0.076 [+0.061, +0.092] |
| transitions off→on: C→A / C→W / A→C / W→C | 67 / 73 / 4 / 21 | 46 / 37 / 1 / 13 |

HotpotQA had no role in generating the hypothesis.

## 4. Second reader (exploratory)

Mistral-7B-Instruct-v0.3 on `confirm_v1`, same prompt:
- **Contradiction lines on − off:** −0.034 [−0.043, −0.025] (2Wiki) and −0.015 [−0.023, −0.007] (MuSiQue); abstention +5 to +6 points.
- **Among questions with lines:** −0.054 and −0.026.
- **Lenient match:** −0.050 and −0.033, so the loss is not an artefact of Mistral's verbose answers.

## 5. Which mechanism? (correlational and automatic)

The brief lists eight candidate sources. Each is assessed below with the evidence we have.

| candidate source | evidence | status |
|---|---|---|
| 1. Incorrect NLI classification | gold evidence for one answer is consistent; 40 % of pairs concern different titles; the effect appears at every confidence level (2Wiki: max confidence < 0.99, −0.063; ≥ 0.99, −0.047) | likely the dominant source; awaits human labels |
| 2. Missing context | the v2 package asks for a sentence-only label and then a label with the full passages, which separates this cause | pending human labels |
| 3. Temporal compatibility | "same title, different years" is 20 % of pairs (e.g. teaser vs trailer release dates); its effect is −0.023 (2Wiki) and −0.119 (MuSiQue) | plausible; correlational |
| 4. Coreference | pronoun-initial pairs are 8 %; their effect is small and imprecise (−0.009 / −0.034, CIs include 0) | weak evidence |
| 5. Entity confusion | "different source titles" pairs carry the largest share and a clear effect (−0.068 / −0.046) | plausible; correlational |
| 6. Dependency direction | not applicable: CONTRADICTS is symmetric in our renderer | — |
| 7. Relation density | the effect does not grow with line count (2Wiki 1–2 lines −0.069, 3–5 −0.050, 6+ −0.020); the filler control rules out a line-count effect | ruled out as the main cause (causal for count) |
| 8. Serialisation artefacts | the targeted relabel changes only the label word; the filler keeps the format | ruled out (causal) |

Source for the groupings: `research_outputs/revision2/false_contra/contradiction_mechanism_correlational.csv`. These groups are observed, overlapping and uncorrected; they suggest, but do not establish, which kinds of false contradiction matter most.

## 6. Human verification (prepared, not done)

Package `research_outputs/revision2/false_contra/human_package_v2/`:
- **Size and strata:** 300 predicted pairs, 30 per stratum per dataset, five strata:
  - pairs whose removal restored the correct answer;
  - other abstentions;
  - high NLI confidence (≥ 0.9935);
  - low NLI confidence (≤ 0.958);
  - no-failure controls.
- **Blinding:** two independent annotator files, in different orders. Annotators never see the question, the outcome, the NLI score or the stratum. The key stays on the server.
- **Labels:** a sentence-only label, then a with-context label (seven categories).
- **Importer:** `scripts/revision/false_contradictions.py import` validates both files, refuses unnamed or identical annotators, and reports raw agreement and Cohen's κ (7-way and genuine-vs-not) by stratum.
- **Estimated effort:** 3–4 hours per annotator.

**Once the labels exist they will tell us:**
1. the share of predicted contradictions that are genuine;
2. whether restored-answer pairs are more often false than no-failure pairs (correlational);
3. how much context resolves.

**An intervention that removes only human-verified false contradictions** (control C4) would then test whether *falsity* matters, as opposed to the mere assertion of conflict. It is not run, because it needs the labels.

## 7. Summary

| claim | status |
|---|---|
| Showing NLI-predicted contradiction lines next to fixed, gold evidence lowers exact match | **confirmatory** (2Wiki, HotpotQA) and replicated with a second reader (exploratory) |
| The label, not the line count, length, order or other labels, carries the effect | **causal**, exploratory |
| The loss runs mainly through abstention, partly through wrong answers | causal decomposition, exploratory; confirmed on fresh data |
| Most predicted contradictions between gold sentences are false | **automatic** triage only |
| The harm requires the contradictions to be false | **not established** (needs human labels + C4) |
