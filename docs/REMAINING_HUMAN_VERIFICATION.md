# Remaining human verification (revision-1)

No result in the paper rests on human labels; none have been produced, and none may be invented. Two packages are ready for annotators. Until they are completed and imported, the paper reports **no** human-verified precision or recall, and every relation is labelled *derived* (from dataset annotations) or *predicted* (by a model).

## Package 1: derived structure (`annotations/verification_v1/`, prepared 2026-10-10)

- **Scope:**
  - 50 questions (MuSiQue 20, 2Wiki 15, HotpotQA 15) from the pilot set;
  - 64 derived dependency edges (42 exact-anchor, 22 fallback-anchor);
  - 178 claim items.
- **Annotator task:**
  - verify each reasoning path;
  - judge each dependency edge (correct / wrong endpoint / wrong direction / not a dependency);
  - judge whether each claim item is faithful to its source sentence.
- **Guide:** `annotations/verification_v1/GUIDE.md`.
- **Import:** `wsh annotations import --package annotations/verification_v1 --out annotations/verified/verification_v1.jsonl`. The importer validates every row, links each question to the current dataset files by digest, and refuses incomplete or inconsistent files.
- **Unblocks:**
  - Exp3 (component attribution) on the 50 verified questions;
  - an edge stratum A (human-verified) in every structural contrast;
  - a measured error rate of the fallback anchors.
- **Estimated effort:** 3–5 annotator-hours; a second annotator on 20 % of the items would give agreement.

## Package 2: predicted contradiction relations (`research_outputs/revision/contradictions/human_package_v1/`)

- **Scope:** 240 unordered pairs of facts labelled CONTRADICTS by the NLI predictor and shown to the reader under R4P on the confirmatory sample.
  - Stratified: 120 pairs where the derived-relation format (R4) was answered correctly and the predicted-relation format (R4P) abstained, and 120 other pairs.
  - The annotator sees only the two sentences and their source titles. Questions, model outputs, NLI scores and automatic categories are hidden (blinded).
- **Labels:**
  - `genuine_contradiction`;
  - `compatible_different_entities`;
  - `compatible_different_times_or_values`;
  - `coreference_or_entity_resolution_error`;
  - `context_ambiguity`;
  - `uncertain`.
- **Guide:** `GUIDE.md` in the package.
- **Import:** `PYTHONPATH=src python scripts/revision/contradictions.py import <package>`. It refuses invalid labels and labels without an annotator ID, and writes `IMPORT_REPORT.json`.
- **Key file:** `human_package_v1_KEY_do_not_share_with_annotators.json` maps items to questions, outcomes and categories. Do not give it to annotators.
- **Unblocks:**
  - the false-contradiction rate of the predictor, with a CI;
  - whether harm concentrates on wrong contradiction labels (outcome × label analysis);
  - an oracle-corrected condition that removes only verified-wrong contradiction lines.
- **Estimated effort:** about 2 annotator-hours per 120 pairs; two annotators are recommended.

## What the paper says until then

- **Relation quality:** automatic diagnostics only. 40 % of contradiction pairs link facts with different source titles, and a further 20 % are same-title pairs that differ in their years. These are heuristic categories, not judgements.
- **Effect of contradiction lines:** the fixed-order intervention (removing the lines) is reported as an effect of *the lines*, whatever their correctness. Whether *wrong* lines cause the harm needs Package 2.
