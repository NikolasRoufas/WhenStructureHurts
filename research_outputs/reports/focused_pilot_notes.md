## 10. Manual failure analysis (written by the analyst; inputs are the records named here)

**Method.** I read every 2WikiMultiHopQA question that is discordant under Protocol A for R1−R0 (17 questions) and for R4−R5 (7 questions). Source: `A_exp1_discordant_examples.json` (`scripts/analysis/examples.py`). Each case was classified by what the two outputs show. No case was removed.

**R1 vs R0 (2Wiki; R0 correct and R1 wrong on 12, the reverse on 5).**

- **Abstention despite complete evidence (7 of the 12 R0-only wins).** R1 replies *insufficient evidence* while R0 answers correctly on the same facts. Example: `2wiki/77f41ab2…`, "Who is Edward De Vere, 17th Earl of Oxford's paternal grandfather?"; R0 answers *John de Vere, 15th Earl of Oxford*, R1 abstains. These questions need two facts that sit in different passages. Under R0 each passage is one item; under R1 the facts are separate sentence items with their titles.
- **Wrong comparison outcome (both directions).** On "who was born earlier / which film came first" questions, the two formats pick opposite entities in 5 cases. Examples: `0f447508…` (R0 *Silas Hardy*, R1 *Lee Mantle* = gold) and `85483fe9…` (R0 *Ernst Ziehm* = gold, R1 *Horace Lawson Hunley*). These look like unstable date comparisons rather than missing evidence: both blocks contain both dates.
- **Template copying (1).** `f23fe16c…`: R1 answers the literal string *a name*, copied from the format instruction `<short answer: a name, …>`.
- **Evaluation strictness (1).** `2f7507ba…`: R0 answers *Theobald II of Bar* against the gold *Theobald II, Count of Bar*. It scores 0 under exact match, yet is arguably correct.

**R4 vs R5 (2Wiki; R4 correct and R5 wrong on 5, the reverse on 2).**

- **Bridge entity returned instead of the final answer (2 of the R4 wins).** R5 names the intermediate entity:
  - `25ca7393…`: R5 *Bakhtyar Khudojnazarov*, a director, where the question asks for a film.
  - `7a71a91e…`: R5 *a name: Ralph Nelson*.
  With the relation lines (R4), the model returns the film. This is the clearest qualitative case of explicit relations helping.
- **Abstention removed (2).** `bf3fd3ba…` and `ea755618…`: R5 abstains and R4 answers correctly.
- **Evaluation error (1, against R4).** `46e4933a…`: R4 answers *Duke Louis of Wurttemberg* and the gold is *Duke Louis of Württemberg*. SQuAD normalisation does not fold diacritics. Folding them (secondary check, §7) changes 3 Protocol A 2Wiki records and no contrast conclusion.

**Error taxonomy (§5), all incorrect records.**
- Under Protocol A, the commonest category is abstention:
  - MuSiQue: 41–58 of 69–79 incorrect per representation;
  - 2Wiki: 16–34 of 56–63.
- With complete gold evidence, the answer string is present in 0.99 (MuSiQue) and 0.98 (2Wiki) of blocks. Missing evidence therefore explains almost none of the Protocol A errors.
- About 10 % of incorrect answers have F1 ≥ 0.5. These are candidates for alias or format mismatches, which is why F1 is reported beside EM throughout.

## 11. Interpretation (exploratory; nothing here is confirmatory)

1. **H1 / H2.** None of the six primary Protocol A contrasts excludes zero (largest |Δ| = 0.07). The pilot can detect only differences much larger than the 0.03 minimum effect of interest. The pre-specified confirmatory test (`docs/CONFIRMATORY_PROTOCOL.md`) is the way to resolve them.
2. **Abstention is a main channel of representation effects for this generator.** On 2Wiki the structured formats abstain on 24–34 of 100 questions, against 16 for raw passages, at identical facts. EM differences between representations are partly coverage differences, which the paired coverage Δ reports.
3. **Serialisation overhead costs evidence under a budget (H4).** At 1.0× the content tokens (per-representation policy):
   - R0 keeps 0.83 (2Wiki) and 0.81 (MuSiQue) of the facts;
   - R1, R4 and R5 keep 0.62–0.65;
   - answer-bearing facts dropped per question: 2Wiki 0.11 for R0 against 0.33–0.34; MuSiQue 0.19 against 0.28–0.35.
   The EM consequences are smaller than the evidence losses and inconclusive at n = 100. Many questions are failed even with complete evidence, so losing a fact changes the outcome only where the model would otherwise have answered correctly.
4. **Relations matter only where they exist.** 29 of 100 2Wiki questions (mostly comparison questions) and 25 of 50 HotpotQA questions have no edges, so R4 = R5 there. HoVer and FEVER have no derived structure at all, so R1 = R5 = R4 on every claim.
