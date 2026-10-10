# Annotation guide: verification package v1

**Purpose.** Check the reasoning structure that the framework derives *automatically* from dataset annotations. This covers step order, DEPENDS_ON edges between sentences, and a sample of derived claims. Questions you verify become **stratum A (human-verified)** in the graph experiments. Questions you don't verify stay in strata B and C (automatically derived) and are analysed separately.

These 50 questions are drawn from the frozen pilot set (`configs/question_sets/pilot_v1.json`). They let us check annotation quality; **they are not a statistical sample for conclusions.**

Expected effort: about 3–5 hours for one annotator.

## Files

| file | what to do |
|---|---|
| `review.md` | **Read only.** Shows each question with its passages, sentence IDs (`s00`, `s01`, …), proposed steps and proposed edges. |
| `paths.csv` | One row per question. Fill in the step-order judgement. |
| `edges.csv` | One row per proposed DEPENDS_ON edge. Fill in a verdict. |
| `claims.csv` | One row per derived claim, or per context-dependent supporting sentence. Fill in faithfulness. |
| `package.jsonl`, `MANIFEST.json` | Machine reference. **Do not edit.** |

Only edit the columns listed below. The importer rejects any change to other columns, such as IDs and proposed values. Put your annotator ID (e.g. initials) in the `annotator` column of every row you fill. You may edit the CSVs in a spreadsheet, but save them as UTF-8 CSV and keep the header row unchanged.

## What a DEPENDS_ON edge means

`A DEPENDS_ON B` means you need the fact in sentence B to know what sentence A is about, or to use A, when answering the question. Typically B supplies the bridge entity that A talks about. For example: B = "DeepMind was acquired by Google"; A = "Google was founded by Larry Page".

The edge should connect the **specific sentences** that carry the bridge. "Fallback" edges were attached to a step's first supporting sentence because no sentence mentioned the bridge entity, so check those endpoints especially carefully.

## paths.csv

- `answer_correct`: `yes` / `no` / `uncertain`. Is the dataset's gold answer correct given the passages? This is recorded only; benchmark labels are never changed.
- `path_verdict`:
  - `correct`: the proposed step order (`proposed_step_titles`) is a valid order for answering.
  - `incorrect`: the order is wrong.
  - `uncertain`
- `corrected_passage_order`: only when the verdict is `incorrect`. Give the passage IDs from `proposed_passage_order`, separated by `;`, in the correct order. It must be a permutation of the proposed IDs.
- `missing_edges`: optional. Add dependencies the package missed, as `<source claim id>><target claim id>` pairs separated by `;`. Use full claim IDs, as shown in `package.jsonl` and `edges.csv`.
- `notes`: free text.

For comparison questions ("Which is older, A or B?") the steps are parallel. Mark `correct` if neither step needs the other.

## edges.csv

`verdict`:
- `correct`: the dependency is real, and the endpoints are the right sentences.
- `wrong_endpoint`: the dependency is real, but the source and/or target sentence is wrong. Fill `corrected_source_claim_id` and/or `corrected_target_claim_id` with a claim ID of the same question.
- `wrong_direction`: the dependency is real but reversed.
- `not_a_dependency`: there is no such dependency.
- `uncertain`

## claims.csv

`why_listed` is either `derived_claim` (a rule-based split of a sentence) or `context_dependent_supporting_sentence` (a supporting sentence that opens with a pronoun or back-reference).

- `faithful`: `yes` / `partial` / `no` / `uncertain`. Does `claim_text` say only what `source_sentence_text` says? Use `partial` if it drops a qualifier or changes scope.
- `self_contained`: `yes` / `no` / `uncertain`. Can the claim be understood on its own, without neighbouring sentences? (e.g. "It is located in Paris" → `no`)

## Rules

- Use only the passages shown. Do not look up outside sources.
- When in doubt, answer `uncertain` and explain in `notes`. A question counts as verified only if its path row **and every** edge row have a definite verdict (not `uncertain`). Uncertain questions stay in strata B/C.
- Two annotators, if available, should work on copies. Disagreements are resolved before import; the importer keeps every annotator ID.

## Import

```bash
.venv/bin/wsh annotations import --package annotations/verification_v1 \
    [--completed <directory with your edited CSVs>] --out annotations/verified/verification_v1.jsonl
```

The importer:
- validates the vocabulary, the required corrections, and that every claim ID exists in that question;
- re-links every question to the current dataset files by content digest;
- refuses on **any** error and lists all of them;
- never overwrites an existing output.

To use the result, set `verified_annotations: annotations/verified/verification_v1.jsonl` in the experiment config.

## Licences

The passages come from the MuSiQue (CC BY 4.0), 2WikiMultihopQA (Apache-2.0) and HotpotQA (CC BY-SA 4.0) development sets. Redistribution of this package must keep this attribution and the CC BY-SA terms.
