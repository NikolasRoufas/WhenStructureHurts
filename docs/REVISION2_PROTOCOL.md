# Revision-2 protocol: exploratory runs (written 2026-10-13, before any of them was run)

Everything here is **exploratory**: designed after the confirmatory and revision-1 results were known. The genuinely confirmatory test of revision-2 is separate (`docs/CONFIRMATORY_PROTOCOL_2.md`). Compute: 11.99 of the 24 authorised GPU-hours were used before revision-2.

## 1. Targeted and length-matched relation controls (`configs/revision2_controls.yaml`)

Same questions (`confirm_v1`) and facts as the revision-1 controls. The order is fixed (R5 order) in every condition.

| condition | relation block | contrast with R4P_FO isolates |
|---|---|---|
| R4P_FO | all predicted lines | — |
| R4P_FO_NC | predicted lines minus CONTRADICTS (revision-1) | the contradiction lines, but also their tokens and line count |
| **R4P_FO_CN** (new, A4) | the same lines, pairs and positions; only CONTRADICTS relabelled `RELATED_TO` | the contradiction *label* alone (same pairs, count, positions; about 2 tokens per line less) |
| **R4P_FO_NCPAD** (new, A5) | each CONTRADICTS line replaced in place by the non-relational line `(this line is intentionally left blank)` (7 Qwen tokens vs 8–9 for a contradiction line) | contradiction content at the same line count and nearly the same length; residual token difference reported per question |

The "error" status of the relabelled lines is not known: the intervention targets *every* predicted contradiction line, not only those **automatically identified** as likely false, and no line is human-verified. Analysis: `scripts/revision/contradictions.py effects` and `transitions.py` (EM, F1, abstention, wrong-answer rate, transitions, token counts), paired bootstrap 95 % CIs, no multiplicity correction (exploratory).

## 2. Stricter abstention guidance (`configs/revision2_conservative.yaml`)

The same 1,000 `confirm_v1` 2Wiki questions and representations (R0, R1, R4, R4P) as `rev-noabst-v1`. The last line of `qa-v2` is replaced by: *If the evidence does not fully establish the answer, reply "Answer: insufficient evidence". Do not guess.* One variant, written once, never tuned. Three-way comparison: qa-v2 (confirmatory records), qa-v2-noabst (revision-1), qa-v2-conservative. Reported: EM, wrong-answer rate, coverage, within-prompt contrasts, and the prompt × representation interaction. The wrong-answer rate under qa-v2-noabst is the measure of the hallucination risk of the direct-answer policy.

## 3. Second reader (`configs/revision_second_reader.yaml`; authorised 2026-10-13)

- **Model:** `mistralai/Mistral-7B-Instruct-v0.3`, revision `c170c708c41dac9275d15a8fff4eca08d52bab71`, Apache-2.0, a different family from Qwen. bf16, greedy, batch size 1, GPU 0, frozen prompt `qa-v2` through the model's own chat template.
- **Before the run:** a bounded smoke test on 10 excluded prompt-development questions (output format, parse rate, determinism, GPU routing, VRAM, throughput) and a cost estimate. The run does not start if the estimate exceeds the remaining allowance.
- **Questions:** `confirm_v1` (1,744 MuSiQue + 3,232 2Wiki), Protocol A.
- **Representations:** R0, R1, R5, R4 (the six primary contrasts) and R4P_FO, R4P_FO_NC (predicted lines at fixed order; contradiction lines on/off).
- **Analysis:** the same contrasts as for Qwen, with paired bootstrap CIs. It is a **cross-model replication on the same questions**, exploratory for the controls, and a replication (not a new confirmation) of the primary contrasts. A model × representation comparison is descriptive: two readers do not support claims about model families in general.

## 4. Analyses on existing records (no generation)

- Exact-anchor vs fallback-anchor derived edges: R4−R5 stratified by `info.question_edge_stratum`.
- Serialisation accounting per representation: input, content and overhead tokens; facts, relations, answer-bearing facts; identical prompts.
- Contradiction mechanism: per-line NLI confidence, auto-triage category, and the line's question outcome (correlational only).
