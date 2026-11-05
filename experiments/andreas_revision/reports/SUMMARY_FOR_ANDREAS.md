# Summary for Prof. Kanavos: journal-revision experiments (status 2026-11-05)

**In one sentence:** the contradiction-line effect replicates with a third, independently trained reader, but the
two human-verification experiments (A and B) cannot report anything until two annotators label the prepared pairs.

## What was done

| | request | status |
|---|---|---|
| **C** | replicate R4P_FO vs R4P_FO_NC with another model family on the 6,400 confirm2 questions | **Done** on our server (GPU 1, 3.4 GPU-hours, 12,800 / 12,800 outputs, 0 errors) |
| **A** | human verification of predicted contradictions | **Ready, waiting for annotators.** The existing 300-pair package was audited and is valid; tools, guidelines and analysis are done. 0 labels so far. |
| **B** | remove only the human-verified false contradictions | **Ready, waiting for annotators.** 300 questions selected (input-only, seed fixed); a 666-pair package built; the new conditions implemented and tested. |
| **D** | larger retrieved-evidence experiment | **Not run (NO-GO, deferred).** The existing retrieval run already shows the effect (about −2.3 EM points, CIs excluding 0). MuSiQue has only 70 unused questions left. A design is ready if a reviewer asks. |

The design was frozen in a protocol before any new run. The one change, made before the full run, is dated in
the protocol.

## Main result (Experiment C)

**Reader.** OLMo-2-1124-7B-Instruct (AllenAI; open data; different lineage from Qwen and Mistral).
- Llama-3.1 and Gemma-3 were our first choice, but they are licence-gated and we have no Hugging Face access on
  the server.
- The same config can run them later.

**Prompts.** Identical byte for byte to the Qwen confirmatory run, so only the reader changed.

**Effect of showing the contradiction lines,** on questions that have at least one:

| | 2Wiki (n = 1,490) | HotpotQA (n = 1,295) |
|---|---|---|
| Exact match | **−3.2 points** [−4.4, −2.0], confirmed | **−2.1 points** [−3.6, −0.5], confirmed |
| Lenient match | −1.9 points [−3.8, −0.1], Holm p = 0.050, formally inconclusive | **−5.8 points** [−7.7, −3.9], confirmed |
| Abstention | +2.2 points | +7.6 points |
| Qwen on the same questions (EM) | −7.7 points | −5.3 points |

**Reading**
- **Direction.** It replicates: with all three readers (Qwen, Mistral, OLMo-2), the contradiction lines lower
  accuracy and raise abstention. For OLMo-2, most of the loss is correct answers becoming "insufficient
  evidence". For Qwen, correct → wrong and correct → abstain are about equally common.
- **Size.** It depends on the reader. On HotpotQA OLMo-2 is as affected as Qwen; on 2Wiki it is affected less
  than half as much.
- **Caveats.**
  - OLMo-2 often ignores the short-answer format, so its exact match is very low (4–12 %). The lenient score is
    the more informative one for this model; we report both.
  - This is a new reader on reused questions, not a new sample.

## What I need from you

1. **Two annotators.** They label 300 + 666 sentence pairs with a 3-class judgement (genuine / false / ambiguous),
   independently and without AI tools, plus a third person for disagreements. Expect about 16 hours each.
   - Files and guidelines: `experiments/andreas_revision/annotation/`.
   - This is the only blocker for the paper's causal question: are the harmful contradictions false, and does
     removing only those restore accuracy?
2. **Optional.** If you want Llama or Gemma specifically, a Hugging Face account with the licence accepted
   (a read token).
3. **A decision on the journal after A and B.**
   - With human-verified results, the paper supports a causal claim suited to TACL or TMLR.
   - Without them, it is a solid, replicated empirical finding with an open mechanism, better suited to IP&M or
     KAIS.

The full report, with every number, file and checksum, is `experiments/andreas_revision/reports/FINAL_EXPERIMENTAL_REPORT.md`.
