# Retrieved-evidence study (revision-2; exploratory)

This report consolidates the matched-retrieval experiment of revision-1 (`docs/RETRIEVAL_GENERALIZATION_REPORT.md`, which has the full design and contrast tables) and adds the cost and retention accounting requested in revision-2. It also audits the fairness of the Experiment-0 system baselines. No new generation was needed for this report.

## 1. Design (recap)

- **Questions:** 500 MuSiQue + 500 2WikiMultiHopQA, drawn fresh (`retr_v1`, seed 3) after the protocol was committed. They are disjoint from every other sample.
- **Retrieval:** frozen per question before any representation is built.
  - BM25 over the question's own passage pool, then cross-encoder reranking of the top 10, keeping the top 4.
  - Gold labels are never used to retrieve or rank. They are used only afterwards, to stratify by retrieval outcome.
- **Representations:** all formats render the **same retrieved passage set**:
  - raw passages (R0) and sentence items (R1);
  - ordered items (R5) and derived relation lines (R4), each with annotation edges restricted to retrieved sentence pairs;
  - predicted relations (R4P), predicted minus contradictions (R4P_NC), and predicted relations at the fixed derived order (R4P_FO).
- **Two analyses:**
  - **equal source content** (Protocol A): every format shows all retrieved sentences;
  - **equal token budget** (Protocol B): 1.0× the content tokens, with a shared gold-free BM25 fact ranking and the per-representation policy.
- **Run:** `revision/exp1/20261012-210958_37616258`, 14,000 records, 0 errors, 1.0 GPU-hour.

## 2. Cost and retention per representation

Source: `research_outputs/revision2/retrieval_costs.csv`.
- **Latency** is per uncached answer generation on GPU 0 at batch size 1. It does not include relation prediction (the NLI cross-encoder) or retrieval, which are shared across formats or computed once per question.
- **Facts kept** is the fraction of retrieved sentences shown. **Support coverage** is the fraction of gold supporting sentences shown.

**2Wiki**

| protocol | rep | EM | F1 | abstained | evidence tokens | input tokens | relation lines | facts kept | support coverage | answer in evidence | latency (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | R0 | 0.264 | 0.307 | 0.444 | 526 | 669 | 0 | 1.00 | 0.781 | 0.646 | 0.38 |
| A | R1 | 0.238 | 0.283 | 0.516 | 681 | 824 | 0 | 1.00 | 0.781 | 0.646 | 0.45 |
| A | R4 | 0.248 | 0.290 | 0.510 | 685 | 828 | 0.36 | 1.00 | 0.781 | 0.646 | 0.45 |
| A | R4P | 0.218 | 0.251 | 0.576 | 749 | 893 | 6.98 | 1.00 | 0.781 | 0.646 | 0.46 |
| A | R4P_NC | 0.242 | 0.281 | 0.508 | 695 | 839 | 1.58 | 1.00 | 0.781 | 0.646 | 0.51 |
| B | R0 | 0.256 | 0.292 | 0.474 | 454 | 597 | 0 | 0.82 | 0.744 | 0.588 | 0.38 |
| B | R1 | 0.266 | 0.293 | 0.504 | 451 | 594 | 0 | 0.67 | 0.696 | 0.520 | 0.43 |
| B | R4P | 0.224 | 0.255 | 0.562 | 447 | 591 | 2.88 | 0.63 | 0.684 | 0.512 | 0.44 |
| B | R4P_NC | 0.260 | 0.288 | 0.518 | 451 | 595 | 0.80 | 0.66 | 0.694 | 0.520 | 0.46 |

**MuSiQue**

| protocol | rep | EM | F1 | abstained | evidence tokens | input tokens | relation lines | facts kept | support coverage | answer in evidence | latency (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | R0 | 0.088 | 0.118 | 0.680 | 526 | 670 | 0 | 1.00 | 0.613 | 0.436 | 0.34 |
| A | R1 | 0.102 | 0.133 | 0.674 | 653 | 797 | 0 | 1.00 | 0.613 | 0.436 | 0.44 |
| A | R4 | 0.114 | 0.144 | 0.664 | 657 | 801 | 0.33 | 1.00 | 0.613 | 0.436 | 0.45 |
| A | R4P | 0.078 | 0.107 | 0.732 | 701 | 846 | 4.94 | 1.00 | 0.613 | 0.436 | 0.44 |
| A | R4P_NC | 0.100 | 0.129 | 0.692 | 665 | 809 | 1.27 | 1.00 | 0.613 | 0.436 | 0.46 |
| B | R0 | 0.098 | 0.130 | 0.672 | 462 | 606 | 0 | 0.84 | 0.613 | 0.414 | 0.34 |
| B | R1 | 0.120 | 0.147 | 0.686 | 457 | 601 | 0 | 0.68 | 0.608 | 0.394 | 0.41 |
| B | R4P | 0.096 | 0.123 | 0.730 | 452 | 597 | 2.30 | 0.65 | 0.606 | 0.386 | 0.41 |
| B | R4P_NC | 0.112 | 0.137 | 0.704 | 455 | 599 | 0.67 | 0.67 | 0.608 | 0.394 | 0.45 |

**Reading.**
- *Equal source content (A).* Item formats cost 25–30 % more evidence tokens than passages (identifiers and repeated titles). Predicted relations add 45–70 tokens more. Generation latency differs by under 0.15 s per question.
- *Equal tokens (B).* Passages keep 82–84 % of the retrieved sentences, against 63–68 % for item formats. On 2Wiki this costs item formats 5 points of support coverage and 7 points of answer-in-evidence.
- *Accuracy does not follow retention one-for-one.* On MuSiQue, R1 under the budget still scores above R0 (+0.022 [+0.002, +0.042]). Predicted relations remain harmful under both protocols.

## 3. Strata (gold labels used only retrospectively)

From `research_outputs/revision/retrieval/retrieval_contrasts.csv`:

| stratum | MuSiQue n | 2Wiki n | R4P−R4 (MuSiQue / 2Wiki) | contradiction lines on − off (MuSiQue / 2Wiki) |
|---|---|---|---|---|
| all supporting sentences retrieved | 149 | 262 | −0.094 / −0.042 | −0.047 / −0.019 |
| some retrieved | 311 | 238 | −0.013 / −0.017 | −0.013 / −0.029 |
| none retrieved | 40 | 0 | 0.000 / — | 0.000 / — |
| distractor-heavy (≤ 1 of 4 passages relevant) | 328 | 119 | see csv | −0.012 / −0.008 |
| long evidence (above-median tokens; the "exceeds context budget" case) | 249 | 250 | see csv | −0.016 / −0.012 |

The harm from displayed contradictions is largest when the retrieved evidence would otherwise suffice. When the evidence is missing, the reader fails under every format.

**Not testable here.** Correct (annotation-derived) structure on incomplete evidence: an annotation edge survives only if both of its sentences are retrieved, so R5 = R1 for 498 of 500 2Wiki questions.

## 4. Fairness of the Experiment-0 baselines (B0–B4)

`research_outputs/revision/analysis/C_exp0_costs.csv` (pilot, n = 100 per dataset).

| system | retrieval | evidence budget | tokens (MuSiQue / 2Wiki) | extraction calls per question |
|---|---|---|---|---|
| B0 | BM25 top-4 | 4 passages | 493 / 506 | 0 |
| B1 | reranked top-4 | 4 passages | 538 / 501 | 0 |
| B2 | B1 + LLM claim extraction | all claims (about 57) | 1,390 / 1,436 | about 15 |
| B3 | B2 + predicted reasoning path | all claims (about 57) | 1,667 / 1,711 | about 15 |
| B4 | our EG-RAG reconstruction | ≤ 12 claims, ≤ 450 tokens | 442 / 489 | about 15 |

These are **system-level** comparisons: retrieval, evidence quantity and representation all change together. The table makes the budgets explicit. We draw no conclusion about graph structure from B0–B4.

**Matched-budget variants of B2–B4 were not run.** They would need new LLM claim extraction for every question (about 24 s each), and §2 already provides the matched comparison that isolates representation: the same retrieved passages, equal content (A) or equal tokens (B). We state this choice in the paper.
