"""Tolerant parsing of generator output.

Expected format (requested by the prompt, NOT required for scoring):
    Answer: <short answer>
    Evidence: E1, E3

* The answer is taken from the first 'Answer:' field; if absent, from the first non-empty
  line that is not an 'Evidence:' line (flag ``format_deviation``).
* Citations are every E<n> token anywhere in the output. Citations to ids not present in the
  prompt are *invalid citations*: recorded separately and never turn a correct answer into a
  failure (fix for the original validator, which converted them into failed runs).
* Verification verdicts are mapped onto the dataset label set by keyword rules; output that
  matches no label (e.g. a free-form statement) is ``unparseable_verdict``.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from ..text import normalize_answer

_ANSWER = re.compile(r"(?im)^\s*[\[*#>\-\s]*(?:final\s+)?answer\s*[*]*\s*[:：]\s*(.*?)\]?\s*$")
_EVID_LINE = re.compile(r"(?im)^\s*[*\-\s]*(evidence|citations?|sources?)\s*[*]*\s*[:：]")
_CITE = re.compile(r"\bE\s?(\d{1,3})\b")
ABSTAIN_PATTERNS = [
    r"\binsufficient (?:evidence|information)\b", r"\bnot enough (?:evidence|information)\b",
    r"\bcannot be determined\b", r"\bcan ?not determine\b", r"\bunknown\b", r"\bno answer\b",
    r"\bthe evidence does not\b", r"\bnot (?:mentioned|stated|provided)\b",
]
_ABSTAIN = re.compile("|".join(ABSTAIN_PATTERNS), re.I)

VERDICT_RULES = {
    # order matters: NEI before REFUTES/SUPPORTS because "not enough info" contains "not"
    "NOT ENOUGH INFO": [r"not\s+enough\s+info", r"\bnei\b", r"insufficient", r"cannot be (?:verified|determined)", r"unverifiable"],
    "NOT_SUPPORTED": [r"not[_\s]+supported", r"\bunsupported\b", r"\brefute[sd]?\b", r"\bfalse\b"],
    "REFUTES": [r"\brefute[sd]?\b", r"\bfalse\b", r"\bcontradict", r"not\s+supported", r"\bincorrect\b"],
    "SUPPORTS": [r"\bsupport(?:s|ed)?\b", r"\btrue\b", r"\bcorrect\b"],
    "SUPPORTED": [r"\bsupport(?:s|ed)?\b", r"\btrue\b", r"\bcorrect\b"],
}


@dataclass
class ParsedOutput:
    answer: str | None
    answer_source: str | None  # field | fallback_line | None
    cited: list[str] = field(default_factory=list)
    invalid_cited: list[str] = field(default_factory=list)
    abstained: bool = False
    verdict: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _clean_answer(a: str) -> str:
    a = re.sub(r"\[?\bE\s?\d{1,3}\b\]?", "", a)
    a = re.sub(r"\(\s*[,;\s]*\)", "", a)
    a = a.strip().strip("*").strip()
    a = re.sub(r"[\s.;,]+$", "", a)
    return a.strip().strip('"').strip()


def map_verdict(text: str, label_set: list[str]) -> str | None:
    t = text.strip()
    for lab in label_set:  # exact label first
        if normalize_answer(t) == normalize_answer(lab) or normalize_answer(t).replace(" ", "_") == lab.lower():
            return lab
    for lab in sorted(label_set, key=lambda x: list(VERDICT_RULES).index(x) if x in VERDICT_RULES else 99):
        for pat in VERDICT_RULES.get(lab, []):
            if re.search(pat, t, re.I):
                return lab
    return None


def parse_output(text: str, valid_ids: set[str], label_set: list[str] | None = None) -> ParsedOutput:
    answer, src = None, None
    m = _ANSWER.search(text)
    if m and m.group(1).strip():
        answer, src = _clean_answer(m.group(1)), "field"
    else:
        for line in text.splitlines():
            if line.strip() and not _EVID_LINE.match(line):
                answer, src = _clean_answer(line), "fallback_line"
                break
    if answer == "":
        answer, src = None, None
    cited: list[str] = []
    for n in _CITE.findall(text):
        cid = f"E{int(n)}"
        if cid not in cited:
            cited.append(cid)
    p = ParsedOutput(answer=answer, answer_source=src, cited=cited,
                     invalid_cited=[c for c in cited if c not in valid_ids])
    if answer is not None:
        p.abstained = bool(_ABSTAIN.search(answer))
        if label_set:
            p.verdict = map_verdict(answer, label_set)
            if p.verdict == "NOT ENOUGH INFO":
                p.abstained = False  # a legitimate verdict, not an abstention
    return p
