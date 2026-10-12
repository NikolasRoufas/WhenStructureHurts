# Revision-1 protocol: exploratory experiments added after the confirmatory result

**Written 2026-10-12, before the retrieval sample (§2) was drawn and before any generation on it.**

Everything in this document is **exploratory**. It was designed after the confirmatory result of `docs/CONFIRMATORY_PROTOCOL.md` was known. No result here is confirmatory, none enters the Holm family, and the paper labels all of it as post hoc. The point of writing it down first is to fix the conditions, samples and analyses before outcomes are seen, not to claim confirmation.

**Compute ceiling:** 24 GPU-hours in total for the campaign. Already used before revision-1: 9.48 GPU-hours (run manifests) or 9.53 (driver wall-clock), plus a preflight of under 0.1. The remaining ceiling is about 14.4 GPU-hours. Generator, revision, bf16, batch size 1 and prompt `qa-v2` are unchanged unless stated.

## 1. Fixed-order relation controls (running since 2026-10-12 20:09 UTC)

- **Config:** `configs/revision_relation_controls.yaml`, stage `revision`, on the already analysed `confirm_v1` questions.
- **Code:** `src/wsh/representations/relation_controls.py`.
- **Conditions:** R5, R4, R4P (cached) and R4P_FO, R4P_FO_NC, R4N_FO, R5P, R4P_NC.
- **Analysis** (`scripts/revision/contradictions.py effects`): paired question-level differences in EM and abstention for each one-factor contrast listed in that script. Each comes with a 95 % bootstrap CI (2,000 resamples, seed 0) and is reported with its number of identical prompts.
- **Strata:**
  - predicted contradiction lines: 0, 1–2, 3–5, 6+;
  - question type;
  - hop count.
- **Model:** for the contradiction-removal contrast, an OLS of the paired difference on the number of contradiction lines, the other line-count difference, and the token difference.
- **Status:** these contrasts were designed after we had seen R4P−R4 on the same questions. They are interventions, so they identify the effect of the manipulated factor on these questions, but they remain exploratory.

## 2. Retrieved-evidence experiment (fresh questions)

- **Sample:** `configs/question_sets/retr_v1.json`, drawn with seed 3 from development questions not in the smoke, pilot or confirmatory sets (`configs/excluded_revision.json`).
  - 500 MuSiQue questions, stratified by hops; only 570 eligible questions remain.
  - 500 2WikiMultiHopQA questions, 125 per type.
  - Same eligibility rules as before.
- **Retrieval (shared, gold-free):** BM25 over each question's own distractor pool, then cross-encoder reranking of the top 10, keeping the top 4 passages. The retrieved passages are fixed per question before any representation is built, and every representation renders exactly their sentences (Protocol A identity is checked per question).
- **Representations:**
  - R0 (passages) and R1 (sentence items);
  - R5 and R4, using annotation-derived edges restricted to retrieved sentence pairs. This is *oracle structure on real retrieval*: the annotations are never used to select evidence;
  - R4P (predicted relations and order), R4P_NC (minus contradiction lines) and R4P_FO (predicted lines at the R5 order).
- **Protocols:**
  - A (natural length);
  - B with budget `content:1.0` and the per-representation policy (the shared, gold-free BM25 fact ranking).
- **Analysis:**
  - The same paired contrasts as the gold experiment (R1−R0, R5−R1, R4−R5, R4P−R4, R4P_NC−R4P, R4P_FO−R5), EM and abstention, with bootstrap CIs.
  - Every contrast is stratified retrospectively by retrieval outcome, using gold labels only for stratification:
    - all gold passages retrieved / some / none;
    - distractor-heavy (at most 1 of 4 retrieved passages is gold);
    - long evidence (above the median of evidence tokens);
    - hop count.
- **Not compared as system effects:** B0–B4 of Experiment 0 differ in evidence budgets. They are re-analysed with their budgets made explicit (tokens, units, extraction calls, latency), and no architectural conclusion is drawn from unequal budgets.
- **Estimated cost:** about 1,000 questions × 7 representations × 2 settings at under 0.5 s per uncached generation plus overhead, i.e. about 2–2.5 GPU-hours.

## 3. Abstention-instruction variant (prompt factor)

- **Sample:** a fixed random subset of 1,000 `confirm_v1` 2Wiki questions (seed 4), already analysed, so exploratory.
- **Conditions:** R0, R1, R4, R4P.
- **Prompt change:** the original `qa-v2` prompt minus its last line, which offers "insufficient evidence". This is a separate factor, never pooled with `qa-v2` results.
- **Analysis:** within-prompt contrasts R1−R0 and R4P−R4, and the prompt × representation interaction, with paired bootstrap CIs.
- **Cost:** about 0.6 GPU-hours.
- Run only if the budget remains after §1 and §2.

## 4. Second reader (pending authorisation)

- No model from a second family is cached on the server.
- Downloading and running one (for example Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3) requires explicit authorisation from the investigator and must fit the remaining ceiling.
- If authorised, it runs the six primary contrasts and the fixed-order relation controls on `confirm_v1`, Protocol A, with prompt `qa-v2`.
- It would be a cross-model replication on the same questions, not an independent replication.

## 5. Not run (and why)

- **An oracle-corrected contradiction condition:** this needs human error labels, which are not available. The blinded package is in `research_outputs/revision/contradictions/human_package_v1/`.
- **LLM-extracted atomic propositions in the information-controlled setting:** paraphrased claims would need semantic-preservation validation that we cannot do at scale within the budget. The paper's claims are narrowed to sentence-item presentation instead.
