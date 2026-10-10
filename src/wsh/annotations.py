"""Human verification of derived reasoning structure.

export  -> annotations/<name>/: package.jsonl (machine reference), review.md (readable),
           paths.csv / edges.csv / claims.csv (blank verification fields), GUIDE.md, MANIFEST.json
import  -> validates the completed CSVs against the package AND the current dataset files
           (question digest), refuses on any error, and writes verified.jsonl
overlay -> ``apply_verified`` replaces a gold bundle's derived DEPENDS_ON edges / path with the
           human-verified ones (status HUMAN_VERIFIED, stratum A). Benchmark answers are never
           modified; an annotator's "answer incorrect" judgement is recorded, not applied.

Verification fields are never filled by code. A question counts as verified only when its
path row and every one of its edge rows carry a definite (non-'uncertain') verdict.
"""

from __future__ import annotations

import csv
import json
import random
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from .data.schemas import AnnotationStatus, Edge, EvidenceBundle, PathStep, Question, RelationType
from .hashing import file_sha256, stable_hash

PACKAGE_VERSION = "verification-v1"

PATH_COLS = ["uid", "dataset", "qid", "hop_count", "question_type", "question", "gold_answers",
             "proposed_passage_order", "proposed_step_titles", "annotator", "answer_correct", "path_verdict",
             "corrected_passage_order", "missing_edges", "notes"]
EDGE_COLS = ["edge_id", "uid", "source_claim_id", "source_text", "target_claim_id", "target_text", "relation",
             "anchor", "anchor_match", "derivation_method", "stratum", "annotator", "verdict",
             "corrected_source_claim_id", "corrected_target_claim_id", "notes"]
CLAIM_COLS = ["item_id", "uid", "claim_id", "source_sentence_id", "source_sentence_text", "claim_text",
              "extraction_method", "why_listed", "annotator", "faithful", "self_contained", "notes"]
HUMAN_FIELDS = {"paths": ["annotator", "answer_correct", "path_verdict", "corrected_passage_order", "missing_edges", "notes"],
                "edges": ["annotator", "verdict", "corrected_source_claim_id", "corrected_target_claim_id", "notes"],
                "claims": ["annotator", "faithful", "self_contained", "notes"]}
VOCAB = {"answer_correct": {"yes", "no", "uncertain"},
         "path_verdict": {"correct", "incorrect", "uncertain"},
         "verdict": {"correct", "wrong_endpoint", "wrong_direction", "not_a_dependency", "uncertain"},
         "faithful": {"yes", "partial", "no", "uncertain"},
         "self_contained": {"yes", "no", "uncertain"}}


class AnnotationImportError(ValueError):
    def __init__(self, errors: list[str]):
        super().__init__(f"{len(errors)} validation error(s); first: {errors[0] if errors else ''}")
        self.errors = errors


def question_digest(q: Question) -> str:
    """Links an annotation to the exact dataset content it was made on."""
    gold = set(q.gold_passage_ids())
    return stable_hash([q.uid, q.question, q.answers, [(p.passage_id, p.title, p.text) for p in q.passages
                                                       if p.passage_id in gold]])


# --------------------------------------------------------------------------- export

def select_for_verification(questions: dict[str, list[Question]], quotas: dict[str, int], seed: int,
                            strat: dict[str, str]) -> list[Question]:
    """Seeded selection balancing strata (hop count / question type) and edge-derivation
    category (questions with vs without fallback-anchored edges)."""
    from .representations.evidence import gold_bundle

    out: list[Question] = []
    for ds, n in quotas.items():
        groups: dict[tuple, list[Question]] = defaultdict(list)
        for q in questions.get(ds, []):
            b = gold_bundle(q)
            cat = "has_fallback" if any(e.meta.get("anchor_match") == "fallback" for e in b.edges) else \
                ("exact_only" if b.edges else "no_edges")
            groups[(str(getattr(q, strat[ds])), cat)].append(q)
        rng = random.Random(seed)
        keys = sorted(groups)
        for k in keys:
            rng.shuffle(groups[k])
        picked: list[Question] = []
        while len(picked) < n and any(groups[k] for k in keys):
            for k in keys:
                if groups[k] and len(picked) < n:
                    picked.append(groups[k].pop(0))
        out += picked
    return out


def _package_record(q: Question) -> dict[str, Any]:
    from .data.provenance import gold_units
    from .extraction.claim_extractor import RuleAtomicExtractor
    from .representations.evidence import gold_bundle
    from .representations.protocols import _context_dependent, edge_stratum

    b = gold_bundle(q)
    gold_p = [b.passages[p] for p in b.passage_order]
    atomic, _ = RuleAtomicExtractor().extract(gold_p, gold_units(q))
    cm = b.claim_map()
    steps = []
    for st in q.reasoning_steps:
        steps.append({"index": st.index, "passage_ids": st.passage_ids,
                      "titles": [q.passage(p).title for p in st.passage_ids], "sub_question": st.sub_question,
                      "sub_answer": st.sub_answer, "depends_on": st.depends_on,
                      "supporting_sentence_indices": st.sentence_indices})
    edges = [{"edge_id": f"{q.uid}#e{k}", "source": e.source, "target": e.target, "relation": e.relation.value,
              "source_text": cm[e.source].text, "target_text": cm[e.target].text, "method": e.method,
              "status": e.status.value, "anchor": e.meta.get("anchor"), "anchor_match": e.meta.get("anchor_match"),
              "steps": e.meta.get("steps"), "stratum": edge_stratum(e)} for k, e in enumerate(b.edges)]
    derived = [{"claim_id": c.claim_id, "source_sentence_id": c.derived_from or c.claim_id.split(".a")[0],
                "text": c.text, "spans": [s.model_dump() for s in c.spans], "method": c.extraction_method}
               for c in atomic if c.claim_id not in cm]
    return {
        "package_version": PACKAGE_VERSION, "uid": q.uid, "qid": q.qid, "dataset": q.dataset, "split": q.split,
        "question": q.question, "answers": q.answers, "question_type": q.question_type, "hop_count": q.hop_count,
        "question_digest": question_digest(q), "source": q.source.model_dump(),
        "annotation_status": {k: v.value for k, v in q.annotations.items()}, "annotation_notes": q.annotation_notes,
        "passages": [{"passage_id": p.passage_id, "title": p.title, "text": p.text} for p in gold_p],
        "claims": [{"claim_id": c.claim_id, "passage_id": c.passage_id, "text": c.text,
                    "span": c.spans[0].model_dump(), "is_gold_support": c.is_gold_support,
                    "context_dependent": _context_dependent(c.text), "extraction_method": c.extraction_method}
                   for c in b.claims],
        "derived_claims": derived,
        "reasoning_steps": steps,
        "proposed_path": [{"label": st.label, "claim_ids": st.claim_ids} for st in (b.path or [])],
        "path_status": b.path_status.value,
        "proposed_passage_order": [p for st in q.reasoning_steps for p in st.passage_ids],
        "edges": edges,
    }


def export_package(questions: list[Question], out_dir: str | Path, selection_meta: dict) -> dict:
    out = Path(out_dir)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f"{out} is not empty; refusing to overwrite an annotation package")
    out.mkdir(parents=True, exist_ok=True)
    recs = [_package_record(q) for q in questions]
    with open(out / "package.jsonl", "w") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    _write_csv(out / "paths.csv", PATH_COLS, [{
        "uid": r["uid"], "dataset": r["dataset"], "qid": r["qid"], "hop_count": r["hop_count"],
        "question_type": r["question_type"], "question": r["question"], "gold_answers": " | ".join(r["answers"]),
        "proposed_passage_order": ";".join(r["proposed_passage_order"]),
        "proposed_step_titles": " -> ".join("/".join(s["titles"]) for s in r["reasoning_steps"])} for r in recs])
    _write_csv(out / "edges.csv", EDGE_COLS, [{
        "edge_id": e["edge_id"], "uid": r["uid"], "source_claim_id": e["source"], "source_text": e["source_text"],
        "target_claim_id": e["target"], "target_text": e["target_text"], "relation": e["relation"],
        "anchor": e["anchor"], "anchor_match": e["anchor_match"], "derivation_method": e["method"],
        "stratum": e["stratum"]} for r in recs for e in r["edges"]])
    claim_rows = []
    for r in recs:
        sent = {c["claim_id"]: c for c in r["claims"]}
        for d in r["derived_claims"]:
            claim_rows.append({"item_id": f"{r['uid']}#c{len(claim_rows)}", "uid": r["uid"], "claim_id": d["claim_id"],
                               "source_sentence_id": d["source_sentence_id"],
                               "source_sentence_text": sent.get(d["source_sentence_id"], {}).get("text", ""),
                               "claim_text": d["text"], "extraction_method": d["method"], "why_listed": "derived_claim"})
        for c in r["claims"]:
            if c["context_dependent"] and c["is_gold_support"]:
                claim_rows.append({"item_id": f"{r['uid']}#c{len(claim_rows)}", "uid": r["uid"], "claim_id": c["claim_id"],
                                   "source_sentence_id": c["claim_id"], "source_sentence_text": c["text"],
                                   "claim_text": c["text"], "extraction_method": c["extraction_method"],
                                   "why_listed": "context_dependent_supporting_sentence"})
    _write_csv(out / "claims.csv", CLAIM_COLS, claim_rows)
    (out / "review.md").write_text(_review_markdown(recs))
    manifest = {"package_version": PACKAGE_VERSION, "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "n_questions": len(recs), "n_edges": sum(len(r["edges"]) for r in recs), "n_claim_items": len(claim_rows),
                "by_dataset": {d: sum(r["dataset"] == d for r in recs) for d in sorted({r["dataset"] for r in recs})},
                "edges_by_stratum": _count(e["stratum"] for r in recs for e in r["edges"]),
                "selection": selection_meta,
                "files_sha256": {f: file_sha256(out / f) for f in ("package.jsonl", "paths.csv", "edges.csv", "claims.csv")},
                "note": "Verification fields are blank by construction. This package is for verifying annotations, "
                        "not for statistical conclusions."}
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def _count(xs) -> dict[str, int]:
    c: dict[str, int] = {}
    for x in xs:
        c[x] = c.get(x, 0) + 1
    return dict(sorted(c.items()))


def _write_csv(path: Path, cols: list[str], rows: list[dict]) -> None:
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") if r.get(c) is not None else "" for c in cols})


def _review_markdown(recs: list[dict]) -> str:
    L = ["# Verification package - readable view", "",
         "One section per question. Fill the CSV files, not this file. See GUIDE.md.", ""]
    for r in recs:
        L += [f"## {r['uid']}  ({r['dataset']}, {r['question_type']}, hops={r['hop_count']})", "",
              f"**Question:** {r['question']}  ", f"**Gold answer(s):** {' | '.join(r['answers'])}", ""]
        for p in r["passages"]:
            L.append(f"**Passage `{p['passage_id']}` - {p['title']}**")
            for c in (c for c in r["claims"] if c["passage_id"] == p["passage_id"]):
                mark = " *(gold support)*" if c["is_gold_support"] else ""
                L.append(f"- `{c['claim_id'].split('#')[-1]}` {c['text']}{mark}")
            L.append("")
        L.append("**Proposed reasoning steps (dataset order):**")
        for s in r["reasoning_steps"]:
            sub = f" - sub-question: {s['sub_question']}" if s["sub_question"] else ""
            L.append(f"{s['index'] + 1}. {'/'.join(s['titles'])}{sub} -> sub-answer: {s['sub_answer']}; "
                     f"depends on steps {[d + 1 for d in s['depends_on']]}")
        L += ["", "**Proposed dependency edges:**"]
        for e in r["edges"] or []:
            L.append(f"- `{e['edge_id'].split('#')[-1]}` [{e['stratum']}, anchor '{e['anchor']}' {e['anchor_match']}]  "
                     f"`{e['source'].split('#')[-1]}` \"{e['source_text']}\"  DEPENDS_ON  "
                     f"`{e['target'].split('#')[-1]}` \"{e['target_text']}\"")
        if not r["edges"]:
            L.append("- (none proposed)")
        L += ["", "---", ""]
    return "\n".join(L)


# --------------------------------------------------------------------------- import

def _read_csv(path: Path, cols: list[str], errors: list[str]) -> list[dict]:
    with open(path, newline="") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != cols:
            errors.append(f"{path.name}: columns changed (expected {cols})")
            return []
        return [{k: (v or "").strip() for k, v in row.items()} for row in rd]


def import_completed(package_dir: str | Path, completed_dir: str | Path | None = None,
                     questions: dict[str, Question] | None = None) -> dict[str, Any]:
    """Validate completed CSVs; return {"verified": [...], "report": {...}}. Raises
    AnnotationImportError listing every problem; nothing is returned partially on error.

    ``questions`` (uid -> Question) links annotations to the original dataset; when omitted
    they are loaded from the dataset files by qid."""
    pkg_dir = Path(package_dir)
    done = Path(completed_dir) if completed_dir else pkg_dir
    pkg = {r["uid"]: r for r in map(json.loads, (pkg_dir / "package.jsonl").read_text().splitlines())}
    errors: list[str] = []
    paths = _read_csv(done / "paths.csv", PATH_COLS, errors)
    edges = _read_csv(done / "edges.csv", EDGE_COLS, errors)
    claims = _read_csv(done / "claims.csv", CLAIM_COLS, errors)
    if errors:
        raise AnnotationImportError(errors)
    pkg_edges = {e["edge_id"]: (uid, e) for uid, r in pkg.items() for e in r["edges"]}
    if questions is None:
        questions = _load_questions_for(pkg)

    def check_vocab(row, field, where):
        v = row[field]
        if v and v not in VOCAB[field]:
            errors.append(f"{where}: {field}={v!r} not in {sorted(VOCAB[field])}")

    def check_annotator(row, kind, where):
        if any(row[f] for f in HUMAN_FIELDS[kind] if f != "annotator") and not row["annotator"]:
            errors.append(f"{where}: filled without an annotator id")

    edges_by_q: dict[str, list[dict]] = defaultdict(list)
    for row in edges:
        where = f"edges.csv {row['edge_id']}"
        if row["edge_id"] not in pkg_edges:
            errors.append(f"{where}: unknown edge id")
            continue
        uid, e = pkg_edges[row["edge_id"]]
        if row["uid"] != uid or row["source_claim_id"] != e["source"] or row["target_claim_id"] != e["target"]:
            errors.append(f"{where}: proposed (read-only) columns were edited")
        check_vocab(row, "verdict", where)
        check_annotator(row, "edges", where)
        cids = {c["claim_id"] for c in pkg[uid]["claims"]}
        if row["verdict"] == "wrong_endpoint":
            for f in ("corrected_source_claim_id", "corrected_target_claim_id"):
                if row[f] and row[f] not in cids:
                    errors.append(f"{where}: {f}={row[f]!r} is not a claim of {uid}")
            if not (row["corrected_source_claim_id"] or row["corrected_target_claim_id"]):
                errors.append(f"{where}: wrong_endpoint needs a corrected source and/or target claim id")
        elif row["corrected_source_claim_id"] or row["corrected_target_claim_id"]:
            errors.append(f"{where}: corrections given but verdict is {row['verdict']!r}")
        edges_by_q[uid].append(row)
    path_rows: dict[str, dict] = {}
    for row in paths:
        where = f"paths.csv {row['uid']}"
        if row["uid"] not in pkg:
            errors.append(f"{where}: unknown question")
            continue
        r = pkg[row["uid"]]
        if row["proposed_passage_order"] != ";".join(r["proposed_passage_order"]):
            errors.append(f"{where}: proposed (read-only) columns were edited")
        for f in ("answer_correct", "path_verdict"):
            check_vocab(row, f, where)
        check_annotator(row, "paths", where)
        if row["path_verdict"] == "incorrect":
            order = [x for x in row["corrected_passage_order"].split(";") if x]
            if sorted(order) != sorted(set(r["proposed_passage_order"])) or len(order) != len(set(order)):
                errors.append(f"{where}: corrected_passage_order must be a permutation of {r['proposed_passage_order']}")
        elif row["corrected_passage_order"]:
            errors.append(f"{where}: corrected order given but path_verdict is {row['path_verdict']!r}")
        cids = {c["claim_id"] for c in r["claims"]}
        for pair in filter(None, row["missing_edges"].split(";")):
            s, _, t = pair.partition(">")
            if s not in cids or t not in cids or s == t:
                errors.append(f"{where}: missing_edges entry {pair!r} must be '<claim id>><claim id>' within {row['uid']}")
        path_rows[row["uid"]] = row
    claim_rows: dict[str, list[dict]] = defaultdict(list)
    for row in claims:
        where = f"claims.csv {row['item_id']}"
        if row["uid"] not in pkg:
            errors.append(f"{where}: unknown question")
            continue
        for f in ("faithful", "self_contained"):
            check_vocab(row, f, where)
        check_annotator(row, "claims", where)
        claim_rows[row["uid"]].append(row)
    for uid, r in pkg.items():
        q = questions.get(uid)
        if q is None:
            errors.append(f"{uid}: not found in the current dataset files")
        elif question_digest(q) != r["question_digest"]:
            errors.append(f"{uid}: dataset content changed since the package was exported (digest mismatch)")
    if errors:
        raise AnnotationImportError(errors)

    verified, incomplete, uncertain = [], [], []
    for uid, r in pkg.items():
        prow = path_rows.get(uid)
        erows = edges_by_q.get(uid, [])
        if not prow or not prow["path_verdict"] or len(erows) != len(r["edges"]) or any(not e["verdict"] for e in erows):
            incomplete.append(uid)
            continue
        if prow["path_verdict"] == "uncertain" or any(e["verdict"] == "uncertain" for e in erows):
            uncertain.append(uid)
            continue
        kept, rejected = [], []
        for row in erows:
            _, e = pkg_edges[row["edge_id"]]
            if row["verdict"] == "correct":
                kept.append({"source": e["source"], "target": e["target"], "origin": row["edge_id"], "correction": None})
            elif row["verdict"] == "wrong_direction":
                kept.append({"source": e["target"], "target": e["source"], "origin": row["edge_id"], "correction": "reversed"})
            elif row["verdict"] == "wrong_endpoint":
                kept.append({"source": row["corrected_source_claim_id"] or e["source"],
                             "target": row["corrected_target_claim_id"] or e["target"], "origin": row["edge_id"],
                             "correction": "endpoint"})
            else:
                rejected.append(row["edge_id"])
        for pair in filter(None, prow["missing_edges"].split(";")):
            s, _, t = pair.partition(">")
            kept.append({"source": s, "target": t, "origin": "added_by_annotator", "correction": "added"})
        order = ([x for x in prow["corrected_passage_order"].split(";") if x] if prow["path_verdict"] == "incorrect"
                 else r["proposed_passage_order"])
        verified.append({
            "package_version": r["package_version"], "uid": uid, "dataset": r["dataset"], "qid": r["qid"],
            "question_digest": r["question_digest"],
            "annotators": sorted({x["annotator"] for x in [prow, *erows, *claim_rows.get(uid, [])] if x["annotator"]}),
            "answer_correct": prow["answer_correct"] or None,
            "path": {"passage_order": order, "corrected": prow["path_verdict"] == "incorrect"},
            "edges": kept, "rejected_edges": rejected,
            "claims": {c["claim_id"]: {"faithful": c["faithful"] or None, "self_contained": c["self_contained"] or None,
                                       "why_listed": c["why_listed"]} for c in claim_rows.get(uid, [])},
            "notes": prow["notes"] or None,
        })
    report = {"n_package_questions": len(pkg), "n_verified": len(verified), "incomplete": incomplete,
              "uncertain": uncertain, "n_edges_kept": sum(len(v["edges"]) for v in verified),
              "n_edges_rejected": sum(len(v["rejected_edges"]) for v in verified),
              "n_paths_corrected": sum(v["path"]["corrected"] for v in verified)}
    return {"verified": verified, "report": report}


def _load_questions_for(pkg: dict[str, dict]) -> dict[str, Question]:
    from .data.loaders import sample_questions

    by_ds: dict[str, list[str]] = defaultdict(list)
    for r in pkg.values():
        by_ds[r["dataset"]].append(r["qid"])
    out = {}
    for ds, qids in by_ds.items():
        split = next(r["split"] for r in pkg.values() if r["dataset"] == ds)
        for q in sample_questions(ds, split, len(qids), 0, qids):
            out[q.uid] = q
    return out


def write_verified(result: dict, out_path: str | Path) -> None:
    out = Path(out_path)
    if out.exists():
        raise FileExistsError(f"{out} exists; verified annotations are never overwritten (use a new file name)")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        for v in result["verified"]:
            f.write(json.dumps(v, ensure_ascii=False) + "\n")
    out.with_suffix(".report.json").write_text(json.dumps(result["report"], indent=2))


# --------------------------------------------------------------------------- overlay

def load_verified(path: str | Path | None) -> dict[str, dict]:
    if not path:
        return {}
    return {v["uid"]: v for v in map(json.loads, Path(path).read_text().splitlines()) if v}


def apply_verified(q: Question, b: EvidenceBundle, rec: dict | None) -> None:
    """Replace derived structure with human-verified structure (in place)."""
    if rec is None:
        return
    if rec["question_digest"] != question_digest(q):
        raise ValueError(f"{q.uid}: verified annotation was made on different dataset content")
    cm = b.claim_map()
    b.edges = [e for e in b.edges if e.relation != RelationType.DEPENDS_ON]
    skipped = 0
    for v in rec["edges"]:
        if v["source"] in cm and v["target"] in cm:
            b.edges.append(Edge(source=v["source"], target=v["target"], relation=RelationType.DEPENDS_ON,
                                status=AnnotationStatus.HUMAN_VERIFIED, method=f"human:{rec['package_version']}",
                                meta={"origin": v["origin"], "correction": v["correction"]}))
        else:
            skipped += 1  # endpoint outside this bundle's scope (e.g. gold_sentences scope)
    order = rec["path"]["passage_order"]
    pos = {c.claim_id: i for i, c in enumerate(b.claims)}
    steps = []
    for k, pid in enumerate(dict.fromkeys(order)):
        cs = sorted((c.claim_id for c in b.claims if c.passage_id == pid), key=pos.get)
        if cs:
            steps.append(PathStep(claim_ids=cs, label=f"Step {k + 1}"))
    rest = [c.claim_id for c in b.claims if c.passage_id not in set(order)]
    if rest:
        steps.append(PathStep(claim_ids=rest, label="Other evidence"))
    b.path, b.path_status = steps or None, AnnotationStatus.HUMAN_VERIFIED
    b.origin = {**b.origin, "verified_annotations": rec["package_version"], "verified_edges_skipped": skipped,
                "human_answer_check": rec.get("answer_correct")}
