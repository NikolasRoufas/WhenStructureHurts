# Human verification of predicted contradictions (package v3)

Two people label the same 666 sentence pairs **independently** (`pairs_annotator1.csv`, `pairs_annotator2.csv`;
the rows are in different orders). Do not discuss items until both files are complete.

Each pair was marked CONTRADICTS by an automatic relation predictor. Both sentences come from Wikipedia passages
that a dataset marks as supporting evidence for one question. You are not shown the question, the predictor's
score, or any model output.

**Step 1 (`label_sentences_only`).** Read only `fact_A` and `fact_B` (with their source titles) and decide whether
they contradict each other as written. Fill this column for the row before reading the passages.

**Step 2 (`label_with_context`).** Now read `passage_A` and `passage_B` (the full passages the sentences come
from) and label the pair again. It may change or stay the same.

Use exactly one of:

- `genuine_contradiction`
- `compatible_different_entities`
- `compatible_different_times_or_values`
- `coreference_or_entity_resolution_error`
- `context_ambiguity`
- `compatible_other`
- `uncertain`

- genuine_contradiction: both sentences cannot be true of the same thing at the same time.
- compatible_different_entities: they are about different people, works or places.
- compatible_different_times_or_values: same entity, different events, dates, roles or attributes that can all be true.
- coreference_or_entity_resolution_error: a conflict appears only if a pronoun or name is resolved to the wrong entity.
- context_ambiguity: cannot be decided from what you can see (use only in step 1 if the passage is needed).
- compatible_other: no conflict, for another reason (say which in `notes`).
- uncertain: you cannot decide.

Write your initials in `annotator` on every labelled row. Never guess to fill a row; leave it blank instead.
Do not use any AI tool to label. Validate with
`PYTHONPATH=src python scripts/revision/false_contradictions.py import <this directory> <key.json>`.
