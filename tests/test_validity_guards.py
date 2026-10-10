"""Automated guards against leakage and invalid comparisons (docs/METHODOLOGICAL_AUDIT.md)."""

import csv
import json
import re

import pytest

from conftest import data_available
from wsh import interventions
from wsh.annotations import (AnnotationImportError, apply_verified, export_package, import_completed,
                             question_digest, write_verified)
from wsh.config import load_config
from wsh.data.question_sets import ExcludedQuestionError, assert_no_excluded, load_excluded
from wsh.data.schemas import AnnotationStatus, Passage
from wsh.evaluation.evaluator import evaluate
from wsh.evaluation.reporting import consistency
from wsh.evaluation.statistics import by_question, paired_bootstrap
from wsh.experiments.common import UnfrozenQuestionSetError, make_layout, require_frozen_questions
from wsh.experiments.exp3_component_analysis import depends_on_prf
from wsh.models.local_generator import generation_cache_key
from wsh.models.prompts import _QA, _VERIFY, PromptCompositionError, assert_prompt_composition, build_request
from wsh.representations.evidence import gold_bundle
from wsh.representations.protocols import bundle_edge_stratum
from wsh.representations.serialization import render
from wsh.text import contains_phrase

REPS = ["R0", "R1", "R2", "R3", "R4", "R5"]


# --- the model never receives gold answers / annotations outside the evidence block ---

def test_prompt_is_template_plus_evidence_plus_question(toy_question):
    ser = render(make_layout("R4", gold_bundle(toy_question)))
    req = build_request(toy_question, ser.text, 48)
    assert_prompt_composition(toy_question, req, ser.text)
    rest = req.system + req.user.replace(ser.text, "").replace(toy_question.question, "") + req.prefill
    assert not any(contains_phrase(rest, a) for a in toy_question.answers)
    tampered = req.model_copy(update={"user": req.user + "\nHint: Larry Page"}) if hasattr(req, "model_copy") else None
    if tampered is None:
        import dataclasses
        tampered = dataclasses.replace(req, user=req.user + "\nHint: Larry Page")
    with pytest.raises(PromptCompositionError):
        assert_prompt_composition(toy_question, tampered, ser.text)


def test_templates_contain_no_dataset_content():
    for t in (_QA, _VERIFY):
        assert set(re.findall(r"{(\w+)}", t)) <= {"evidence", "question", "labels"}


_LINE = re.compile(r"^\[(E\d+)\] (?:\(source: (.+?)\) )?(.*)$")


@pytest.mark.parametrize("rep", REPS)
def test_rendered_evidence_has_only_facts_and_structure(toy_question, rep):
    """Every rendered line is a fact line whose ID maps to exactly that text, or a structural
    line; no sub-question, sub-answer, gold flag or annotation text can appear."""
    b = gold_bundle(toy_question)
    ser = render(make_layout(rep, b, 3))
    cm = b.claim_map()
    for ln in ser.text.splitlines():
        m = _LINE.match(ln)
        if m:
            did, title, text = m.groups()
            item = ser.id_map[did]
            assert text == " ".join(cm[c].text for c in item["claim_ids"])  # citation ID -> source mapping
            assert title in (None, *(b.passages[p].title for p in item["passage_ids"]))
        else:
            assert re.fullmatch(r"Step \d+:|Other evidence:|Relations:|E\d+ [A-Z_]+ E\d+|Unresolved conflicts:", ln), ln


# --- gold vs predicted structure are never mixed ---

def test_gold_and_predicted_edges_are_separate(toy_question):
    b = gold_bundle(toy_question)
    assert all(e.status != AnnotationStatus.MODEL_PREDICTED for e in b.edges)
    assert bundle_edge_stratum(b) == "B_derived_exact_anchor"


def test_c2_agreement_suppressed_when_gold_shares_the_heuristic(toy_question):
    b = gold_bundle(toy_question)
    cp = {c.claim_id: c.passage_id for c in b.claims}
    assert depends_on_prf(b.edges, b.edges, cp, "hotpotqa")["dep_precision"] is None
    assert depends_on_prf(b.edges, b.edges, cp, "musique")["dep_precision"] == 1.0
    hv = [e.model_copy(update={"status": AnnotationStatus.HUMAN_VERIFIED}) for e in b.edges]
    assert depends_on_prf(b.edges, hv, cp, "hotpotqa")["dep_gold_circularity"] == "none:human_verified"


# --- question-set boundaries ---

def test_excluded_questions_refused_outside_smoke(toy_question):
    ex = {toy_question.uid: "smoke"}
    assert_no_excluded({"toy": [toy_question]}, ex, "smoke")
    with pytest.raises(ExcludedQuestionError):
        assert_no_excluded({"toy": [toy_question]}, ex, "pilot")


def test_pilot_must_use_frozen_questions(tmp_path):
    raw = load_config("configs/pilot.yaml")
    require_frozen_questions(raw)  # frozen file -> fine
    loose = raw.model_copy(update={"datasets": [raw.datasets[0].model_copy(update={"qids": None, "qids_file": None})]})
    with pytest.raises(UnfrozenQuestionSetError):
        require_frozen_questions(loose)


def test_frozen_pilot_set_excludes_smoke_questions():
    frozen = json.loads(open("configs/question_sets/pilot_v1.json").read())
    excluded = load_excluded("configs/excluded_questions.json")
    assert excluded and all(k.split("/", 1)[0] in frozen["datasets"] for k in excluded)
    pilot = {f"{ds}/{q}" for ds, qs in frozen["datasets"].items() for q in qs}
    assert not pilot & set(excluded)
    smoke = load_config("configs/smoke.yaml")
    assert all(d.split == "dev" for d in smoke.datasets + load_config("configs/pilot.yaml").datasets)


# --- metrics: answering vs correctness, citations ---

def test_abstention_is_unanswered_not_wrong(toy_question):
    b = gold_bundle(toy_question)
    ser = render(make_layout("R1", b))
    ab = evaluate(toy_question, "Answer: insufficient evidence", "eos", ser, b)
    wr = evaluate(toy_question, "Answer: Paris\nEvidence: E1", "eos", ser, b)
    assert ab["failure"]["primary"] == "abstained" and not ab["failure"]["answered"] and ab["eval"]["em"] == 0.0
    assert wr["failure"]["primary"] == "wrong_answer" and wr["failure"]["answered"]


@pytest.mark.parametrize("out,status,flag", [
    ("Answer: Larry Page", "none_given", "missing_citation"),
    ("Answer: Larry Page\nEvidence: E1", "all_valid", None),
    ("Answer: Larry Page\nEvidence: E1, E99", "some_invalid", "invalid_citation"),
    ("Answer: Larry Page\nEvidence: E99", "all_invalid", "invalid_citation"),
])
def test_missing_and_invalid_citations_are_separate(toy_question, out, status, flag):
    b = gold_bundle(toy_question)
    r = evaluate(toy_question, out, "eos", render(make_layout("R1", b)), b)
    assert r["eval"]["citation_status"] == status and r["eval"]["em"] == 1.0
    assert (flag in r["failure"]["flags"]) if flag else not ({"missing_citation", "invalid_citation"} & set(r["failure"]["flags"]))


def test_em_f1_edge_cases():
    from wsh.evaluation.answer_metrics import exact_match, token_f1

    assert exact_match("the  Beatles!", ["Beatles"]) == 1.0
    assert exact_match("Beatles", ["The Rolling Stones", "the beatles"]) == 1.0  # max over aliases
    assert token_f1("Paul McCartney", ["John Lennon"]) == 0.0
    assert abs(token_f1("John Winston Lennon", ["John Lennon"]) - 0.8) < 1e-9  # P=2/3, R=1


# --- statistics: same questions, question-level resampling ---

def test_paired_uses_only_shared_questions():
    a = {"q1": 1.0, "q2": 0.0, "q3": 1.0}
    b = {"q2": 1.0, "q3": 1.0, "q4": 0.0}
    r = paired_bootstrap(a, b)
    assert r["n_paired"] == 2 and r["n_only_a"] == 1 and r["n_only_b"] == 1 and r["delta"] == 0.5


def test_bootstrap_unit_is_the_question():
    recs = [{"question_uid": "q1", "v": 1.0}] * 5 + [{"question_uid": "q2", "v": 0.0}]
    m = by_question(recs, lambda r: r["v"])
    assert m == {"q1": 1.0, "q2": 0.0}  # five records of q1 count once


# --- caching and generator settings ---

def test_cache_key_covers_everything_that_changes_outputs():
    base = dict(model_id="m", revision="r", prompt="p", max_new_tokens=8,
                decoding={"do_sample": False, "dtype": "float32", "device": "cpu"})
    k0 = generation_cache_key(**base)
    for change in ({"model_id": "m2"}, {"revision": "r2"}, {"prompt": "p2"}, {"max_new_tokens": 9},
                   {"decoding": {**base["decoding"], "device": "cuda"}},
                   {"decoding": {**base["decoding"], "dtype": "bfloat16"}}):
        assert generation_cache_key(**{**base, **change}) != k0


def test_consistency_flags_mixed_generator_settings():
    r = lambda dev: {"model_id": "m", "model_revision": "r", "prompt_version": "qa-v2",  # noqa: E731
                     "generation": {"decoding": {"device": dev}}}
    assert consistency([r("cpu"), r("cpu")])["generator_settings_identical"]
    assert not consistency([r("cpu"), r("cuda")])["generator_settings_identical"]


# --- interventions ---

@pytest.mark.parametrize("name,params", [("P1", {}), ("P2", {}), ("P3", {}), ("P4", {}), ("P5", {"mode": "strip"}),
                                         ("P6", {"op": "negation"}), ("P6", {"op": "entity"}), ("P7", {})])
def test_every_intervention_declares_label_effect(toy_question, name, params):
    out, rec = interventions.apply(name, gold_bundle(toy_question), toy_question, 0.4, 0, params)
    assert rec.label_effect in interventions.LABEL_EFFECTS
    assert isinstance(rec.answer_introduced, bool)


def test_p4_never_injects_answer_evidence(toy_question):
    q = toy_question.model_copy(deep=True)
    # make the only non-gold passage state the answer: it must not be used as a distractor
    paris = next(p for p in q.passages if p.title == "Paris")
    txt = "Larry Page visited Paris. Paris is the capital of France."
    q.passages[q.passages.index(paris)] = Passage(**{**paris.model_dump(), "text": txt,
                                                      "sentence_spans": [(0, 25), (26, len(txt))]})
    out, rec = interventions.apply("P4", gold_bundle(q), q, 0.4, 0, {"mode": "hard"})
    assert all("Larry Page" not in c.text for c in out.claims if c.is_distractor)
    assert rec.changes[0]["excluded_answer_bearing_candidates"] >= 1 and not rec.answer_introduced


# --- human verification package ---

def _fill(path, cols_values):
    rows = list(csv.DictReader(open(path)))
    for r in rows:
        r.update(cols_values(r))
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        w.writeheader()
        w.writerows(rows)


def test_annotation_roundtrip_and_validation(tmp_path, toy_question):
    pkg = tmp_path / "pkg"
    man = export_package([toy_question], pkg, {"test": True})
    assert man["n_questions"] == 1 and man["n_edges"] == 1
    for f in ("paths.csv", "edges.csv"):  # exported blank
        assert all(not r["annotator"] and not (r.get("verdict") or r.get("path_verdict")) for r in csv.DictReader(open(pkg / f)))
    qs = {toy_question.uid: toy_question}
    assert import_completed(pkg, questions=qs)["report"]["incomplete"] == [toy_question.uid]  # blank => nothing verified
    # simulated annotator (test only)
    _fill(pkg / "edges.csv", lambda r: {"annotator": "t1", "verdict": "wrong_direction"})
    _fill(pkg / "paths.csv", lambda r: {"annotator": "t1", "path_verdict": "correct", "answer_correct": "yes"})
    res = import_completed(pkg, questions=qs)
    assert res["report"]["n_verified"] == 1
    v = res["verified"][0]
    assert v["edges"][0]["correction"] == "reversed" and v["question_digest"] == question_digest(toy_question)
    b = gold_bundle(toy_question)
    apply_verified(toy_question, b, v)
    assert b.path_status == AnnotationStatus.HUMAN_VERIFIED and bundle_edge_stratum(b) == "A_human_verified"
    assert toy_question.answers == ["Larry Page and Sergey Brin", "Larry Page"]  # labels never modified
    write_verified(res, tmp_path / "v.jsonl")
    with pytest.raises(FileExistsError):
        write_verified(res, tmp_path / "v.jsonl")
    # invalid completions are rejected with every error listed
    _fill(pkg / "edges.csv", lambda r: {"annotator": "", "verdict": "maybe", "corrected_source_claim_id": "nope"})
    with pytest.raises(AnnotationImportError) as e:
        import_completed(pkg, questions=qs)
    assert len(e.value.errors) >= 2
    # changed dataset content is detected
    _fill(pkg / "edges.csv", lambda r: {"annotator": "t1", "verdict": "correct", "corrected_source_claim_id": ""})
    other = toy_question.model_copy(update={"question": "changed?"})
    with pytest.raises(AnnotationImportError):
        import_completed(pkg, questions={toy_question.uid: other})


def test_export_refuses_to_overwrite(tmp_path, toy_question):
    export_package([toy_question], tmp_path / "p", {})
    with pytest.raises(FileExistsError):
        export_package([toy_question], tmp_path / "p", {})


@pytest.mark.skipif(not data_available("musique"), reason="dataset not downloaded")
def test_shipped_annotation_package_is_blank_and_linked():
    import pathlib

    pkg = pathlib.Path("annotations/verification_v1")
    if not pkg.exists():
        pytest.skip("package not exported")
    for f, field in (("paths.csv", "path_verdict"), ("edges.csv", "verdict"), ("claims.csv", "faithful")):
        assert all(not r[field] and not r["annotator"] for r in csv.DictReader(open(pkg / f)))
    rep = import_completed(pkg)["report"]  # links every question to the current dataset files
    assert rep["n_verified"] == 0 and len(rep["incomplete"]) == rep["n_package_questions"]


@pytest.mark.skipif(not data_available("musique"), reason="dataset not downloaded")
def test_preflight_reports_every_check_without_running_experiments(tmp_path, monkeypatch):
    from wsh.models.policy import is_cached
    from wsh.preflight import run_preflight

    if not is_cached("Qwen/Qwen2.5-0.5B-Instruct", load_config("configs/pilot.yaml").model.revision):
        pytest.skip("models not cached")
    monkeypatch.setenv("WSH_RESULTS_ROOT", str(tmp_path / "r"))
    monkeypatch.setenv("WSH_CACHE_PATH", str(tmp_path / "c" / "x.sqlite"))
    rep = run_preflight("configs/pilot.yaml")
    assert {"config_valid", "model_policy", "device", "models_cached", "datasets_match_frozen_set",
            "frozen_questions_load_without_excluded", "paths_writable"} <= set(rep["checks"])
    assert rep["ok"], {k: v for k, v in rep["checks"].items() if not v["ok"]}
    assert not (tmp_path / "r" / "pilot").exists()  # nothing was run
