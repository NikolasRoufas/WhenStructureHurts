# Retrieval generalisation report (revision-1, exploratory)

**Design** (`docs/REVISION_PROTOCOL.md` §2, committed `34356e5` before the sample was drawn).
- **Sample:** a fresh sample, `retr_v1.json` (seed 3, sha256 `8c32d7ed…`): 500 MuSiQue and 500 2WikiMultiHopQA questions, disjoint from smoke, pilot and confirmatory questions (checked by uid).
- **Retrieval:** a shared, gold-free stage. BM25 ranks each question's own passage pool, a cross-encoder reranks the top 10, and the top 4 are kept. The four passages are fixed per question before any representation is built.
- **Representations:** each one renders exactly the sentences of those passages (Protocol A identity verified per question).
  - R4/R5 use annotation-derived edges restricted to retrieved sentence pairs: oracle *structure* on real retrieval, with annotations never used for selection.
  - R4P, R4P_NC and R4P_FO use predicted relations.
- **Protocols:** A (natural length) and B (budget = 1.0× content tokens, per-representation policy, gold-free BM25 fact ranking).

**Run.** `results/revision/exp1/20261012-210958_37616258`, config `configs/revision_retrieval.yaml`, commit `8423203`.
- 14,000 records: 0 errors, 0 unavailable, 1.0 GPU-hour.
- Outputs: `research_outputs/revision/retrieval/` (`scripts/revision/retrieval_analysis.py`).

**Status.** The contrasts were specified before this sample existed, so in that sense this is a prospective test. It was not part of a confirmatory family, there is no multiplicity correction, and n = 500 per dataset. We report it as an exploratory replication on fresh questions.

## 1. Retrieval outcome (gold labels used only to stratify)

| | complete (all supporting sentences retrieved) | partial | none |
|---|---|---|---|
| MuSiQue (500) | 149 | 311 | 40 |
| 2Wiki (500) | 262 | 238 | 0 |

- Support coverage of the four retrieved passages: MuSiQue 0.61, 2Wiki 0.78.
- Answer string present in the evidence: 0.44 and 0.65.
- **Sample limitation:** the remaining MuSiQue pool is almost all 2-hop (459 of 500; 41 3-hop, no 4-hop), because earlier samples used up the longer questions.

## 2. Contrasts (Protocol A; paired ΔEM, 95 % bootstrap CI, n = 500)

| contrast | MuSiQue ΔEM | ΔAbst | identical prompts | 2Wiki ΔEM | ΔAbst | identical |
|---|---|---|---|---|---|---|
| R1−R0 (sentence items vs passages) | +0.014 [0.000, +0.028] | −0.006 | 0 | −0.026 [−0.054, +0.002] | +0.072 | 5 |
| R5−R1 (derived order) | +0.010 [0.000, +0.020] | −0.008 | 451 | 0.000 | 0.000 | 498 |
| R4−R5 (derived relation lines) | +0.002 [−0.012, +0.016] | −0.002 | 342 | +0.010 [−0.008, +0.028] | −0.006 | 322 |
| R4P−R4 (predicted vs derived) | **−0.036 [−0.056, −0.020]** | +0.068 | 72 | **−0.030 [−0.054, −0.008]** | +0.066 | 84 |
| R4P−R4P_NC (contradiction lines on vs off) | **−0.022 [−0.038, −0.008]** | +0.040 | 131 | **−0.024 [−0.046, −0.004]** | +0.068 | 110 |
| R4P_FO−R5 (predicted lines at the derived order) | −0.022 [−0.038, −0.008] | +0.052 | 86 | −0.016 [−0.042, +0.010] | +0.052 | 66 |

**By retrieval outcome:**
- R4P−R4 when retrieval is complete: MuSiQue −0.094 [−0.148, −0.047], 2Wiki −0.042 [−0.080, −0.008].
- R4P−R4 when it is partial: −0.013 / −0.017.
- R1−R0 on 2Wiki: −0.057 [−0.099, −0.015] when complete, +0.008 when partial.
- When nothing relevant is retrieved (MuSiQue, n = 40) there is no difference: the model fails under every representation.
- In distractor-heavy retrievals (at most 1 of 4 passages relevant) the effects shrink towards zero.

**Reading:**
1. **The predicted-relation harm and the contradiction-line effect replicate on fresh questions with real retrieval.** Their size is similar to the gold-evidence results (−2 to −4 EM points, about +4 to +7 points of abstention).
2. **The effects concentrate where the evidence suffices to answer.** Misleading relation lines matter most when the model would otherwise be able to answer; when evidence is missing, the model fails or abstains anyway.
3. **Derived structure rarely survives retrieval.** An annotation edge needs both endpoint sentences retrieved, so R4 = R5 and R5 = R1 for most questions (2Wiki: 498 of 500 R5 = R1). With top-4 retrieval we therefore cannot test *correct* structure on incomplete evidence at this scale. This is a limitation of the design, not a null result about structure.
4. **R1−R0 on 2Wiki points the same way as the confirmed gold-evidence effect** (−0.026 with +7 points of abstention), but the interval includes zero at n = 500. On MuSiQue it points the other way (+0.014).

## 3. Budget (Protocol B, 1.0× content tokens, per-representation)

| | facts kept R0 / R1 / R4P | answer in evidence R0 / R1 | ΔEM R1−R0 | ΔEM R4P−R4 | ΔEM R4P−R4P_NC |
|---|---|---|---|---|---|
| MuSiQue | 0.840 / 0.683 / 0.645 | 0.414 / 0.394 | +0.022 [+0.002, +0.042] | −0.032 [−0.050, −0.016] | −0.016 [−0.028, −0.006] |
| 2Wiki | 0.821 / 0.666 / 0.628 | 0.588 / 0.520 | +0.010 [−0.016, +0.034] | −0.040 [−0.060, −0.020] | −0.036 [−0.054, −0.018] |

Under a budget, sentence items keep about 15 percentage points fewer facts than passages (as in the gold-evidence pilot). On MuSiQue they still score slightly higher than passages, so evidence lost to formatting overhead does not translate directly into lost accuracy. The predicted-relation harm persists under the budget.

## 4. Exp0 (pilot) budget fairness

`research_outputs/revision/analysis/C_exp0_costs.csv` (from `scripts/revision/exp0_costs.py`).

| system | evidence tokens (MuSiQue / 2Wiki) | units | extraction calls / question | latency / question | note |
|---|---|---|---|---|---|
| B0 (BM25 top-4) | 493 / 506 | 4 | 0 | 0.36–0.38 s | |
| B1 (reranked top-4) | 538 / 501 | 4 | 0 | 0.36–0.39 s | |
| B2 (extracted claims) | 1,390 / 1,436 | about 57 | about 15 | about 24 s | about 3× the tokens of B1 |
| B3 (predicted path) | 1,667 / 1,711 | about 57 | about 15 | about 24 s | |
| B4 (EG-RAG reconstruction) | 442 / 489 | 12 | about 15 | about 24 s | 450-token / 12-claim selection; 55–62 % of its predicted relations are CONTRADICTS; 4.5–5 conflict sets per question |

The system comparison is not budget-matched: B2 and B3 receive about three times the evidence of B0 and B1. We therefore report Exp0 as system-level descriptions with their budgets explicit, and draw no architectural conclusion from it. The budget-matched evidence on retrieved passages is §3 above. B4's large share of contradiction relations is consistent with the mechanism identified in the controlled experiments, but within Exp0 it is an association only.
