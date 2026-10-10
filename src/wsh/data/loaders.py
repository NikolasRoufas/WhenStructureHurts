"""Dataset adapters: raw benchmark files -> ``Question`` objects.

All annotations are tagged with an ``AnnotationStatus``. Derivation rules used here:

* R-SEG   MuSiQue paragraphs have no sentence segmentation; we apply text.split_sentences
          (DETERMINISTIC_DERIVED, splitter id recorded per passage).
* R-HOP   hop_count = number of decomposition steps (MuSiQue, dataset-supplied) or number of
          distinct supporting passages (others, derived).
* R-MSQ   MuSiQue step dependencies: step j depends on step i iff its sub-question contains
          "#{i+1}" (derived from the dataset's decomposition).
* R-2WK   2Wiki steps follow the dataset's evidence-triple order. Triple -> passage by
          normalised title == normalised subject. Step j depends on step i (i<j) iff
          subject_j == object_i. If any triple cannot be mapped, steps are UNAVAILABLE.
* R-HPQ   HotpotQA bridge order: gold passage A precedes B iff A's supporting sentences
          mention B's normalised title and not vice versa (falls back to full passage text);
          otherwise UNAVAILABLE. Comparison questions: two parallel steps, no dependency.
* R-HOV   HoVer sentence text recovered from the HotpotQA distractor-dev context.
SUPPORTS/CONTRADICTS/DUPLICATE/SUPERSEDES gold edges are UNAVAILABLE for every dataset.
"""

from __future__ import annotations

import json
import logging
import os
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator

import yaml

from ..hashing import stable_hash
from ..text import SENTENCE_SPLITTER_ID, contains_phrase, normalize_title, split_sentences
from .provenance import passage_id
from .schemas import (
    AnnotationStatus as S,
    Passage,
    Question,
    ReasoningStep,
    SourceRef,
    SupportingFact,
)

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_ROOT = Path(os.environ["WSH_DATA_ROOT"]) if os.environ.get("WSH_DATA_ROOT") else REPO_ROOT / "data" / "raw"
DEFAULT_REGISTRY = REPO_ROOT / "configs" / "datasets.yaml"

NO_GOLD_EDGES = {
    "supports_edges": S.UNAVAILABLE,
    "contradicts_edges": S.UNAVAILABLE,
    "duplicate_edges": S.UNAVAILABLE,
    "supersedes_edges": S.UNAVAILABLE,
    "temporal_info": S.UNAVAILABLE,
}


class DataUnavailableError(RuntimeError):
    pass


@dataclass
class DatasetSpec:
    name: str
    raw: dict[str, Any]

    @property
    def task(self) -> str:
        return self.raw["task"]

    @property
    def repo(self) -> str:
        src = self.raw["source"]
        return src.get("repo") or src.get("url")

    @property
    def revision(self) -> str:
        return self.raw["source"]["revision"]

    def local_dir(self, data_root: Path) -> Path:
        src = self.raw["source"]
        return data_root / (src.get("local_dir") or src["repo"].replace("/", "__"))

    def file_for(self, split: str, data_root: Path) -> Path:
        if split not in self.raw["splits"]:
            raise DataUnavailableError(f"{self.name}: split '{split}' not registered")
        return self.local_dir(data_root) / self.raw["splits"][split]["file"]


def load_registry(path: str | Path = DEFAULT_REGISTRY) -> dict[str, DatasetSpec]:
    with open(path) as f:
        raw = yaml.safe_load(f)["datasets"]
    return {k: DatasetSpec(k, v) for k, v in raw.items()}


# ----------------------------------------------------------------------------- helpers


def _join_sentences(sents: list[str]) -> tuple[str, list[tuple[int, int]]]:
    """Concatenate dataset-supplied sentences, keeping exact per-sentence offsets."""
    text = ""
    spans: list[tuple[int, int]] = []
    for s in sents:
        s = str(s)
        if text and not text[-1].isspace() and not s[:1].isspace():
            text += " "
        start = len(text)
        text += s
        a, b = start, len(text)
        while a < b and text[a].isspace():
            a += 1
        while b > a and text[b - 1].isspace():
            b -= 1
        spans.append((a, b))
    return text, spans


def _lineage(dataset: str, title: str) -> str:
    return f"{dataset}:title:{normalize_title(title)}"


def _src(spec: DatasetSpec, split: str, idx: int) -> SourceRef:
    return SourceRef(
        dataset=spec.name, split=split, source_repo=spec.repo, source_revision=spec.revision,
        source_file=spec.raw["splits"][split]["file"], row_index=idx,
    )


def _answer_type(ans: str) -> str:
    return "yes_no" if ans.strip().lower() in {"yes", "no"} else "span"


def _context_passages(dataset: str, qid: str, titles, sentences) -> list[Passage]:
    out = []
    for pos, (t, sents) in enumerate(zip(titles, sentences)):
        text, spans = _join_sentences(list(sents))
        out.append(Passage(
            passage_id=passage_id(dataset, qid, pos), title=str(t), text=text, sentence_spans=spans,
            segmentation="dataset", segmentation_status=S.DATASET_SUPPLIED, position=pos,
            lineage_id=_lineage(dataset, str(t)),
        ))
    return out


def _map_supporting(passages: list[Passage], titles, sent_ids, notes: dict[str, str]) -> list[SupportingFact]:
    by_title: dict[str, list[Passage]] = {}
    for p in passages:
        by_title.setdefault(p.title, []).append(p)
    facts: list[SupportingFact] = []
    dropped = []
    for t, i in zip(titles, sent_ids):
        cands = by_title.get(str(t), [])
        if not cands:
            dropped.append(f"{t}#missing_title")
            continue
        if len(cands) > 1:
            notes["supporting_title_ambiguous"] = f"title '{t}' occurs {len(cands)}x; mapped to first"
        p = cands[0]
        i = int(i)
        if not 0 <= i < p.n_sentences:
            dropped.append(f"{t}#{i}#out_of_range")
            continue
        sf = SupportingFact(passage_id=p.passage_id, sentence_index=i, status=S.DATASET_SUPPLIED)
        if sf not in facts:
            facts.append(sf)
    if dropped:
        notes["supporting_facts_dropped"] = ";".join(dropped)
    return facts


def _sentences_by_passage(facts: list[SupportingFact]) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    for f in facts:
        if f.sentence_index is not None:
            out.setdefault(f.passage_id, []).append(f.sentence_index)
    return out


def _hop_count_from_facts(facts: list[SupportingFact]) -> int:
    return len({f.passage_id for f in facts})


# ----------------------------------------------------------------------------- HotpotQA


def _hotpot_steps(q_type: str, passages: list[Passage], facts: list[SupportingFact],
                  notes: dict[str, str]) -> tuple[list[ReasoningStep], S]:
    by_p = _sentences_by_passage(facts)
    gold = list(by_p)
    if len(gold) != 2:
        notes["reasoning_order"] = f"expected 2 gold passages, found {len(gold)}"
        return [], S.UNAVAILABLE
    pm = {p.passage_id: p for p in passages}
    a, b = gold
    if q_type == "comparison":
        notes["reasoning_order"] = "comparison: two parallel steps, no dependency (R-HPQ)"
        return [ReasoningStep(index=i, passage_ids=[pid], sentence_indices={pid: by_p[pid]})
                for i, pid in enumerate(gold)], S.DETERMINISTIC_DERIVED

    def mentions(src: str, dst: str, full: bool) -> bool:
        p = pm[src]
        text = p.text if full else " ".join(p.sentence(i) for i in by_p[src])
        return contains_phrase(text, normalize_title(pm[dst].title))

    for full in (False, True):
        ab, ba = mentions(a, b, full), mentions(b, a, full)
        if ab != ba:
            first, second = (a, b) if ab else (b, a)
            notes["reasoning_order"] = f"bridge via title mention ({'passage' if full else 'supporting sentences'}) (R-HPQ)"
            bridge = re.sub(r"\s*\([^)]*\)\s*$", "", pm[second].title)  # bridge entity = answer of step 0
            return [
                ReasoningStep(index=0, passage_ids=[first], sentence_indices={first: by_p[first]}, sub_answer=bridge),
                ReasoningStep(index=1, passage_ids=[second], sentence_indices={second: by_p[second]}, depends_on=[0]),
            ], S.DETERMINISTIC_DERIVED
    notes["reasoning_order"] = "bridge order not determinable by rule R-HPQ"
    return [], S.UNAVAILABLE


def load_hotpotqa(spec: DatasetSpec, split: str, data_root: Path) -> Iterator[Question]:
    import pandas as pd

    df = pd.read_parquet(spec.file_for(split, data_root))
    for idx, r in enumerate(df.itertuples(index=False)):
        notes: dict[str, str] = {}
        passages = _context_passages("hotpotqa", r.id, r.context["title"], r.context["sentences"])
        facts = _map_supporting(passages, r.supporting_facts["title"], r.supporting_facts["sent_id"], notes)
        steps, st = _hotpot_steps(r.type, passages, facts, notes)
        yield Question(
            uid=f"hotpotqa/{r.id}", qid=r.id, dataset="hotpotqa", split=split, task="qa",
            question=r.question, answers=[r.answer], answer_type=_answer_type(r.answer),
            question_type=r.type, hop_count=_hop_count_from_facts(facts), passages=passages,
            supporting_facts=facts, reasoning_steps=steps,
            annotations={
                "answer": S.DATASET_SUPPLIED, "supporting_passages": S.DATASET_SUPPLIED,
                "supporting_sentences": S.DATASET_SUPPLIED, "sentence_segmentation": S.DATASET_SUPPLIED,
                "hop_count": S.DETERMINISTIC_DERIVED, "reasoning_order": st,
                "depends_on_edges": st,
                **NO_GOLD_EDGES,
            },
            annotation_notes=notes, source=_src(spec, split, idx),
        )


# ----------------------------------------------------------------------------- 2Wiki


def _twowiki_steps(evidences, passages: list[Passage], facts: list[SupportingFact],
                   notes: dict[str, str]) -> tuple[list[ReasoningStep], S]:
    by_p = _sentences_by_passage(facts)
    pm = {p.passage_id: p for p in passages}
    steps: list[ReasoningStep] = []
    triples = [[str(x) for x in t] for t in evidences]
    if not triples:
        notes["reasoning_order"] = "no evidence triples"
        return [], S.UNAVAILABLE
    for i, (subj, rel, obj) in enumerate(triples):
        ns = normalize_title(subj)
        match = [pid for pid in by_p if normalize_title(pm[pid].title) == ns]
        if not match:
            match = [pid for pid in by_p if ns and (ns in normalize_title(pm[pid].title))]
        if len(match) != 1:
            notes["reasoning_order"] = f"triple {i} subject '{subj}' maps to {len(match)} gold passages (R-2WK)"
            return [], S.UNAVAILABLE
        pid = match[0]
        deps = [j for j, (_, _, o) in enumerate(triples[:i]) if normalize_title(o) == ns]
        steps.append(ReasoningStep(index=i, passage_ids=[pid], sentence_indices={pid: by_p[pid]},
                                   triple=[subj, rel, obj], depends_on=deps, sub_answer=obj))
    notes["reasoning_order"] = "evidence-triple order; deps by subject==previous object (R-2WK)"
    return steps, S.DETERMINISTIC_DERIVED


def load_2wiki(spec: DatasetSpec, split: str, data_root: Path) -> Iterator[Question]:
    import pandas as pd

    df = pd.read_parquet(spec.file_for(split, data_root))
    for idx, r in enumerate(df.itertuples(index=False)):
        notes: dict[str, str] = {}
        passages = _context_passages("2wikimultihopqa", r.id, r.context["title"], r.context["sentences"])
        facts = _map_supporting(passages, r.supporting_facts["title"], r.supporting_facts["sent_id"], notes)
        steps, st = _twowiki_steps(r.evidences, passages, facts, notes)
        yield Question(
            uid=f"2wikimultihopqa/{r.id}", qid=r.id, dataset="2wikimultihopqa", split=split, task="qa",
            question=r.question, answers=[r.answer], answer_type=_answer_type(r.answer),
            question_type=r.type, hop_count=_hop_count_from_facts(facts), passages=passages,
            supporting_facts=facts, reasoning_steps=steps,
            annotations={
                "answer": S.DATASET_SUPPLIED, "supporting_passages": S.DATASET_SUPPLIED,
                "supporting_sentences": S.DATASET_SUPPLIED, "sentence_segmentation": S.DATASET_SUPPLIED,
                "evidence_triples": S.DATASET_SUPPLIED, "hop_count": S.DETERMINISTIC_DERIVED,
                "reasoning_order": st, "depends_on_edges": st,
                **NO_GOLD_EDGES,
            },
            annotation_notes=notes, source=_src(spec, split, idx),
        )


# ----------------------------------------------------------------------------- MuSiQue


_REF = re.compile(r"#(\d+)")


def load_musique(spec: DatasetSpec, split: str, data_root: Path) -> Iterator[Question]:
    with open(spec.file_for(split, data_root)) as f:
        for idx, line in enumerate(f):
            r = json.loads(line)
            qid = r["id"]
            notes: dict[str, str] = {}
            passages = []
            for p in r["paragraphs"]:
                text = p["paragraph_text"]
                passages.append(Passage(
                    passage_id=passage_id("musique", qid, p["idx"]), title=p["title"], text=text,
                    sentence_spans=split_sentences(text), segmentation=SENTENCE_SPLITTER_ID,
                    segmentation_status=S.DETERMINISTIC_DERIVED, position=p["idx"],
                    lineage_id=_lineage("musique", p["title"]),
                ))
            facts = [SupportingFact(passage_id=passage_id("musique", qid, p["idx"]), sentence_index=None,
                                    status=S.DATASET_SUPPLIED) for p in r["paragraphs"] if p["is_supporting"]]
            steps = []
            for i, d in enumerate(r["question_decomposition"]):
                pid = passage_id("musique", qid, d["paragraph_support_idx"])
                deps = sorted({int(m) - 1 for m in _REF.findall(d["question"]) if 0 < int(m) <= i})
                steps.append(ReasoningStep(index=i, passage_ids=[pid], sub_question=d["question"],
                                           sub_answer=d["answer"], depends_on=deps))
            notes["reasoning_order"] = "decomposition order; deps from '#k' references (R-MSQ)"
            yield Question(
                uid=f"musique/{qid}", qid=qid, dataset="musique", split=split, task="qa",
                question=r["question"], answers=[r["answer"], *r.get("answer_aliases", [])],
                answer_type=_answer_type(r["answer"]), question_type=qid.split("__")[0],
                hop_count=len(steps), passages=passages, supporting_facts=facts, reasoning_steps=steps,
                annotations={
                    "answer": S.DATASET_SUPPLIED, "supporting_passages": S.DATASET_SUPPLIED,
                    "supporting_sentences": S.UNAVAILABLE, "sentence_segmentation": S.DETERMINISTIC_DERIVED,
                    "decomposition": S.DATASET_SUPPLIED, "hop_count": S.DATASET_SUPPLIED,
                    "reasoning_order": S.DATASET_SUPPLIED, "depends_on_edges": S.DETERMINISTIC_DERIVED,
                    **NO_GOLD_EDGES,
                },
                annotation_notes=notes, source=_src(spec, split, idx),
            )


# ----------------------------------------------------------------------------- HoVer


def load_hover(spec: DatasetSpec, split: str, data_root: Path, registry: dict[str, DatasetSpec]) -> Iterator[Question]:
    hp = {q.qid: q for q in load_hotpotqa(registry["hotpotqa"], "dev", data_root)}
    with open(spec.file_for(split, data_root)) as f:
        rows = json.load(f)
    for idx, r in enumerate(rows):
        src_q = hp.get(r["hpqa_id"])
        if src_q is None:
            continue
        titles = {p.title for p in src_q.passages}
        if not all(t in titles for t, _ in r["supporting_facts"]):
            continue
        qid = r["uid"]
        notes: dict[str, str] = {"passage_text": f"recovered from HotpotQA dev context of {r['hpqa_id']} (R-HOV)"}
        passages = [p.model_copy(update={"passage_id": passage_id("hover", qid, p.position),
                                         "lineage_id": _lineage("hover", p.title)}) for p in src_q.passages]
        facts = _map_supporting(passages, [t for t, _ in r["supporting_facts"]], [i for _, i in r["supporting_facts"]], notes)
        if len(facts) != len(r["supporting_facts"]):
            continue  # a supporting sentence could not be recovered; skip rather than guess
        yield Question(
            uid=f"hover/{qid}", qid=qid, dataset="hover", split=split, task="verification",
            question=r["claim"], answers=[r["label"]], answer_type="verdict",
            label_set=["SUPPORTED", "NOT_SUPPORTED"], question_type=f"{r['num_hops']}hop",
            hop_count=int(r["num_hops"]), passages=passages, supporting_facts=facts,
            annotations={
                "answer": S.DATASET_SUPPLIED, "supporting_sentences": S.DATASET_SUPPLIED,
                "supporting_passages": S.DATASET_SUPPLIED, "passage_text": S.DETERMINISTIC_DERIVED,
                "sentence_segmentation": S.DATASET_SUPPLIED, "hop_count": S.DATASET_SUPPLIED,
                "reasoning_order": S.UNAVAILABLE, "depends_on_edges": S.UNAVAILABLE, **NO_GOLD_EDGES,
            },
            annotation_notes=notes, source=_src(spec, split, idx),
        )


# ----------------------------------------------------------------------------- FEVER


def _fever_title(page: str) -> str:
    rep = {"-LRB-": "(", "-RRB-": ")", "-LSB-": "[", "-RSB-": "]", "-COLON-": ":", "_": " "}
    for k, v in rep.items():
        page = page.replace(k, v)
    return page


def _fever_text(t: str) -> str:
    t = t.replace("-LRB-", "(").replace("-RRB-", ")").replace("-LSB-", "[").replace("-RSB-", "]")
    return re.sub(r"\s+([,.;:!?)\]])", r"\1", re.sub(r"([(\[])\s+", r"\1", t)).strip()


def fever_passage(page: str, line: str | int, text: str, position: int = 0) -> Passage:
    """FEVER sentences are content-addressed by (page, line) so ids are shared between a
    claim's evidence and the split-wide retrieval pool."""
    clean = _fever_text(text)
    return Passage(
        passage_id=f"fever/sent/{stable_hash([page, str(line)], 12)}", title=_fever_title(page), text=clean,
        sentence_spans=[(0, len(clean))], segmentation="dataset", segmentation_status=S.DATASET_SUPPLIED,
        position=position, lineage_id=f"fever:page:{page}",
    )


def load_fever(spec: DatasetSpec, split: str, data_root: Path) -> Iterator[Question]:
    with open(spec.file_for(split, data_root)) as f:
        for idx, line in enumerate(f):
            r = json.loads(line)
            label = r["label"]
            passages, facts = [], []
            gold_status = S.MODEL_PREDICTED if label == "NOT ENOUGH INFO" else S.DATASET_SUPPLIED
            for pos, (page, ln, text) in enumerate(r["evidence"]):
                p = fever_passage(page, ln, text, pos)
                if any(x.passage_id == p.passage_id for x in passages):
                    continue
                passages.append(p)
                facts.append(SupportingFact(passage_id=p.passage_id, sentence_index=0, status=gold_status))
            yield Question(
                uid=f"fever/{r['id']}", qid=r["id"], dataset="fever", split=split, task="verification",
                question=r["claim"], answers=[label], answer_type="verdict",
                label_set=["SUPPORTS", "REFUTES", "NOT ENOUGH INFO"], question_type=label,
                hop_count=len({p.lineage_id for p in passages}), passages=passages, supporting_facts=facts,
                annotations={
                    "answer": S.DATASET_SUPPLIED, "supporting_sentences": gold_status,
                    "supporting_passages": gold_status, "sentence_segmentation": S.DATASET_SUPPLIED,
                    "hop_count": S.DETERMINISTIC_DERIVED, "reasoning_order": S.UNAVAILABLE,
                    "depends_on_edges": S.UNAVAILABLE, **NO_GOLD_EDGES,
                },
                annotation_notes={"evidence": "NEI evidence is system-retrieved (not gold)" if label == "NOT ENOUGH INFO"
                                  else "human-annotated FEVER evidence as packaged by copenlu"},
                source=_src(spec, split, idx),
            )


def load_fever_corpus(spec: DatasetSpec, split: str, data_root: Path) -> list[Passage]:
    """Split-wide pool of evidence sentences (deduplicated) used as FEVER's retrieval corpus."""
    seen: dict[str, Passage] = {}
    with open(spec.file_for(split, data_root)) as f:
        for line in f:
            for page, ln, text in json.loads(line)["evidence"]:
                p = fever_passage(page, ln, text, len(seen))
                seen.setdefault(p.passage_id, p)
    return list(seen.values())


# ----------------------------------------------------------------------------- public API


def iter_questions(name: str, split: str, data_root: str | Path = DEFAULT_DATA_ROOT,
                   registry: dict[str, DatasetSpec] | None = None) -> Iterator[Question]:
    registry = registry or load_registry()
    data_root = Path(data_root)
    if name not in registry:
        raise DataUnavailableError(f"unknown dataset '{name}'")
    spec = registry[name]
    path = spec.file_for(split, data_root)
    if not path.exists():
        raise DataUnavailableError(f"{name}/{split}: {path} missing; run `wsh data fetch --dataset {name}`")
    loaders: dict[str, Callable[..., Iterator[Question]]] = {
        "hotpotqa": load_hotpotqa, "2wikimultihopqa": load_2wiki, "musique": load_musique, "fever": load_fever,
    }
    if name == "hover":
        yield from load_hover(spec, split, data_root, registry)
    else:
        yield from loaders[name](spec, split, data_root)


def sample_questions(name: str, split: str, n: int, seed: int, qids: list[str] | None = None,
                     data_root: str | Path = DEFAULT_DATA_ROOT, stratify_by: str | None = None,
                     registry: dict[str, DatasetSpec] | None = None) -> list[Question]:
    """Deterministic sample. With ``qids`` the exact questions are returned in that order.

    Sampling is a seeded shuffle of the full split (optionally round-robin over strata);
    the selected qids are recorded in every run manifest.
    """
    if split == "test":
        raise DataUnavailableError("test splits are not used by this framework")
    all_q = list(iter_questions(name, split, data_root, registry))
    if qids:
        idx = {q.qid: q for q in all_q}
        missing = [x for x in qids if x not in idx]
        if missing:
            raise DataUnavailableError(f"{name}: qids not found: {missing[:5]}")
        return [idx[x] for x in qids]
    rng = random.Random(seed)
    order = list(range(len(all_q)))
    rng.shuffle(order)
    if not stratify_by:
        return [all_q[i] for i in order[:n]]
    strata: dict[Any, list[int]] = {}
    for i in order:
        strata.setdefault(getattr(all_q[i], stratify_by), []).append(i)
    keys = sorted(strata, key=str)
    picked: list[int] = []
    while len(picked) < min(n, len(all_q)):
        for k in keys:
            if strata[k] and len(picked) < n:
                picked.append(strata[k].pop(0))
    return [all_q[i] for i in picked]
