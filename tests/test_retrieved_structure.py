"""Retrieved-evidence structure option (revision-1): annotation edges restricted to retrieved sentences."""
from wsh.config import load_config
from wsh.experiments import exp1_representations as e1
from wsh.representations.evidence import gold_bundle


class _Res:
    reranker = None

    def corpus(self, ds):
        return None


class _Runner:
    def __init__(self, cfg):
        self.cfg, self.res = cfg, _Res()


def _cfg(mode):
    return load_config("configs/smoke.yaml", {"exp1.evidence_source": "retrieved", "exp1.retrieved_edges": mode,
                                              "retrieval.top_k": 4})


def test_annotation_restricted_edges_are_a_subset_of_gold_edges(toy_question, monkeypatch):
    import wsh.retrieval.reranking as rr
    from wsh.retrieval.reranking import retrieve as real

    monkeypatch.setattr(rr, "retrieve", lambda q, cfg, **kw: real(q, cfg, method="bm25", rerank=False))
    b = e1._retrieved_bundle(toy_question, _Runner(_cfg("annotation_restricted")))
    gold = {e.key for e in gold_bundle(toy_question).edges}
    ids = {c.claim_id for c in b.claims}
    assert {e.key for e in b.edges} <= gold
    assert all(e.source in ids and e.target in ids for e in b.edges)
    assert b.origin["edges"] == "annotation_derived_restricted_to_retrieved"


def test_default_retrieved_structure_unchanged(toy_question, monkeypatch):
    import wsh.retrieval.reranking as rr
    from wsh.retrieval.reranking import retrieve as real

    monkeypatch.setattr(rr, "retrieve", lambda q, cfg, **kw: real(q, cfg, method="bm25", rerank=False))
    b = e1._retrieved_bundle(toy_question, _Runner(_cfg("heuristic")))
    assert all(e.method.startswith("heuristic") for e in b.edges)
