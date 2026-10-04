"""Load the bundled benchmark data.

Two datasets:
  questions      single question pairs: categories near_repeat and paraphrase (should hit),
                 negation, entity_swap, number_date and scope (traps)
  conversations  pairs of multi-turn chats whose final user messages match: subtypes
                 same_context_reworded, irrelevant_history, same_context_extra_chatter
                 (should hit), context_swap, detail_swap and intent_flip (traps)

Every item has `same_answer`: true if one reply is correct for both.
"""
import json
from importlib import resources
from pathlib import Path


def _data_dir():
    bundled = resources.files("fow_cache") / "data"
    if bundled.is_dir():
        return Path(str(bundled))
    return Path(__file__).resolve().parent.parent / "data"  # running from a source checkout


def _read_jsonl(paths):
    items = []
    for path in paths:
        with open(path) as f:
            items += [json.loads(line) for line in f if line.strip()]
    return items


def load_questions():
    """List of {id, category, a, b, same_answer, style}: a is the cached question, b the new one."""
    return _read_jsonl([_data_dir() / "pairs.jsonl"])


def load_conversations():
    """List of {id, subtype, a, b, same_answer, note}: a and b are lists of
    {role, content} messages ending with a user message; a is the cached conversation."""
    d = _data_dir()
    return _read_jsonl(sorted((d / "conv-parts").glob("*.jsonl")) + sorted((d / "conv-long").glob("*.jsonl")))


def length_bucket(item):
    n = max(len(item["a"]), len(item["b"]))
    return "short" if n <= 4 else "medium" if n <= 8 else "long" if n <= 20 else "very_long"
