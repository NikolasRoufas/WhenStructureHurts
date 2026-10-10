"""Experiment 0 - rebuilt baselines B0-B4 on retrieved evidence, with the repaired evaluation
(stable unique ids, invalid citations separated from wrong answers, explicit truncation and
format tracking, corrected FEVER verdict scoring, full denominators)."""

from __future__ import annotations

from ..systems import SYSTEM_REPRESENTATION, build_system_bundle
from .common import Runner, make_layout


def body(runner: Runner, questions) -> None:
    cfg = runner.cfg
    for ds, qs in questions.items():
        res = runner.res.egrag_resources(ds)
        for q in qs:
            for system in cfg.exp0.systems:
                rep = SYSTEM_REPRESENTATION[system]
                cond = {"system": system, "representation": rep, "extraction": cfg.extraction.method,
                        "top_k": cfg.retrieval.top_k}

                def build(system=system, rep=rep, q=q):
                    b, trace = build_system_bundle(system, q, cfg, res)
                    return b, make_layout(rep, b), trace

                runner.run(q, cond, build)
