# Human verification: predicted contradiction relations (package v1)

You will see 240 pairs of sentences. Each pair was labelled CONTRADICTS by an automatic relation predictor.
Both sentences come from Wikipedia passages that a dataset marks as supporting evidence for a question
(the question itself is not shown). Judge only whether the two sentences, read as they are, contradict
each other. Do not look anything up. Fill `label` with exactly one of:

- `genuine_contradiction`
- `compatible_different_entities`
- `compatible_different_times_or_values`
- `coreference_or_entity_resolution_error`
- `context_ambiguity`
- `uncertain`

Definitions:
- genuine_contradiction: both sentences cannot be true of the same thing at the same time.
- compatible_different_entities: they describe different people/works/places, so no conflict.
- compatible_different_times_or_values: same entity, but different events, dates, roles or attributes that can all be true.
- coreference_or_entity_resolution_error: a conflict appears only because a pronoun or name is resolved to the wrong entity.
- context_ambiguity: cannot be decided without the surrounding passage.
- uncertain: none of the above can be decided.

Write your initials in `annotator` on every row, and anything unusual in `notes`. Labels must be your own
judgement; leave a row blank rather than guessing. Import with:
`PYTHONPATH=src python scripts/revision/contradictions.py import <this directory>`.
