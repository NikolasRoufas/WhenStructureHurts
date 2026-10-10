import pytest
import yaml
from pydantic import ValidationError

from wsh.cache import KVCache
from wsh.config import load_config
from wsh.models.policy import AUTH_ENV, PolicyViolation, check_model


def test_smoke_config_valid_and_policy_ok():
    cfg = load_config("configs/smoke.yaml")
    cfg.enforce_model_policy()
    assert cfg.model.do_sample is False


@pytest.mark.parametrize("mid", ["Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen2.5-3B-Instruct", "some/unknown-model"])
def test_large_or_unknown_models_blocked_in_smoke(mid):
    with pytest.raises(PolicyViolation):
        check_model(mid, None, "smoke")


def test_full_stage_requires_env_and_flag(monkeypatch):
    monkeypatch.delenv(AUTH_ENV, raising=False)
    with pytest.raises(PolicyViolation):
        check_model("Qwen/Qwen2.5-7B-Instruct", None, "full", authorized_flag=True)
    monkeypatch.setenv(AUTH_ENV, "1")
    with pytest.raises(PolicyViolation):
        check_model("Qwen/Qwen2.5-7B-Instruct", None, "full", authorized_flag=False)
    assert check_model("Qwen/Qwen2.5-7B-Instruct", None, "full", authorized_flag=True).n_params > 1e9


def test_revision_must_match_pin():
    with pytest.raises(PolicyViolation):
        check_model("Qwen/Qwen2.5-0.5B-Instruct", "deadbeef", "smoke")


def _cfg(tmp_path, **mut):
    raw = yaml.safe_load(open("configs/smoke.yaml"))
    for k, v in mut.items():
        raw[k] = v
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(raw))
    return p


def test_stage_limits_enforced(tmp_path):
    with pytest.raises(ValidationError):
        load_config(_cfg(tmp_path, datasets=[{"name": "musique", "n_examples": 500}]))
    with pytest.raises(ValidationError):
        load_config(_cfg(tmp_path, datasets=[{"name": "musique", "split": "test", "n_examples": 2}]))
    with pytest.raises(ValidationError):
        load_config(_cfg(tmp_path, max_generations=10**6))


def test_unknown_keys_rejected(tmp_path):
    with pytest.raises(ValidationError):
        load_config(_cfg(tmp_path, typo_key=1))


def test_sampling_cannot_be_enabled(tmp_path):
    raw = yaml.safe_load(open("configs/smoke.yaml"))
    raw["model"]["do_sample"] = True
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(raw))
    with pytest.raises(ValidationError):
        load_config(p)


def test_pilot_and_full_configs_validate_but_full_is_blocked(monkeypatch):
    load_config("configs/pilot.yaml").enforce_model_policy()
    full = load_config("configs/full.yaml")
    monkeypatch.delenv(AUTH_ENV, raising=False)
    with pytest.raises(PolicyViolation):
        full.enforce_model_policy()


def test_cache_roundtrip_and_counts(tmp_path):
    c = KVCache(tmp_path / "c.sqlite")
    assert c.get("ns", {"a": 1}) is None and c.misses == 1
    c.set("ns", {"a": 1}, {"v": [1, 2]})
    assert c.get("ns", {"a": 1}) == {"v": [1, 2]} and c.hits == 1
    calls = []
    v, cached = c.get_or_compute("ns", "k", lambda: calls.append(1) or 5)
    v2, cached2 = c.get_or_compute("ns", "k", lambda: calls.append(1) or 6)
    assert (v, cached, v2, cached2, len(calls)) == (5, False, 5, True, 1)
    c2 = KVCache(tmp_path / "c.sqlite")  # persistence across instances
    assert c2.get("ns", {"a": 1}) == {"v": [1, 2]}


def test_realign_and_finite_guard():
    import torch

    from wsh.models.encoders import NonFiniteOutputError, assert_finite, realign_parameters

    m = torch.nn.Linear(4, 2)
    before = [p.clone() for p in m.parameters()]
    realign_parameters(m)
    assert all(torch.equal(a, b) for a, b in zip(before, m.parameters()))
    assert_finite([0.1, 2.0], "ok")
    with pytest.raises(NonFiniteOutputError):
        assert_finite([float("nan")], "reranker")


GPU_MODELS = ["Qwen/Qwen2.5-3B-Instruct", "Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen3.5-9B"]


@pytest.mark.parametrize("mid", GPU_MODELS)
def test_gpu_models_blocked_in_development_stages(mid, monkeypatch):
    monkeypatch.setenv(AUTH_ENV, "1")  # even with the env var set, local stages refuse them
    for stage in ("smoke", "pilot"):
        with pytest.raises(PolicyViolation):
            check_model(mid, None, stage, authorized_flag=True)


@pytest.mark.parametrize("mid", GPU_MODELS)
@pytest.mark.parametrize("stage", ["gpu_pilot", "full"])
def test_gpu_models_need_env_and_flag(mid, stage, monkeypatch):
    monkeypatch.delenv(AUTH_ENV, raising=False)
    with pytest.raises(PolicyViolation):
        check_model(mid, None, stage, authorized_flag=True)
    monkeypatch.setenv(AUTH_ENV, "1")
    with pytest.raises(PolicyViolation):
        check_model(mid, None, stage, authorized_flag=False)
    assert check_model(mid, None, stage, authorized_flag=True).n_params > 1e9


def test_gpu_pilot_config_pinned_and_gated(monkeypatch):
    from wsh.models.policy import load_model_registry

    _, reg = load_model_registry()
    cfg = load_config("configs/gpu_pilot.yaml")
    assert cfg.stage == "gpu_pilot" and cfg.model.revision == reg["Qwen/Qwen2.5-7B-Instruct"].revision
    for mid in GPU_MODELS:  # switching the generator resolves its pinned revision
        c = load_config("configs/gpu_pilot.yaml", {"model.model_id": mid})
        assert c.model.revision == reg[mid].revision
    monkeypatch.delenv(AUTH_ENV, raising=False)
    with pytest.raises(PolicyViolation):
        cfg.enforce_model_policy(authorized_flag=True)
    monkeypatch.setenv(AUTH_ENV, "1")
    cfg.enforce_model_policy(authorized_flag=True)  # validation only: nothing is loaded or launched
    pilot = load_config("configs/pilot.yaml")
    assert [d.qids for d in cfg.datasets] == [d.qids for d in pilot.datasets]  # same frozen questions
    assert cfg.exp1 == pilot.exp1 and cfg.exp2 == pilot.exp2 and cfg.exp3 == pilot.exp3


def test_qwen35_disables_thinking_in_chat_template():
    from wsh.models.policy import load_model_registry

    entry = load_model_registry()[1]["Qwen/Qwen3.5-9B"]
    assert entry.raw["chat_template_kwargs"] == {"enable_thinking": False}


def test_full_stage_refuses_pilot_questions(toy_question):
    from wsh.data.question_sets import ExcludedQuestionError, assert_no_excluded, pilot_question_uids

    pilot = pilot_question_uids()
    assert len(pilot) == 350
    uid = next(iter(pilot))
    q = toy_question.model_copy(update={"uid": uid})
    assert_no_excluded({"x": [q]}, {}, "gpu_pilot")  # pilots may use their own questions
    with pytest.raises(ExcludedQuestionError):
        assert_no_excluded({"x": [q]}, {}, "full")
