"""Experiment C preflight (no generation): render every frozen confirm2 prompt (system + user from the Qwen run)
through the OLMo-2 chat template exactly as LocalHFGenerator.render does, count tokens, and report overflow
against max_input_tokens per condition.

    PYTHONPATH=src python experiments/andreas_revision/model_replication/token_preflight.py <confirm2_run_dir> <out.json>
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from transformers import AutoTokenizer

from wsh.config import load_config
from wsh.models.prompts import ANSWER_PREFILL

CFG = Path(__file__).resolve().parent / "configs/olmo2_confirm2_full.yaml"


def main(run: Path, out: Path) -> None:
    cfg = load_config(CFG)
    tok = AutoTokenizer.from_pretrained(cfg.model.model_id, revision=cfg.model.revision, local_files_only=True)
    lens: dict = defaultdict(dict)
    with open(run / "predictions.jsonl") as f:
        for line in f:
            r = json.loads(line)
            rep = r["condition"]["representation"]
            if r["condition"].get("protocol") != "A" or rep not in ("R4P_FO", "R4P_FO_NC"):
                continue
            msgs = [{"role": "system", "content": r["prompt"]["system"]}, {"role": "user", "content": r["prompt"]["user"]}]
            text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True) + ANSWER_PREFILL
            lens[rep][(r["dataset"], r["question_uid"])] = len(tok(text, add_special_tokens=False)["input_ids"])
    lim = cfg.model.max_input_tokens
    res = {"model": f"{cfg.model.model_id}@{cfg.model.revision}", "max_input_tokens": lim,
           "max_position_embeddings": getattr(tok, "model_max_length", None)}
    for rep, d in lens.items():
        v = sorted(d.values())
        res[rep] = {"n": len(v), "max": v[-1], "p99": v[int(0.99 * (len(v) - 1))], "mean": sum(v) / len(v),
                    "n_overflow": sum(x > lim for x in v)}
    over = {k for rep in lens for k, x in lens[rep].items() if x > lim}
    res["n_questions_any_overflow"] = len(over)
    res["n_questions_condition_dependent_overflow"] = sum(
        (lens["R4P_FO"].get(k, 0) > lim) != (lens["R4P_FO_NC"].get(k, 0) > lim) for k in over)
    out.write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
