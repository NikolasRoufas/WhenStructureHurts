"""Deterministic text utilities shared across the pipeline.

Everything here is rule-based and documented so that derived annotations
(sentence segmentation, entity mentions, anchors) are reproducible.
"""

from __future__ import annotations

import re
import string
import unicodedata

STOPWORDS = frozenset(
    """a an the of in on at to for from by with and or but is are was were be been being
    as that this these those it its he she they them his her their who whom whose which what
    when where why how did does do has have had not no yes than then there here into about
    over under after before between during also both either neither one two first second
    i you we our your my me us so such can could would should will shall may might must
    """.split()
)

_ARTICLES = re.compile(r"\b(a|an|the)\b", re.UNICODE)
_PUNCT = set(string.punctuation) | {"‘", "’", "“", "”", "–", "—"}
_WORD = re.compile(r"\w+", re.UNICODE)


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def normalize_answer(s: str) -> str:
    """SQuAD-style normalisation: lowercase, drop punctuation and articles, squeeze spaces."""
    s = s.lower()
    s = "".join(ch for ch in s if ch not in _PUNCT)
    s = _ARTICLES.sub(" ", s)
    return " ".join(s.split())


def answer_tokens(s: str) -> list[str]:
    return normalize_answer(s).split()


def word_tokens(s: str) -> list[str]:
    return [t.lower() for t in _WORD.findall(s)]


def content_tokens(s: str) -> list[str]:
    return [t for t in word_tokens(strip_accents(s)) if t not in STOPWORDS]


def jaccard(a: str, b: str) -> float:
    sa, sb = set(content_tokens(a)), set(content_tokens(b))
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / max(1, len(sa | sb))


def lexical_support(claim: str, source: str) -> float:
    """Fraction of the claim's content tokens that occur in the source text."""
    ct = content_tokens(claim)
    if not ct:
        return 0.0
    src = set(content_tokens(source))
    return sum(t in src for t in ct) / len(ct)


def normalize_title(t: str) -> str:
    """Lowercase, strip accents and parenthetical disambiguators: 'Ed Wood (film)' -> 'ed wood'."""
    t = re.sub(r"\s*\([^)]*\)\s*", " ", t)
    return " ".join(word_tokens(strip_accents(t)))


def contains_phrase(haystack: str, needle: str) -> bool:
    """Token-boundary containment after normalisation (accents, case, punctuation)."""
    n = normalize_answer(strip_accents(needle))
    if not n:
        return False
    h = normalize_answer(strip_accents(haystack))
    return f" {n} " in f" {h} "


# --- sentence segmentation (used only where a dataset does not supply sentences) ---

_ABBREV = {
    "mr", "mrs", "ms", "dr", "st", "jr", "sr", "prof", "gen", "col", "lt", "sgt", "capt",
    "inc", "ltd", "co", "corp", "vs", "etc", "no", "vol", "fig", "mt", "ft", "u.s", "e.g", "i.e",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
}
_SENT_END = re.compile(r"[.!?][\"'”’)\]]*\s+(?=[\"'“‘(\[]?[A-Z0-9])")

SENTENCE_SPLITTER_ID = "regex-v1"


def split_sentences(text: str) -> list[tuple[int, int]]:
    """Return (start, end) character offsets of sentences in ``text``.

    Rule: split after ., ! or ? followed by whitespace and an uppercase letter/digit,
    unless the token before the period is a known abbreviation or a single initial.
    Offsets exclude leading/trailing whitespace. Deterministic; documented as
    SENTENCE_SPLITTER_ID in provenance records.
    """
    spans: list[tuple[int, int]] = []
    start = 0
    for m in _SENT_END.finditer(text):
        end = m.start() + 1
        prev = re.search(r"(\S+)$", text[start:end])
        tok = prev.group(1).rstrip(".").lower() if prev else ""
        if tok in _ABBREV or (len(tok) == 1 and tok.isalpha()):
            continue
        # Extend over closing quotes/brackets that belong to this sentence.
        close = re.match(r"[\"'”’)\]]*", text[end:])
        end += len(close.group(0)) if close else 0
        spans.append(_trim(text, start, end))
        start = m.end()
    if start < len(text) and text[start:].strip():
        spans.append(_trim(text, start, len(text)))
    return [s for s in spans if s[1] > s[0]]


def _trim(text: str, s: int, e: int) -> tuple[int, int]:
    while s < e and text[s].isspace():
        s += 1
    while e > s and text[e - 1].isspace():
        e -= 1
    return s, e


# --- heuristic entity mentions (no external NER dependency) ---

_CAP_SEQ = re.compile(
    r"\b(?:[A-Z][\w'\-\.]*|[0-9]{4})(?:\s+(?:of|de|la|le|von|van|der|the|and|&)?\s*[A-Z][\w'\-\.]*)*",
    re.UNICODE,
)
YEAR = re.compile(r"\b(1[0-9]{3}|20[0-9]{2})\b")
_SENT_INITIAL_STOP = {"The", "A", "An", "In", "On", "It", "He", "She", "They", "This", "That", "His", "Her", "Its", "Their", "As", "At", "After", "Before", "During", "When", "While"}

ENTITY_EXTRACTOR_ID = "capseq-v1"


def extract_entities(text: str) -> list[str]:
    """Heuristic entity mentions: capitalised token sequences and four-digit years.

    Sentence-initial function words are dropped. Precision is modest; the output is
    only used for candidate-pair pruning, anchoring and corruption targeting, and is
    always recorded as heuristic.
    """
    out: list[str] = []
    for m in _CAP_SEQ.finditer(text):
        span = m.group(0).strip().rstrip(".")
        words = span.split()
        while words and words[0] in _SENT_INITIAL_STOP:
            words = words[1:]
        if words:
            ent = " ".join(words)
            if ent not in out:
                out.append(ent)
    return out
