# INVALID RUN - kept for the audit trail, do not use

All cross-encoder reranker scores in this run were NaN (misaligned memory-mapped weights on
Apple CPU; see `realign_parameters` in src/wsh/models/encoders.py). Sorting on NaN preserved
the first-stage order, so B1 silently equalled B0, and B2-B4 (which rerank) used unreranked
passages. NLI and dense encoders were verified unaffected (no non-finite cached values).
Superseded by the next exp0 smoke run. Discovered 2026-10-10 while inspecting B0==B1.
