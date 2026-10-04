"""Turn per-pair scores into the headline numbers: at each threshold, how many
should-hit pairs are served from cache and how many traps get a wrong answer."""
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
TRAPS = ["negation", "entity_swap", "number_date", "scope"]
HITS = ["near_repeat", "paraphrase"]
# Each scorer at the threshold its library ships with (embeddings without a library
# default are shown at 0.90, RedisVL's cosine-similarity equivalent).
DEFAULTS = {
    "gptcache-default": (0.80, "GPTCache defaults (ONNX albert, threshold 0.8)"),
    "embed-langcache-embed-v1": (0.90, "RedisVL defaults (langcache-embed-v1, distance 0.1)"),
    "embed-all-mpnet-base-v2": (0.90, "all-mpnet-base-v2 (old RedisVL default) at 0.90"),
    "embed-all-MiniLM-L6-v2": (0.90, "all-MiniLM-L6-v2 at 0.90"),
    "embed-bge-small-en-v1.5": (0.90, "bge-small-en-v1.5 at 0.90"),
    "jev": (0.50, "Jev yes/no check, detailed prompt, 0.5"),
    "jev-neutral": (0.50, "Jev yes/no check, one-line prompt, 0.5"),
}


def load(path):
    style = {p["id"]: p["style"] for p in map(json.loads, open(ROOT / "data" / "pairs.jsonl"))}
    with open(path) as f:
        return [dict(r, score=float(r["score"]), same=r["same_answer"] == "True", style=style[r["id"]]) for r in csv.DictReader(f)]


def frac(rows, t, pred):
    sel = [r for r in rows if pred(r)]
    return sum(r["score"] >= t for r in sel) / len(sel) if sel else float("nan")


def best_hit_at(rows, max_false):
    best = (0.0, None)
    for i in range(1001):
        t = i / 1000
        hit, fh = frac(rows, t, lambda r: r["same"]), frac(rows, t, lambda r: not r["same"])
        if fh <= max_false and hit > best[0]:
            best = (hit, t)
    return best


def main():
    pairs = [json.loads(line) for line in open(ROOT / "data" / "pairs.jsonl")]
    n_hit = sum(p["same_answer"] for p in pairs)
    lines = ["# fow-cache results", "",
             f"{len(pairs)} pairs: {n_hit} that should be served from cache (near-verbatim repeats and paraphrases), "
             f"{len(pairs) - n_hit} traps that need a different answer.", "",
             "## Each scorer at its default threshold", "",
             "| scorer | should-hit served | near repeats | paraphrases | traps given a wrong answer | negation | entity swap | number/date | scope | one-word-edit traps | reworded traps |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    fig, ax = plt.subplots(figsize=(7, 5))
    summary = []
    for name, (t, label) in DEFAULTS.items():
        path = ROOT / "results" / "scores" / f"{name}.csv"
        if not path.exists():
            continue
        rows = load(path)
        cells = [frac(rows, t, lambda r: r["same"])]
        cells += [frac(rows, t, lambda r, c=c: r["category"] == c) for c in HITS]
        cells += [frac(rows, t, lambda r: not r["same"])]
        cells += [frac(rows, t, lambda r, c=c: r["category"] == c) for c in TRAPS]
        cells += [frac(rows, t, lambda r, s=s: not r["same"] and r["style"] == s) for s in ("minimal", "reworded")]
        lines.append(f"| {label} | " + " | ".join(f"{c:.0%}" for c in cells) + " |")
        curve = [(frac(rows, i / 200, lambda r: r["same"]), frac(rows, i / 200, lambda r: not r["same"])) for i in range(201)]
        ax.plot([c[1] for c in curve], [c[0] for c in curve], label=label)
        summary.append((label, best_hit_at(rows, 0.01), best_hit_at(rows, 0.05)))
    lines += ["", "## Best should-hit rate with wrong answers capped (any threshold)", "",
              "| scorer | at <=1% wrong answers (threshold) | at <=5% wrong answers (threshold) |", "|---|---|---|"]
    for label, one, five in summary:
        lines.append(f"| {label} | {one[0]:.0%} ({one[1]}) | {five[0]:.0%} ({five[1]}) |")
    ax.set_xlabel("traps given a wrong cached answer")
    ax.set_ylabel("should-hit questions served from cache")
    ax.set_title("Every threshold, every scorer")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(ROOT / "results" / "tradeoff.png", dpi=160)
    (ROOT / "results" / "README.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
