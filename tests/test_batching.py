"""Batched generation: correctness against unbatched generation, association, padding, OOM,
caching, and runner-level completeness/resumption."""

import json
import os

import pytest

from conftest import FakeGenerator
from wsh.artifacts import RunContext
from wsh.cache import KVCache
from wsh.config import ModelConfig, load_config
from wsh.experiments.common import BudgetExceeded, Runner, make_layout
from wsh.hashing import stable_hash
from wsh.models.interfaces import GenerationRequest, GenerationResult
from wsh.representations.evidence import gold_bundle

QWEN = "Qwen/Qwen2.5-0.5B-Instruct"
REV = "7ae557604adf67be50417f59c2c2f167def9a775"


def _tokenizer():
    from wsh.models.policy import is_cached

    if not is_cached(QWEN, REV):
        pytest.skip("Qwen tokenizer not cached")
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(QWEN, revision=REV, local_files_only=True)


def _tiny_generator(batch_size, cache=None, seed=0):
    """Randomly initialised 2-layer Qwen2 with the real tokenizer: any padding or attention-
    mask error changes its greedy outputs, so equality with unbatched runs is informative."""
    import torch
    from transformers import Qwen2Config, Qwen2ForCausalLM

    from wsh.models.local_generator import LocalHFGenerator

    tok = _tokenizer()
    torch.manual_seed(seed)
    cfg = Qwen2Config(vocab_size=len(tok), hidden_size=64, intermediate_size=128, num_hidden_layers=2,
                      num_attention_heads=4, num_key_value_heads=2, max_position_embeddings=4096,
                      eos_token_id=tok.eos_token_id, pad_token_id=tok.pad_token_id)
    model = Qwen2ForCausalLM(cfg).float()
    mcfg = ModelConfig(model_id="tiny/random", revision="0", device="cpu", dtype="float32", max_new_tokens=12,
                       max_input_tokens=2048, batch_size=batch_size)
    return LocalHFGenerator.from_components(mcfg, model, tok, "cpu", cache)


def _requests(n=11):
    # deliberately mixed lengths (4 to ~300 words), one exact duplicate, two max_new_tokens groups
    reqs = []
    for i in range(n):
        body = " ".join(f"fact{i}_{k}" for k in range(1 + (i * 37) % 300))
        reqs.append(GenerationRequest(system="You answer.", user=f"Evidence: {body}\nQuestion {i}?", max_new_tokens=12,
                                      prefill="Answer:"))
    reqs.append(GenerationRequest(**{**reqs[3].__dict__}))  # duplicate of request 3
    reqs.append(GenerationRequest(system="You answer.", user="short", max_new_tokens=5, prefill="Answer:"))
    return reqs


def test_batched_equals_unbatched_on_mixed_lengths():
    reqs = _requests()
    single = _tiny_generator(1)
    ref = [single.generate(r) for r in reqs]
    for bs in (2, 4, 16):
        got = _tiny_generator(bs).generate_batch(reqs)
        assert [g.text for g in got] == [r.text for r in ref], f"batch_size={bs}"
        assert [g.output_tokens for g in got] == [r.output_tokens for r in ref]
        assert [g.input_tokens for g in got] == [r.input_tokens for r in ref]  # padding never counted
        assert [g.finish_reason for g in got] == [r.finish_reason for r in ref]


def test_batched_is_deterministic_and_left_padded():
    reqs = _requests()
    a, b = _tiny_generator(4).generate_batch(reqs), _tiny_generator(4).generate_batch(reqs)
    assert [x.text for x in a] == [y.text for y in b]
    assert _tiny_generator(4).tokenizer.padding_side == "left"


def test_results_are_in_request_order_with_dedup_and_overflow():
    g = _tiny_generator(4)
    g.max_input_tokens = 200
    reqs = _requests()
    out = g.generate_batch(reqs)
    assert len(out) == len(reqs)
    assert out[11].text == out[3].text and out[11].cached and not out[3].cached  # duplicate served like a cache hit
    assert g.stats["n_dedup_in_batch"] == 1
    over = [i for i, r in enumerate(out) if r.finish_reason == "skipped_overflow"]
    assert over and all(out[i].output_tokens == 0 and "max_input_tokens" in out[i].error for i in over)


def test_cache_works_with_batching_and_is_batch_size_specific(tmp_path):
    cache = KVCache(tmp_path / "c.sqlite")
    g = _tiny_generator(4, cache)
    reqs = _requests()
    first = g.generate_batch(reqs)
    n = g.n_uncached
    again = g.generate_batch(reqs)
    assert g.n_uncached == n and all(r.cached for r in again)  # nothing regenerated
    assert [r.text for r in again] == [r.text for r in first]
    g8 = _tiny_generator(8, cache)
    g8.generate_batch(reqs[:2])
    assert g8.n_uncached == 2  # a different batch size never reuses outputs


def test_rows_are_cut_at_first_eos():
    import torch

    g = _tiny_generator(2)
    eos = g.tokenizer.eos_token_id
    def fake_generate(input_ids, attention_mask, max_new_tokens, **kw):
        # each row's continuation depends on that row's own input (as with a real model):
        # the shorter prompt finishes early and is then padded, the longer one hits the limit
        early = [11, 12, eos, g.tokenizer.pad_token_id, g.tokenizer.pad_token_id]
        full = [21, 22, 23, 24, 25]
        n = attention_mask.sum(dim=1)
        rows = [early if int(k) == int(n.min()) else full for k in n]
        return torch.cat([input_ids, torch.tensor(rows)], dim=1)

    g.model.generate = fake_generate
    reqs = [GenerationRequest(system="s", user="u one", max_new_tokens=5),
            GenerationRequest(system="s", user="u two two two two", max_new_tokens=5)]
    a, b = g.generate_batch(reqs)  # internally reordered longest-first; results come back in request order
    assert (a.finish_reason, a.output_tokens) == ("eos", 3) and (b.finish_reason, b.output_tokens) == ("length", 5)
    assert a.text == g.tokenizer.decode([11, 12], skip_special_tokens=True)
    assert a.input_tokens < b.input_tokens


def test_oom_splits_batch_and_keeps_every_result():
    import torch

    g = _tiny_generator(8)
    reqs = _requests()[:8]
    ref = [_tiny_generator(1).generate(r) for r in reqs]
    real = g.model.generate

    def oom_above_two(**kw):
        if kw["input_ids"].shape[0] > 2:
            raise torch.OutOfMemoryError("CUDA out of memory (simulated)")
        return real(**kw)

    g.model.generate = oom_above_two
    out = g.generate_batch(reqs)
    assert [o.text for o in out] == [r.text for r in ref] and g.stats["n_oom_splits"] >= 2

    def always_oom(**kw):
        raise torch.OutOfMemoryError("CUDA out of memory (simulated)")

    g2 = _tiny_generator(4)
    g2.model.generate = always_oom
    out = g2.generate_batch(reqs[:3])
    assert len(out) == 3 and all(o.finish_reason == "error" and "OutOfMemory" in o.error for o in out)
    assert g2.stats["n_oom_failures"] == 3


def test_non_oom_errors_are_recorded_not_raised():
    g = _tiny_generator(4)

    def broken(**kw):
        raise ValueError("boom")

    g.model.generate = broken
    out = g.generate_batch(_requests()[:3])
    assert all(o.finish_reason == "error" and "boom" in o.error for o in out)


@pytest.mark.skipif(os.environ.get("WSH_RUN_SLOW") != "1", reason="real-model check; set WSH_RUN_SLOW=1")
def test_real_qwen05b_batched_matches_unbatched_on_smoke_prompts():
    """The 0.5B development model on real smoke prompts (several representations, mixed
    lengths): batched greedy outputs must equal unbatched ones on this device/dtype."""
    from wsh.experiments.common import load_questions
    from wsh.models.local_generator import LocalHFGenerator
    from wsh.models.prompts import build_request
    from wsh.representations.serialization import render

    cfg = load_config("configs/smoke.yaml")
    reqs = []
    for qs in load_questions(cfg).values():
        for q in qs[:2]:
            try:
                b = gold_bundle(q)
            except Exception:
                continue
            for rep in ("R0", "R2", "R4"):
                reqs.append(build_request(q, render(make_layout(rep, b, 0)).text, 48))
    dev = os.environ.get("WSH_TEST_DEVICE", "cpu")  # e.g. cuda on the server
    dtype = os.environ.get("WSH_TEST_DTYPE", "float32")
    m1 = cfg.model.model_copy(update={"device": dev, "dtype": dtype, "batch_size": 1})
    ref = LocalHFGenerator(m1, "smoke").generate_batch(reqs)
    got = LocalHFGenerator(m1.model_copy(update={"batch_size": 8}), "smoke").generate_batch(reqs)
    agree = sum(a.text == b.text for a, b in zip(ref, got))
    print(f"\nreal 0.5B batched-vs-unbatched exact agreement on {dev}/{dtype}: {agree}/{len(reqs)}")
    assert agree == len(reqs)


# ---------------------------------------------------------------- runner level


class EchoGenerator(FakeGenerator):
    """Answer depends only on the request, so any mix-up between records and outputs shows."""

    def __init__(self, batch: bool):
        super().__init__()
        self.batch_calls = []  # (runs with model.batch_size == 1 never call generate_batch)

    @staticmethod
    def expected(user: str) -> str:
        return f"Answer: a{stable_hash(user)[:8]}\nEvidence: E1"

    def generate(self, req):
        self.calls.append(req)
        return GenerationResult(text=self.expected(req.user), input_tokens=1, output_tokens=1, latency_s=0.0,
                                finish_reason="eos", model_id=self.model_id, revision=self.revision)

    def generate_batch(self, reqs):
        self.batch_calls.append(len(reqs))
        return [GenerationResult(text=self.expected(r.user), input_tokens=1, output_tokens=1, latency_s=0.0,
                                 finish_reason="eos", model_id=self.model_id, revision=self.revision,
                                 batch_size=len(reqs)) for r in reqs]


class _Res:
    def __init__(self, gen):
        self.generator, self.nli_grounding, self.cache, self.loaded = gen, None, KVCache(None), {}

    def count_tokens(self, t):
        return len(t.split())

    def apply_verified(self, q, b):
        pass


REPS = ["R0", "R1", "R2", "R3", "R4", "R5"]


def _run_exp1(tmp_path, toy_question, batch_size, gen, name):
    from wsh.experiments import exp1_representations

    cfg = load_config("configs/smoke.yaml", {"results_root": str(tmp_path / name), "exp1.representations": REPS,
                                             "exp1.budget_policies": ["shared", "per_representation"],
                                             "model.batch_size": batch_size})
    ctx = RunContext(cfg, "exp1")
    runner = Runner(cfg, ctx, _Res(gen))
    exp1_representations.body(runner, {"toy": [toy_question]})
    runner.flush()
    return ctx, [json.loads(x) for x in (ctx.dir / "predictions.jsonl").read_text().splitlines()]


def test_runner_batched_equals_unbatched_records(tmp_path, toy_question):
    _, a = _run_exp1(tmp_path, toy_question, 1, EchoGenerator(batch=False), "a")
    gb = EchoGenerator(batch=True)
    _, b = _run_exp1(tmp_path, toy_question, 3, gb, "b")
    assert gb.batch_calls and max(gb.batch_calls) > 1  # really batched
    ka, kb = [r["record_key"] for r in a], [r["record_key"] for r in b]
    assert len(kb) == len(set(kb)) and set(ka) == set(kb)  # no duplicates, nothing missing
    by = {r["record_key"]: r for r in a}
    for r in b:
        assert r["generation"]["text"] == EchoGenerator.expected(r["prompt"]["user"])  # correct association
        assert r["generation"]["text"] == by[r["record_key"]]["generation"]["text"]
        assert r["eval"] == by[r["record_key"]]["eval"]


def test_interrupted_batched_run_resumes_without_loss_or_duplication(tmp_path, toy_question):
    from wsh.experiments import exp1_representations

    cfg = load_config("configs/smoke.yaml", {"results_root": str(tmp_path), "exp1.representations": REPS,
                                             "model.batch_size": 2})  # queue limit 8 < 12 records
    ctx = RunContext(cfg, "exp1")
    runner = Runner(cfg, ctx, _Res(EchoGenerator(batch=True)))
    exp1_representations.body(runner, {"toy": [toy_question]})
    lost = len(runner._pending)
    assert lost > 0  # simulate a crash: the queue is never flushed
    written = len((ctx.dir / "predictions.jsonl").read_text().splitlines())
    ctx2 = RunContext(cfg, "exp1", resume_dir=str(ctx.dir))
    r2 = Runner(cfg, ctx2, _Res(EchoGenerator(batch=True)))
    exp1_representations.body(r2, {"toy": [toy_question]})
    r2.flush()
    recs = [json.loads(x) for x in (ctx.dir / "predictions.jsonl").read_text().splitlines()]
    keys = [r["record_key"] for r in recs]
    assert len(keys) == len(set(keys)) == written + lost
    assert r2.n_skipped_done == written


def test_budget_cap_counts_queued_records(tmp_path, toy_question):
    cfg = load_config("configs/smoke.yaml", {"results_root": str(tmp_path), "model.batch_size": 8, "max_generations": 3})
    runner = Runner(cfg, RunContext(cfg, "unit"), _Res(EchoGenerator(batch=True)))
    b = gold_bundle(toy_question)
    with pytest.raises(BudgetExceeded):
        for i in range(10):
            runner.run(toy_question, {"representation": "R1", "i": i}, lambda: (b, make_layout("R1", b), {}))
    assert len(runner._pending) == 3  # never more than the cap is admitted
    runner.flush()
    assert runner.n_written == 3


def test_chat_template_kwargs_reach_the_template():
    g = _tiny_generator(1)
    seen = {}
    real = g.tokenizer.apply_chat_template

    def spy(msgs, **kw):
        seen.update(kw)
        return real(msgs, **{k: v for k, v in kw.items() if k != "enable_thinking"})

    g.tokenizer.apply_chat_template = spy
    g.chat_template_kwargs = {"enable_thinking": False}
    g.render(GenerationRequest(system="s", user="u", max_new_tokens=4))
    assert seen.get("enable_thinking") is False
