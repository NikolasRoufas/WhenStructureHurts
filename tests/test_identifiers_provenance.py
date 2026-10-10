import pytest

from wsh.data.provenance import (DuplicateIdentifierError, assert_unique, atomic_claim_id, derived_claim_id,
                                 gold_units, passage_id, sentence_claim_id)
from wsh.data.schemas import AnnotationStatus
from wsh.data.validation import ValidationError, validate_bundle, validate_question
from wsh.extraction.claim_extractor import SentenceClaimExtractor
from wsh.representations.evidence import gold_bundle


def test_passage_ids_unique_even_with_duplicate_titles(toy_question):
    # Regression for the original bug: two context entries with the same title ("Google")
    # used to resolve to the same identifier in the passage-level baselines.
    titles = [p.title for p in toy_question.passages]
    assert titles.count("Google") == 2
    ids = [p.passage_id for p in toy_question.passages]
    assert len(set(ids)) == len(ids)
    validate_question(toy_question)


def test_passage_level_claims_never_collide(toy_question):
    claims, _ = SentenceClaimExtractor().extract(toy_question.passages, gold_units(toy_question))
    assert_unique([c.claim_id for c in claims])  # would raise on collision


def test_assert_unique_raises():
    with pytest.raises(DuplicateIdentifierError):
        assert_unique(["a", "b", "a"])


def test_claim_id_scheme_is_stable_and_hierarchical():
    pid = passage_id("hotpotqa", "5a8b", 3)
    assert pid == "hotpotqa/5a8b/p03"
    assert sentence_claim_id(pid, 2) == "hotpotqa/5a8b/p03#s02"
    assert atomic_claim_id(pid, 2, 1) == "hotpotqa/5a8b/p03#s02.a1"
    assert derived_claim_id("x#s00", "p6negation") == "x#s00~p6negation"
    # deterministic: same inputs, same id
    assert passage_id("hotpotqa", "5a8b", 3) == pid


def test_sentence_claim_text_matches_span(toy_question):
    b = gold_bundle(toy_question)
    for c in b.claims:
        sp = c.spans[0]
        assert b.passages[sp.passage_id].text[sp.start:sp.end] == c.text
    validate_bundle(b)


def test_gold_flags_follow_supporting_facts(toy_question):
    b = gold_bundle(toy_question)
    gold = {c.claim_id for c in b.claims if c.is_gold_support}
    p0, p1 = toy_question.passages[0].passage_id, toy_question.passages[1].passage_id
    assert gold == {f"{p0}#s01", f"{p1}#s00"}


def test_validation_rejects_corrupted_gold(toy_question):
    b = gold_bundle(toy_question)
    c = b.claims[0]
    b.claims[0] = c.model_copy(update={"is_corrupted": True, "is_gold_support": True, "status": AnnotationStatus.CORRUPTED})
    with pytest.raises(ValidationError):
        validate_bundle(b)


def test_validation_rejects_tampered_sentence_text(toy_question):
    b = gold_bundle(toy_question)
    b.claims[0] = b.claims[0].model_copy(update={"text": "something else"})
    with pytest.raises(ValidationError):
        validate_bundle(b)


def test_model_predicted_evidence_is_not_gold(toy_question):
    q = toy_question.model_copy(deep=True)
    for f in q.supporting_facts:
        f.status = AnnotationStatus.MODEL_PREDICTED  # e.g. FEVER NEI evidence
    assert q.gold_facts() == []
    assert gold_units(q) == []
