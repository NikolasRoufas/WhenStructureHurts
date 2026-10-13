# ACL 2027 / ARR submission checklist (checked 2026-10-13)

**Nothing has been submitted.** Submission requires the authors' explicit decision.

## Sources (official pages, read 2026-10-13)

- ACL 2027 main call: https://2027.aclweb.org/calls/main/
- ARR dates: https://aclrollingreview.org/dates
- ARR author checklist: https://aclrollingreview.org/authorchecklist
- ACL sustainable reviewing policy (applies to ARR from October 2026): https://www.aclweb.org/portal/node/14591
- ACL policy on AI writing assistance (linked from the ACL 2027 call): https://2023.aclweb.org/blog/ACL-2023-policy/

Policies change between cycles. Re-read every page above in the week of submission.

## Route and dates

| item | official statement | consequence for us |
|---|---|---|
| ACL 2027 | Kyoto, 17–22 August 2027; submission through ARR | — |
| ARR deadline for ACL 2027 | "Jan 4, 2027", 11:59 pm UTC−12 (AoE), long and short papers | target cycle: **January 2027** |
| October 2026 ARR cycle | deadline 12 October 2026 (feeds NAACL/COLING 2027) | **already passed** |
| Commitment / notification | "TBD" | check in December |
| Findings | papers not selected for the main conference are automatically considered for Findings of ACL | no separate submission |

## Format

| requirement | official | status |
|---|---|---|
| Long paper ≤ 8 pages | "8 for long … not including limitations and ethical considerations"; references and appendices also excluded; all in one PDF | **met**: Conclusion ends on p. 8 (re-check after the revision-2 rewrite) |
| Camera-ready +1 page | 9 pages | — |
| ACL template | official `acl.sty` | met (acl-org/acl-style-files `d5adc823ff0f`) |
| Limitations section | required, titled "Limitations"; "strictly no new experiments, figures or analysis" | present; contains no new analysis |
| Ethical considerations | recommended title "Ethical considerations"; may extend to p. 9 | **to add** (short: public datasets, no human subjects yet, compute, AI assistance) |
| Acknowledgements | must not be included at submission | none in the PDF |

## Anonymity

| requirement | status |
|---|---|
| No author names, affiliations or self-identifying references to prior work | met: `\author{Anonymous ACL submission}`. Our earlier EG-RAG paper is not cited, and B4 is described as "our reconstruction" without attribution. Re-check before submission |
| No links to non-anonymous repositories or tracking services | met: the paper refers to "the repository" without a URL. The GitHub repository **must not** be linked; use an anonymised copy (e.g. anonymous.4open.science) for supplementary code |
| Supplementary material anonymised | to do: strip author names from `docs/`, configs and git metadata in any uploaded archive |
| Preprint field | the "we do not intend to release" option is binding; authors decide |

## Responsible NLP checklist (filled on OpenReview; the authors must answer)

Inappropriately filled checklists "can be considered grounds for desk rejection". Answers need section numbers and justifications, not blanket "yes".

| item | where in the paper / repository |
|---|---|
| Limitations | Limitations section |
| Risks | Ethical considerations (to add) |
| Artefacts used, their licences and intended use | MuSiQue (CC BY 4.0), 2WikiMultiHopQA (Apache-2.0), HotpotQA (CC BY-SA 4.0), HoVer (CC BY-SA 4.0), FEVER (CC BY-SA 3.0); Qwen2.5-7B-Instruct (Apache-2.0); Mistral-7B-Instruct-v0.3 (Apache-2.0); bge-small-en-v1.5 (MIT); ms-marco-MiniLM-L6-v2 and nli-deberta-v3-xsmall/small (Apache-2.0). **Every licence must be verified by the authors on the dataset or model card before submission** |
| Data statistics | §5; `configs/question_sets/*.json` |
| Compute (model sizes, GPU-hours, hardware) | §5 "Hardware"; `docs/REVISION_EXPERIMENT_LOG.md` |
| Hyperparameters, decoding | §5; configs |
| Statistics: error bars, number of runs | every estimate has a paired bootstrap CI; greedy decoding, one run (deterministic) |
| Packages | `pyproject.toml`, `uv.lock` |
| Human annotators | none completed. If the blinded packages are labelled before submission: instructions (`GUIDE.md`), recruitment, pay, consent and ethics review must be reported |
| AI assistants | see the next section |

## Generative AI disclosure (required)

ACL policy (2023, linked from the ACL 2027 call) requires authors to describe the scope and nature of any use of writing or coding assistants. The ARR checklist page asks authors to disclose it "in either the acknowledgements or the checklist itself". Acknowledgements are excluded at submission, so the disclosure goes in the **checklist**, and in the acknowledgements of the camera-ready version. Generative AI cannot be an author. The authors are responsible for every claim, citation and number.

The use was substantial. A truthful draft for the authors to verify and edit:

> We used an AI coding and writing assistant (Anthropic's Claude, via Claude Code) extensively throughout this project. It wrote most of the experiment and analysis code, ran experiments on our server under our instructions and compute limits, drafted the protocols, and drafted and revised most of the manuscript text, tables and figures. All design decisions, authorisations (compute, new data, models) and final claims were made by the authors. Every number in the paper is generated by scripts from saved predictions and was cross-checked by an independent audit script; the authors [must state here what they personally verified: code review, re-running analyses, checking citations]. No AI system was used to produce human annotations.

The bracketed part must be completed truthfully by the authors. **Human verification of the work** (citations, code, analyses and claims) is the authors' responsibility before submission.

## Sustainable reviewing (from October 2026)

Each submission must provide a qualified service contributor (reviewer or chair). Submissions without one enter a lottery for spare capacity and "may be desk rejected". There are caps of 20 submissions and 5 first-author submissions per author per cycle. **Action for the authors:** designate a qualified reviewer at submission time.

## Other desk-rejection risks to check

- **Hallucinated references:** every bibliography entry was verified against its publisher page in revision-1/2 (`paper/README.md`). Re-check after the final edits.
- **Salami slicing:** this paper and our earlier EG-RAG architecture paper ask different questions. Make sure no result is shared between them.
- **Author list:** it cannot change after submission. Decide it before uploading.
- **Dual submission:** not allowed.

## Remaining actions for the authors

1. Decide authorship and order (no AI author).
2. Complete and verify the AI-assistance disclosure.
3. Verify the dataset and model licences.
4. Fill the Responsible NLP checklist on OpenReview.
5. Designate a qualified reviewer.
6. Prepare an anonymised code supplement.
7. Add the Ethical considerations section (draft provided in the paper).
8. Re-read the official pages above in the submission week.
