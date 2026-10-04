"""Headline numbers for the conversation benchmark: per strategy, how many should-hit
pairs are served from cache and how many traps get a wrong answer, by subtype and by
conversation length. Writes results/CONVERSATIONS.md."""
import csv
from pathlib import Path

from report import best_hit_at, frac

ROOT = Path(__file__).resolve().parent.parent
TRAPS = ["context_swap", "detail_swap", "intent_flip"]
HITS = ["same_context_reworded", "irrelevant_history", "same_context_extra_chatter"]
LENGTHS = ["short", "medium", "long", "very_long"]
STRATEGIES = {
    "last-langcache": (0.90, "Last message only, RedisVL default embedder (0.90)"),
    "last-mpnet": (0.90, "Last message only, all-mpnet-base-v2 (0.90)"),
    "last-jev": (0.50, "Last message only, Jev"),
    "full-jev": (0.50, "Whole conversations, Jev"),
    "window-jev": (0.50, "Last 7 messages only, Jev"),
    "notes-jev": (0.50, "4-5 word notes per exchange + last message, Jev"),
    "facts-jev": (0.50, "Running facts + last message, Jev"),
    "facts2-jev": (0.50, "Running facts v2 (goal, fixed keys) + previous reply + last message, Jev"),
    "facts3-jev": (0.50, "Running facts v2 + previous reply + last message, Jev asked what the final message depends on"),
    "hybrid-jev": (0.50, "Hybrid: facts v2 for older turns + last 7 messages verbatim, Jev"),
    "rewrite-langcache": (0.90, "Standalone rewrite, RedisVL default embedder (0.90)"),
    "rewrite-mpnet": (0.90, "Standalone rewrite, all-mpnet-base-v2 (0.90)"),
    "rewrite-jev": (0.50, "Standalone rewrite, Jev"),
    "rewrite-lite-jev": (0.50, "Standalone rewrite from facts + last 7 messages, Jev"),
    "rewrite-window-jev": (0.50, "Standalone rewrite from last 7 messages only, Jev"),
    "rewrite-batch-jev": (0.50, "Standalone rewrite from batched facts (every 4 exchanges) + recent messages, Jev"),
    "rewrite-batch2-jev": (0.50, "Standalone rewrite, facts every 2 exchanges, Jev"),
    "rewrite-batch8-jev": (0.50, "Standalone rewrite, facts every 8 exchanges, Jev"),
}


def load(path):
    with open(path) as f:
        return [dict(r, score=float(r["score"]), same=r["same_answer"] == "True") for r in csv.DictReader(f)]


def pct(x):
    return "n/a" if x != x else f"{x:.0%}"


def main():
    rows_by = {n: load(ROOT / "results" / "conv-scores" / f"{n}.csv")
               for n in STRATEGIES if (ROOT / "results" / "conv-scores" / f"{n}.csv").exists()}
    if not rows_by:
        raise SystemExit("no scores yet: run bench/conversations.py first")
    any_rows = next(iter(rows_by.values()))
    n_hit = sum(r["same"] for r in any_rows)
    lines = ["# fow-cache: conversations", "",
             f"{len(any_rows)} pairs of conversations: {n_hit} should be served from cache, "
             f"{len(any_rows) - n_hit} are traps where the final messages match but earlier context changes the answer.", "",
             "## Each strategy at its default threshold", "",
             "| strategy | should-hit served | " + " | ".join(h.replace("_", " ") for h in HITS)
             + " | traps given a wrong answer | " + " | ".join(t.replace("_", " ") for t in TRAPS) + " |",
             "|---|" + "---|" * (2 + len(HITS) + len(TRAPS))]
    by_len = ["", "## Wrong answers and hits by conversation length", "",
              "| strategy | " + " | ".join(f"traps wrong, {l}" for l in LENGTHS) + " | "
              + " | ".join(f"hits served, {l}" for l in LENGTHS) + " | median latency |",
              "|---|" + "---|" * (2 * len(LENGTHS) + 1)]
    capped = ["", "## Best should-hit rate with wrong answers capped (any threshold)", "",
              "| strategy | at <=1% wrong (threshold) | at <=5% wrong (threshold) |", "|---|---|---|"]
    for name, rows in rows_by.items():
        t, label = STRATEGIES[name]
        cells = [frac(rows, t, lambda r: r["same"])]
        cells += [frac(rows, t, lambda r, s=s: r["subtype"] == s) for s in HITS]
        cells += [frac(rows, t, lambda r: not r["same"])]
        cells += [frac(rows, t, lambda r, s=s: r["subtype"] == s) for s in TRAPS]
        lines.append(f"| {label} | " + " | ".join(pct(c) for c in cells) + " |")
        lc = [frac(rows, t, lambda r, l=l: not r["same"] and r["length"] == l) for l in LENGTHS]
        lc += [frac(rows, t, lambda r, l=l: r["same"] and r["length"] == l) for l in LENGTHS]
        lat = sorted(float(r["latency_s"]) for r in rows if r["latency_s"])
        by_len.append(f"| {label} | " + " | ".join(pct(c) for c in lc)
                      + f" | {f'{lat[len(lat)//2]*1000:.0f} ms' if lat else 'local'} |")
        one, five = best_hit_at(rows, 0.01), best_hit_at(rows, 0.05)
        capped.append(f"| {label} | {pct(one[0])} ({one[1]}) | {pct(five[0])} ({five[1]}) |")
    out = "\n".join(lines + by_len + capped) + "\n"
    (ROOT / "results" / "CONVERSATIONS.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
