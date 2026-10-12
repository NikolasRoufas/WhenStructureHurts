# Submission readiness (2026-10-12)

**Status: internal-review draft, not ready for submission.** Nothing has been submitted anywhere (no conference, journal or arXiv), and nothing will be without the authors' decision.

## Checklist

| item | status |
|---|---|
| Official ACL template (`acl.sty`, `acl_natbib.bst` from acl-org/acl-style-files `d5adc823ff0f`), review mode | done |
| Compiles (tectonic 0.15.0 on the server) with no errors, no undefined references, no overfull boxes | done |
| Main text within 8 pages (Conclusion ends on p. 8); Limitations, references and appendices after it | done |
| Anonymous: no author names, affiliations or identifying URLs; the repository is referred to generically | done |
| Authorship and affiliations | **not set**: must be confirmed by the authors (the earlier EG-RAG paper lists two authors, which may not apply here) |
| Every number traceable to a run | done (`paper/CLAIMS_EVIDENCE_AUDIT.md`) |
| Bibliography verified against venues | done for every entry. "Dissecting GraphRAG" (named in the brief) could not be found and is not cited |
| Limitations section | done |
| Ethics / broader impact statement | not written (no human subjects; the datasets are public). Add if the venue requires it |
| Responsible NLP checklist (ACL) | not filled; needs the authors' answers (licences of MuSiQue, 2Wiki, HotpotQA, HoVer and FEVER, compute, artefact release) |
| Artefact release | code and frozen sets are in a private repository; the release decision is the authors' |
| Supplementary material | tables, figures and analysis CSVs in `research_outputs/`. Raw predictions stay on the server, recorded by sha256 |

## Blocking issues before a main-track submission

See `paper/REVIEWER_SELF_CRITIQUE.md`:
- a second generator family and a no-abstention prompt;
- a clean, pre-specified R4P ablation;
- retrieved-evidence Protocol A at scale;
- human-verified structure.

## Non-blocking polish

- The figures use matplotlib defaults with serif fonts; they could be harmonised further.
- The appendix tables are dense.
- Some Discussion numbers point to appendix tables.
