"""Experiment 2 - controlled structural perturbations P1-P7 on gold-evidence representations.

Every (question, representation, perturbation, params, seed) is run at each configured rate,
including rate 0 (the unperturbed reference; identical prompts are served from the generation
cache and flagged). Sensitivity is computed per question relative to its own rate-0 record.
Interventions that do not apply to a question (e.g. P2 without edges, P7 without a verified
temporal spec) are recorded as unavailable.
"""

from __future__ import annotations

from .. import interventions
from ..representations.evidence import EvidenceUnavailable, gold_bundle
from .common import ConditionUnavailable, Runner, make_layout


def body(runner: Runner, questions) -> None:
    e2 = runner.cfg.exp2
    for ds, qs in questions.items():
        for q in qs:
            try:
                base = gold_bundle(q, runner.cfg.exp1.evidence_scope)
                base_err = None
            except EvidenceUnavailable as e:
                base, base_err = None, e
            for rep in e2.base_representations:
                for spec in e2.perturbations:
                    params = dict(spec.params)
                    if spec.name == "P7":
                        params.setdefault("spec_path", e2.temporal_spec_path)
                    for rate in spec.rates:
                        for seed in e2.seeds:
                            cond = {"representation": rep, "perturbation": spec.name,
                                    "params": {k: v for k, v in params.items() if k != "spec_path"},
                                    "rate": rate, "pseed": seed, "scope": runner.cfg.exp1.evidence_scope}

                            def build(rep=rep, spec=spec, params=params, rate=rate, seed=seed):
                                if base_err:
                                    raise base_err
                                if rep == "R3" and not base.path:
                                    raise ConditionUnavailable("reasoning path unavailable")
                                pb, rec = interventions.apply(spec.name, base, q, rate, seed, params)
                                if not rec.applicable and rate > 0:
                                    raise ConditionUnavailable(f"{spec.name} not applicable: {rec.reason}")
                                if spec.name == "P2" and rep not in ("R4", "R4P") and rate > 0:
                                    raise ConditionUnavailable("P2 only affects graph representations")
                                return pb, make_layout(rep, pb, seed), {"intervention": rec.to_dict()}

                            runner.run(q, cond, build)
