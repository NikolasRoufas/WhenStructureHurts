from wsh.evaluation.answer_metrics import exact_match, token_f1, yes_no_normalize
from wsh.evaluation.evaluator import evaluate
from wsh.evaluation.failure_analysis import classify
from wsh.evaluation.parsing import map_verdict, parse_output
from wsh.experiments.common import make_layout
from wsh.representations.evidence import gold_bundle
from wsh.representations.serialization import render


def test_em_f1_squad_conventions():
    assert exact_match("The Larry Page.", ["Larry Page"]) == 1.0
    assert exact_match(None, ["x"]) == 0.0
    assert abs(token_f1("Larry Page and Sergey", ["Larry Page and Sergey Brin"]) - (2 * 1 * 0.8 / 1.8)) < 1e-9  # P=4/4, R=4/5
    assert token_f1("yes", ["no"]) == 0.0 and token_f1("yes it is", ["yes"]) == 0.0  # yes/no exact only
    assert yes_no_normalize("Yes, they were.") == "yes"


def test_fever_verdict_mapping_fix():
    labels = ["SUPPORTS", "REFUTES", "NOT ENOUGH INFO"]
    assert map_verdict("SUPPORTS", labels) == "SUPPORTS"
    assert map_verdict("refuted", labels) == "REFUTES"
    assert map_verdict("The claim is not supported", labels) == "REFUTES"
    assert map_verdict("Not enough info", labels) == "NOT ENOUGH INFO"
    # The original failure mode: a natural-language statement is NOT silently scored as a label
    assert map_verdict("Jackie was directed by Pablo Larrain", labels) is None
    hover = ["SUPPORTED", "NOT_SUPPORTED"]
    assert map_verdict("NOT SUPPORTED", hover) == "NOT_SUPPORTED"
    assert map_verdict("supported", hover) == "SUPPORTED"


def test_parse_format_and_citations():
    p = parse_output("Answer: Larry Page [E2]\nEvidence: E1, E2, E9", {"E1", "E2"})
    assert p.answer == "Larry Page" and p.answer_source == "field"
    assert p.cited == ["E2", "E1", "E9"] and p.invalid_cited == ["E9"]
    q = parse_output("Larry Page founded it.", {"E1"})
    assert q.answer_source == "fallback_line" and q.cited == []
    assert parse_output("Answer: insufficient evidence", {"E1"}).abstained


def test_invalid_citation_does_not_make_correct_answer_wrong(toy_question):
    b = gold_bundle(toy_question)
    ser = render(make_layout("R1", b))
    out = evaluate(toy_question, "Answer: Larry Page\nEvidence: E99", "eos", ser, b)
    assert out["eval"]["em"] == 1.0
    assert out["failure"]["answered"] is True
    assert "invalid_citation" in out["failure"]["flags"]
    assert out["eval"]["n_invalid_cited"] == 1 and out["eval"]["citation_validity"] == 0.0


def test_truncated_but_parsed_answer_is_scored(toy_question):
    b = gold_bundle(toy_question)
    ser = render(make_layout("R1", b))
    out = evaluate(toy_question, "Answer: Larry Page\nEvid", "length", ser, b)
    assert out["eval"]["em"] == 1.0 and "truncated" in out["failure"]["flags"] and out["failure"]["answered"]


def test_unanswered_examples_stay_in_denominator(toy_question):
    b = gold_bundle(toy_question)
    ser = render(make_layout("R1", b))
    out = evaluate(toy_question, "", "eos", ser, b)
    assert out["failure"]["primary"] == "empty_output" and not out["failure"]["answered"]
    assert out["eval"]["em"] == 0.0 and out["eval"]["f1"] == 0.0
    perr = evaluate(toy_question, None, None, None, None, pipeline_error=True)
    assert perr["failure"]["primary"] == "pipeline_error" and perr["eval"]["em"] == 0.0


def test_citation_precision_recall(toy_question):
    b = gold_bundle(toy_question)
    ser = render(make_layout("R1", b))
    gold_ids = [d for d, v in ser.id_map.items() if b.claim(v["claim_ids"][0]).is_gold_support]
    other = [d for d in ser.id_map if d not in gold_ids][0]
    out = evaluate(toy_question, f"Answer: Larry Page\nEvidence: {gold_ids[0]}, {other}", "eos", ser, b)
    assert out["eval"]["citation_precision"] == 0.5 and out["eval"]["citation_recall"] == 0.5
    assert out["eval"]["support_coverage"] == 1.0 and out["eval"]["answer_in_evidence"] == 1.0


def test_failure_precedence():
    f = classify(finish_reason="skipped_overflow")
    assert f["primary"] == "context_overflow" and not f["answered"]
    f = classify(finish_reason="error")
    assert f["primary"] == "generation_error"


def test_answer_in_evidence_is_order_invariant(toy_question):
    # answer straddles a sentence boundary (cf. HotpotQA "Hey Pa! / There's a Goat on the Roof")
    q = toy_question.model_copy(update={"answers": ["an AI lab. DeepMind was acquired"]})
    b = gold_bundle(q)
    vals = {evaluate(q, "Answer: x", "eos", render(make_layout(rep, b, seed)), b)["eval"]["answer_in_evidence"]
            for rep, seed in [("R0", 0), ("R1", 0)] + [("R2", s) for s in range(6)]}
    assert vals == {1.0}
