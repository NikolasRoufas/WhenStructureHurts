"""When Structure Hurts: evidence transformations in retrieval-augmented reasoning."""

__version__ = "0.1.0"

# Bump whenever the prompt templates change; it is part of every generation cache key
# and every per-example record.
PROMPT_VERSION = "qa-v2"  # v1->v2 (2026-10-10, smoke debugging): format after question + "Answer:" prefill
