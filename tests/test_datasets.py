"""Parsing of REAL benchmark files (skipped if the raw data has not been fetched)."""

import itertools

import pytest

from conftest import data_available
from wsh.data.loaders import DataUnavailableError, iter_questions, sample_questions
from wsh.data.schemas import AnnotationStatus as S
from wsh.data.validation import validate_question
from wsh.representations.evidence import gold_bundle

DATASETS = ["musique", "2wikimultihopqa", "hotpotqa", "hover", "fever"]


@pytest.mark.parametrize("name", DATASETS)
def test_first_records_parse_and_validate(name):
    if not data_available(name):
        pytest.skip(f"{name} not fetched")
    qs = list(itertools.islice(iter_questions(name, "dev"), 50))
    assert qs
    for q in qs:
        validate_question(q)
        assert q.uid.startswith(f"{name}/") and q.qid in q.uid
        assert q.annotations["supports_edges"] == S.UNAVAILABLE  # never manufactured


@pytest.mark.skipif(not data_available("hotpotqa"), reason="hotpotqa not fetched")
def test_hotpotqa_first_dev_example_exact():
    q = next(iter_questions("hotpotqa", "dev"))
    assert q.qid == "5a8b57f25542995d1e6f1371"
    assert q.answers == ["yes"] and q.answer_type == "yes_no"
    assert len(q.passages) == 10
    gold_titles = [q.passage(f.passage_id).title for f in q.supporting_facts]
    assert gold_titles == ["Scott Derrickson", "Ed Wood"]
    assert q.question_type == "comparison" and all(not s.depends_on for s in q.reasoning_steps)


@pytest.mark.skipif(not data_available("musique"), reason="musique not fetched")
def test_musique_decomposition_dependencies():
    q = next(iter_questions("musique", "dev"))
    assert q.qid == "2hop__460946_294723"
    assert [s.sub_answer for s in q.reasoning_steps] == ["Steve Hillage", "Miquette Giraudy"]
    assert q.reasoning_steps[1].depends_on == [0]
    assert q.annotations["supporting_sentences"] == S.UNAVAILABLE  # paragraph-level only
    assert all(f.sentence_index is None for f in q.supporting_facts)
    assert q.annotations["sentence_segmentation"] == S.DETERMINISTIC_DERIVED


@pytest.mark.skipif(not data_available("2wikimultihopqa"), reason="2wiki not fetched")
def test_2wiki_triples_map_to_steps():
    q = next(iter_questions("2wikimultihopqa", "dev"))
    assert q.answers == ["Małgorzata Braunek"]
    assert [s.triple[1] for s in q.reasoning_steps] == ["director", "mother"]
    assert q.reasoning_steps[1].depends_on == [0]
    b = gold_bundle(q)
    dep = [e for e in b.edges if e.relation.value == "DEPENDS_ON"]
    assert dep and dep[0].status == S.DETERMINISTIC_DERIVED


@pytest.mark.skipif(not data_available("fever"), reason="fever not fetched")
def test_fever_nei_evidence_is_model_predicted():
    for q in itertools.islice(iter_questions("fever", "dev"), 400):
        if q.answers[0] == "NOT ENOUGH INFO":
            assert all(f.status == S.MODEL_PREDICTED for f in q.supporting_facts)
            assert q.gold_facts() == []
            return
    pytest.fail("no NEI example found")


def test_sampling_is_deterministic():
    if not data_available("musique"):
        pytest.skip("musique not fetched")
    a = [q.qid for q in sample_questions("musique", "dev", 5, seed=7)]
    b = [q.qid for q in sample_questions("musique", "dev", 5, seed=7)]
    c = [q.qid for q in sample_questions("musique", "dev", 5, seed=8)]
    assert a == b and a != c


def test_test_split_refused():
    with pytest.raises(DataUnavailableError):
        sample_questions("musique", "test", 1, 0)
