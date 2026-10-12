# Submission readiness (revision-1, 2026-10-13)

**Status: internal-review draft. Not submitted anywhere** (no conference, journal or arXiv), and nothing will be without the authors' explicit decision.

## Checklist

| item | status |
|---|---|
| Official ACL template (`acl.sty`, `acl_natbib.bst`, acl-org/acl-style-files `d5adc823ff0f`), review mode, line numbers | done |
| Compiles with tectonic on the server: no errors, no undefined references or citations | done |
| Overfull boxes | one of 1.4 pt in the Fig. 1 TikZ (appendix, invisible); none in tables |
| Main text within 8 pages (Conclusion ends on p. 8); Limitations, references, appendices after it | done (20 pages total) |
| Every page inspected visually (rendered PDF, not only the log) | done 2026-10-13 |
| Anonymous: no names, affiliations or identifying URLs | done |
| Authorship and affiliations | **not set**; must be confirmed by the people involved |
| Every number traceable to a run | `paper/CLAIMS_EVIDENCE_AUDIT.md`, `docs/REPRODUCIBILITY_CHECKLIST.md` |
| Bibliography checked against venues; Nishida et al. (TACL 2026) cited with official BibTeX | done |
| Exploratory vs confirmatory labelled in text, tables and captions | done |
| Limitations section | done |
| Ethics statement / Responsible NLP checklist | not filled; needs the authors' answers (dataset licences, compute, artefact release) |
| Human annotation | none collected; no human-verified precision/recall reported |

## Blocking issues before a main-track submission

1. A second reader from another model family (configured; needs authorisation and about 5.5 GPU-hours).
2. Human labels for the blinded contradiction pairs, to establish that the predicted contradictions are false.
3. Optionally, a fresh-sample, pre-specified test of the contradiction effect to turn the main exploratory finding into a confirmatory one.

See `paper/REVIEWER_SELF_CRITIQUE.md` and `docs/FINAL_RESEARCH_ASSESSMENT.md`.

## Non-blocking polish

- Figure 5 and Table 18 sit on mostly empty appendix pages (float placement); harmless in review mode.
- Some appendix tables are dense (Table 12 transitions).
