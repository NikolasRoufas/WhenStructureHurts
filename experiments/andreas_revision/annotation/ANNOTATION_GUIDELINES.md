# Annotation guidelines: predicted contradictions (packages v2 and v3)

This addendum extends the `GUIDE.md` shipped with each package. The CSV files are not changed. Read both
documents before you start.

## Who labels, and how

- Two people label every pair, **independently**. Do not discuss items until both files are complete.
- Do not use ChatGPT, Claude or any other AI tool, a search engine, or an automatic checker to choose a label.
  Labels must be your own judgement of the text shown.
- Write your initials (or a pseudonymous id agreed with the project lead) in `annotator` on every labelled row.
  The two files must carry different ids. Do not put full names or e-mail addresses in the files.
- You are not shown the question, the predictor's score, the stratum, or any model output. Please do not look
  them up in the repository.

## What you label

Each row is a pair of sentences (`fact_A`, `fact_B`) that an automatic system marked as **contradicting** each
other. Your job is to decide whether that claim is right.

1. `label_sentences_only`: label from the two sentences and their source titles alone.
2. `label_with_context`: then read `passage_A` and `passage_B` and label again. **This is the primary label.**

Use exactly one of the seven labels in `GUIDE.md`. For the analysis they are grouped into three classes:

| class | labels | meaning |
|---|---|---|
| **genuine** | `genuine_contradiction` | They cannot both be true of the same entity in the same respect at the same time. |
| **false** | `compatible_different_entities`, `compatible_different_times_or_values`, `coreference_or_entity_resolution_error`, `compatible_other` | Both can be true. |
| **ambiguous** | `context_ambiguity`, `uncertain` | The text shown does not let you decide reliably. |

Choose *ambiguous* rather than guessing. It is a valid answer, and it is analysed separately.

## Decision rules and examples

The examples below are constructed for this guide; they are not items of the package.

**Entity identity.** Two sentences about different people, works or places do not contradict each other, even
if they share a name or attribute.
- "*Midnight Blue* is a 1963 album by Kenny Burrell." / "The Blackout All-Stars was a 1994 supergroup."
  → `compatible_different_entities`.
- "John Smith (born 1950) is a British actor." / "John Smith (born 1962) is an American footballer." These are
  two different John Smiths → `compatible_different_entities`.

**Same entity, different attributes or events.**
- "She was born in Athens." / "She lived in Paris for most of her life." → `compatible_different_times_or_values`.
- "The film was released in 1984." / "Filming began in 1983." → `compatible_different_times_or_values`.

**Dates and time periods.** A conflict needs the *same* event or state.
- "He was mayor from 1990 to 1994." / "He was mayor in 1998." Both can hold if he served twice → *false*,
  unless the passage says the 1990–1994 term was his only one.
- "He was born on 3 May 1920." / "He was born on 5 June 1921." The same person, birth, and two dates
  → `genuine_contradiction`.

**Numbers.** Different numbers about different things are not a conflict. Approximate figures, or figures from
different years, are usually compatible.
- "The city has 200,000 inhabitants." / "The metropolitan area has 1.2 million inhabitants." → *false*
  (different areas).
- "The bridge is 300 m long." / "The bridge is 450 m long." The same bridge and the same measure, with no
  sign of different spans or dates → `genuine_contradiction`.

**Negation and polarity.**
- "The album did not chart." / "The album reached number 12 in the UK." The same album → `genuine_contradiction`.
- "The album did not chart in the US." / "The album reached number 12 in the UK." Different countries → *false*.

**Pronouns and coreference.** If "he" or "the film" only seems to conflict because it is resolved to the wrong
entity, use `coreference_or_entity_resolution_error`.

**Context-dependent statements.** If you need information that neither the sentences nor the passages give,
for example which of two homonymous places is meant, use `context_ambiguity` in step 1 and `uncertain` in
step 2.

**Wikipedia inconsistencies.** If two passages really disagree about the same fact, for example two different
birth years for the same person, that is `genuine_contradiction`, even if one of them is a known error.

## Optional error-category tag

To help the analysis, you may start `notes` with one tag in square brackets, followed by a short reason:

`[entity]`, `[time]`, `[number]`, `[negation]`, `[context]`, `[coreference]`, `[genuine-conflict]`, `[other]`

For example: `[time] two different terms of office`. Tags are optional. A tag outside this list is refused by
the validator, so it can be corrected.

## Validation

Before handing in a file, run:

    PYTHONPATH=src python experiments/andreas_revision/annotation/annotation_tools.py validate <package_dir> <key.json>

(The project lead runs this. Annotators do not need the key and should not open it.)

## Adjudication

After both files are complete, the project lead computes agreement and creates `adjudication_package.csv`. It
contains every pair on which the two annotators chose different *classes*, plus pairs where they agree on
"false" but chose different false subtypes. A third person (or the two annotators together, after both files are
frozen) fills `adjudicated_label`, `adjudicator` and `rationale`. The adjudicator sees both labels and notes,
but no outcome or score.

## Data protection

The files contain only Wikipedia text, labels, notes and an annotator id. Annotator ids are pseudonymous. The
mapping from ids to people is kept by the project lead outside the repository. By labelling, annotators agree
that their pseudonymous labels and notes may be published with the paper's data.
