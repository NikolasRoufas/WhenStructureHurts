# SUPERSEDED (2026-10-10, pre-GPU preflight) - raw predictions kept unchanged

The raw records in `predictions.jsonl` are intact and remain the record of what the model
produced. The per-record evaluation fields and the derived summaries (`metrics.json`,
`summary.csv`, `report.md`) were computed with metric definitions that have since been
corrected. They are superseded and must not be cited or compared with newer runs:

- **answered/coverage:** an abstention ("insufficient evidence") was counted as answered. It now
  counts as unanswered (coverage), while still scoring 0.
- **primary metric:** these reports use token F1 for QA. The frozen protocol uses exact match
  (docs/PILOT_PROTOCOL.md).
- **missing fields:** `citation_status` (missing vs invalid citations) and `evidence_sufficient`
  do not exist in these records.
- **answer_in_evidence / hop_answer_coverage:** these were order-dependent in runs before the
  first audit fix.
- **Exp1 only:** the `min_matched` budget mode (end truncation) is retired; its conditions confound
  structure with information loss. Replaced by Protocols A and B.
- **Exp2 only:** these records have no `answer_introduced` audit, and P4 could inject
  answer-bearing distractors.
- **Exp3 only:** there is no edge-stratum separation, and C2 agreement on HotpotQA (a circular label) is
  not suppressed.

Re-scoring these records would require rebuilding each record's evidence bundle (retrieval +
LLM extraction for Exp0/Exp3, perturbations for Exp2). That was not done, because smoke scores
carry no scientific weight; the corrected pipeline was instead re-run on the smoke questions
(see docs/EXPERIMENT_LOG.md, section "Pre-GPU preflight").
