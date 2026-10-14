# Documentation

| document | content |
|---|---|
| [EXPERIMENT_SPEC.md](EXPERIMENT_SPEC.md) | every condition, control, metric and contrast, with code paths |
| [METHODOLOGICAL_AUDIT.md](METHODOLOGICAL_AUDIT.md) | validity risks and the guards that address them (tested in `tests/test_validity_guards.py`) |
| [EGRAG_RECONSTRUCTION.md](EGRAG_RECONSTRUCTION.md) | baselines B0–B4 and the component choices of the EG-RAG reconstruction |
| [PILOT_PROTOCOL.md](PILOT_PROTOCOL.md) | frozen pilot design: contrasts, metric, statistics, sample-size rule |
| [CONFIRMATORY_PROTOCOL.md](CONFIRMATORY_PROTOCOL.md) | frozen protocol of the first confirmatory run (`configs/confirm.yaml`) |
| [CONFIRMATORY_PROTOCOL_2.md](CONFIRMATORY_PROTOCOL_2.md) | frozen protocol of the second confirmatory run (`configs/confirm2.yaml`) |
| [REVISION_PROTOCOL.md](REVISION_PROTOCOL.md), [REVISION2_PROTOCOL.md](REVISION2_PROTOCOL.md) | exploratory runs (relation controls, retrieved evidence, prompt variants, second reader) |

The protocols are kept verbatim as frozen; references in them to other documents point to the research record, which is preserved in the `revision-1` branch and the `research-record-revision2` tag.
