"""Command-line entry point.

    wsh data fetch --dataset musique [--split dev]
    wsh data inspect --dataset musique --n 2
    wsh models check|fetch <model_id> --stage smoke
    wsh validate-config configs/smoke.yaml
    wsh run {exp0,exp1,exp2,exp3} --config configs/smoke.yaml [--resume DIR] [--set key=value ...]
    wsh exp4 --config configs/smoke.yaml --source-run DIR [--plumbing-check]
    wsh report RUN_DIR
    wsh questions freeze --spec configs/question_sets/pilot_v1.spec.yaml --out configs/question_sets/pilot_v1.json
    wsh annotations export --questions configs/question_sets/pilot_v1.json --out annotations/verification_v1
    wsh annotations import --package annotations/verification_v1 [--completed DIR] --out annotations/verified/v1.jsonl
    wsh preflight --config configs/pilot.yaml [--tiny-generation]
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys

import yaml


def _parse_sets(items: list[str] | None) -> dict:
    out = {}
    for it in items or []:
        k, v = it.split("=", 1)
        out[k] = yaml.safe_load(v)
    return out


def main(argv: list[str] | None = None) -> int:
    # must be set before CUDA initialises for deterministic cuBLAS (no effect on CPU/MPS)
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    ap = argparse.ArgumentParser(prog="wsh")
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("data")
    d.add_argument("action", choices=["fetch", "inspect"])
    d.add_argument("--dataset", required=True)
    d.add_argument("--split", default="dev")
    d.add_argument("--n", type=int, default=2)
    d.add_argument("--seed", type=int, default=0)

    m = sub.add_parser("models")
    m.add_argument("action", choices=["check", "fetch"])
    m.add_argument("model_id")
    m.add_argument("--stage", default="smoke")
    m.add_argument("--authorized-compute", action="store_true")

    v = sub.add_parser("validate-config")
    v.add_argument("config")
    v.add_argument("--authorized-compute", action="store_true")

    r = sub.add_parser("run")
    r.add_argument("experiment", choices=["exp0", "exp1", "exp2", "exp3"])
    r.add_argument("--config", required=True)
    r.add_argument("--resume")
    r.add_argument("--set", nargs="*", help="override config values, e.g. model.max_new_tokens=48")
    r.add_argument("--authorized-compute", action="store_true",
                   help="required (with WSH_COMPUTE_AUTHORIZED=1) for the 'full' stage")

    e4 = sub.add_parser("exp4")
    e4.add_argument("--config", required=True)
    e4.add_argument("--source-run", required=True)
    e4.add_argument("--plumbing-check", action="store_true")

    rp = sub.add_parser("report")
    rp.add_argument("run_dir")

    qs = sub.add_parser("questions")
    qs.add_argument("action", choices=["freeze"])
    qs.add_argument("--spec", required=True)
    qs.add_argument("--out", required=True)

    an = sub.add_parser("annotations")
    an.add_argument("action", choices=["export", "import"])
    an.add_argument("--questions", help="frozen question set JSON (export)")
    an.add_argument("--quotas", default="musique=20,2wikimultihopqa=15,hotpotqa=15")
    an.add_argument("--seed", type=int, default=0)
    an.add_argument("--package", help="package directory (import)")
    an.add_argument("--completed", help="directory with the completed CSVs (default: the package directory)")
    an.add_argument("--out", required=True)

    pf = sub.add_parser("preflight")
    pf.add_argument("--config", required=True)
    pf.add_argument("--authorized-compute", action="store_true")
    pf.add_argument("--tiny-generation", action="store_true", help="load the configured generator and generate once")

    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO if a.verbose else logging.WARNING, format="%(asctime)s %(name)s %(message)s")

    if a.cmd == "data":
        if a.action == "fetch":
            from .fetch import fetch_dataset

            print(fetch_dataset(a.dataset, a.split))
        else:
            from .data.loaders import sample_questions

            for q in sample_questions(a.dataset, a.split, a.n, a.seed):
                print(json.dumps({"uid": q.uid, "question": q.question, "answers": q.answers, "type": q.question_type,
                                  "hops": q.hop_count, "gold_passages": q.gold_passage_ids(),
                                  "steps": [s.model_dump() for s in q.reasoning_steps],
                                  "annotations": {k: v.value for k, v in q.annotations.items()},
                                  "notes": q.annotation_notes}, indent=2, ensure_ascii=False))
        return 0

    if a.cmd == "models":
        from .models.policy import check_model

        entry = check_model(a.model_id, None, a.stage, authorized_flag=a.authorized_compute)
        if a.action == "check":
            from .models.policy import load_model_registry, preflight

            pol, _ = load_model_registry()
            print(json.dumps(preflight(entry, pol), indent=2))
        else:
            from .fetch import fetch_model

            print(json.dumps(fetch_model(a.model_id, a.stage, a.authorized_compute), indent=2))
        return 0

    if a.cmd == "validate-config":
        from .config import load_config

        cfg = load_config(a.config)
        cfg.enforce_model_policy(a.authorized_compute)
        print(f"OK: {a.config} (stage={cfg.stage}, model={cfg.model.model_id}, datasets={[x.name for x in cfg.datasets]})")
        return 0

    if a.cmd == "run":
        from .config import load_config
        from .experiments import exp0_baselines, exp1_representations, exp2_perturbations, exp3_component_analysis
        from .experiments.common import run_experiment

        cfg = load_config(a.config, _parse_sets(a.set))
        body = {"exp0": exp0_baselines.body, "exp1": exp1_representations.body, "exp2": exp2_perturbations.body,
                "exp3": exp3_component_analysis.body}[a.experiment]
        ctx = run_experiment(cfg, a.experiment, body, resume_dir=a.resume, authorized_flag=a.authorized_compute)
        print(ctx.dir)
        return 0

    if a.cmd == "exp4":
        from .config import load_config
        from .evaluation.reporting import load_records
        from .experiments.exp4_adaptive_selection import evaluate_selectors

        cfg = load_config(a.config)
        if not (cfg.exp4.enabled or a.plumbing_check):
            print("Experiment 4 is gated: set exp4.enabled only after Experiments 1-3 show a reproducible effect, "
                  "or use --plumbing-check to exercise the code path.", file=sys.stderr)
            return 2
        res = evaluate_selectors(load_records(a.source_run), cfg.exp4.selectors, cfg.exp4.train_fraction, cfg.exp4.split_seed)
        if a.plumbing_check:
            res["NOTICE"] = "PLUMBING CHECK ONLY - not a result; tiny n; selectors untrained/meaningless at this scale"
        from pathlib import Path

        out = Path(a.source_run) / ("exp4_plumbing_check.json" if a.plumbing_check else "exp4_selectors.json")
        if out.exists():
            print(f"refusing to overwrite {out}", file=sys.stderr)
            return 3
        out.write_text(json.dumps(res, indent=2, default=str))
        print(out)
        return 0

    if a.cmd == "questions":
        from pathlib import Path

        from .config import repo_path
        from .data.question_sets import freeze, load_excluded

        spec = yaml.safe_load(open(a.spec))
        out = repo_path(a.out)
        if out.exists():
            print(f"refusing to overwrite frozen question set {out}", file=sys.stderr)
            return 3
        res = freeze(spec["datasets"], spec["seed"], load_excluded(spec.get("excluded")), spec.get("split", "dev"))
        res["spec"] = spec
        res["spec_file"] = a.spec
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(res, indent=2))
        from .hashing import file_sha256

        print(json.dumps({"out": str(out), "sha256": file_sha256(out), **{k: v["n_selected"] for k, v in res["details"].items()}}))
        return 0

    if a.cmd == "annotations":
        from .annotations import export_package, import_completed, select_for_verification, write_verified

        if a.action == "export":
            from .data.loaders import sample_questions

            frozen = json.loads(open(a.questions).read())
            quotas = {k: int(v) for k, v in (x.split("=") for x in a.quotas.split(","))}
            pool = {ds: sample_questions(ds, frozen["split"], len(frozen["datasets"][ds]), 0, frozen["datasets"][ds])
                    for ds in quotas}
            strat = {ds: frozen["details"][ds]["stratify_by"] or "question_type" for ds in quotas}
            chosen = select_for_verification(pool, quotas, a.seed, strat)
            from .hashing import file_sha256

            man = export_package(chosen, a.out, {"source_question_set": a.questions,
                                                 "source_question_set_sha256": file_sha256(a.questions),
                                                 "quotas": quotas, "seed": a.seed, "balanced_by": strat,
                                                 "also_balanced_by": "edge category (has_fallback / exact_only / no_edges)"})
            print(json.dumps({k: man[k] for k in ("n_questions", "n_edges", "n_claim_items", "by_dataset", "edges_by_stratum")}))
            return 0
        res = import_completed(a.package, a.completed)
        write_verified(res, a.out)
        print(json.dumps(res["report"], indent=2))
        return 0

    if a.cmd == "preflight":
        from .preflight import run_preflight

        rep = run_preflight(a.config, a.authorized_compute, a.tiny_generation)
        print(json.dumps(rep, indent=2, default=str))
        return 0 if rep["ok"] else 1

    if a.cmd == "report":
        from pathlib import Path

        from .evaluation.reporting import write_reports

        class _Ctx:
            dir = Path(a.run_dir)

        write_reports(_Ctx())
        print(Path(a.run_dir) / "report.md")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
