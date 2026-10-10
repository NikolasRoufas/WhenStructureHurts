"""Runner lifecycle with the software-test mock generator (never used for reported results)."""

import json

import pytest

from conftest import FakeGenerator
from wsh.artifacts import RunContext, RunExistsError
from wsh.cache import KVCache
from wsh.config import load_config
from wsh.evaluation.reporting import write_reports
from wsh.experiments.common import ConditionUnavailable, Runner, make_layout
from wsh.representations.evidence import gold_bundle


class _Res:
    def __init__(self, gen):
        self.generator = gen
        self.nli_grounding = None
        self.cache = KVCache(None)
        self.loaded = {}

    def count_tokens(self, t):
        return len(t.split())


@pytest.fixture
def cfg(tmp_path):
    return load_config("configs/smoke.yaml", {"results_root": str(tmp_path / "results")})


def test_run_records_resume_and_no_overwrite(cfg, toy_question):
    ctx = RunContext(cfg, "unit")
    r = Runner(cfg, ctx, _Res(FakeGenerator(default="Answer: Larry Page\nEvidence: E1")))
    b = gold_bundle(toy_question)
    rec = r.run(toy_question, {"representation": "R1"}, lambda: (b, make_layout("R1", b), {}))
    assert rec["eval"]["em"] == 1.0 and rec["evidence"]["representation"] == "R1"
    for key in ("record_key", "run_id", "dataset_source", "model_revision", "seed", "timestamp", "generation", "failure"):
        assert key in rec
    # unavailable conditions are recorded, not dropped and not counted as failures
    ua = r.run(toy_question, {"representation": "R3x"}, lambda: (_ for _ in ()).throw(ConditionUnavailable("no path")))
    assert ua["unavailable"].startswith("ConditionUnavailable")
    # pipeline errors are recorded with a failure classification
    pe = r.run(toy_question, {"representation": "bad"}, lambda: (_ for _ in ()).throw(ValueError("boom")))
    assert pe["failure"]["primary"] == "pipeline_error"
    # resume skips completed keys
    ctx2 = RunContext(cfg, "unit", resume_dir=str(ctx.dir))
    gen2 = FakeGenerator()
    r2 = Runner(cfg, ctx2, _Res(gen2))
    assert r2.run(toy_question, {"representation": "R1"}, lambda: (b, make_layout("R1", b), {})) is None
    assert gen2.calls == [] and r2.n_skipped_done == 1
    # reports are recomputable from predictions.jsonl
    ctx2.update_manifest(status="completed")
    res = write_reports(ctx2)
    assert res["n_records"] == 3 and (ctx2.dir / "report.md").exists()
    table = [x for x in (ctx2.dir / "report.md").read_text().splitlines() if x.startswith("|")]
    assert len({x.count("|") for x in table[:3]}) == 1  # header, separator and rows have equal cell counts
    lines = (ctx.dir / "predictions.jsonl").read_text().splitlines()
    assert len(lines) == 3 and all(json.loads(x)["record_key"] for x in lines)


def test_resume_refuses_changed_config(cfg, toy_question):
    ctx = RunContext(cfg, "unit")
    other = cfg.model_copy(update={"seed": 99})
    with pytest.raises(RunExistsError):
        RunContext(other, "unit", resume_dir=str(ctx.dir))


def test_new_run_never_reuses_directory(cfg, monkeypatch):
    import wsh.artifacts as art

    monkeypatch.setattr(art.time, "strftime", lambda fmt, *a: "20990101-000000" if "%H%M%S" in fmt else "t")
    a = RunContext(cfg, "unit")
    b = RunContext(cfg, "unit")  # same second, same config: a fresh sibling directory, never a reuse
    assert a.dir != b.dir and b.dir.name == a.dir.name + "-2"
    assert (a.dir / "manifest.json").exists() and (b.dir / "manifest.json").exists()


def test_torn_last_line_is_tolerated(cfg, toy_question):
    ctx = RunContext(cfg, "unit")
    with open(ctx.pred_path, "a") as f:
        f.write('{"record_key": "x", "partial')
    ctx2 = RunContext(cfg, "unit", resume_dir=str(ctx.dir))
    assert not ctx2.is_done("x")
