"""Honest numbers for the conversation benchmark: thresholds are picked on one half of
the pairs and scored on the other (two-fold, split within each subtype x length group),
so every pair is scored once by thresholds that never saw it. Covers single strategies
and "serve only if both agree" combinations. Writes results/CONVERSATIONS_HELDOUT.md."""
import csv
import hashlib
import itertools
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCORES = ROOT / "results" / "conv-scores"
GRID = [i / 20 for i in range(1, 20)]  # 0.05 ... 0.95
TARGETS = [0.01, 0.05]  # max wrong-answer rate allowed on the tuning half

SINGLES = {
    "full-jev": "Whole conversation",
    "hybrid-jev": "Hybrid (facts + last 7)",
    "facts-jev": "Running facts v1",
    "rewrite-jev": "Rewrite from whole transcript",
    "rewrite-lite-jev": "Rewrite from facts + last 7",
    "rewrite-window-jev": "Rewrite from last 7 only",
    "rewrite-batch-jev": "Rewrite from batched facts + recent",
    "rewrite-batch2-jev": "Rewrite, facts every 2 exchanges",
    "rewrite-batch8-jev": "Rewrite, facts every 8 exchanges",
}
COMBOS = [
    ("full-jev", "rewrite-jev"),
    ("full-jev", "rewrite-lite-jev"),
    ("hybrid-jev", "rewrite-lite-jev"),
    ("full-jev", "rewrite-window-jev"),
    ("full-jev", "rewrite-batch-jev"),
    ("full-jev", "rewrite-batch2-jev"),
    ("full-jev", "rewrite-batch8-jev"),
]


def load(name):
    with open(SCORES / f"{name}.csv") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def folds(rows):
    """Deterministic 50/50 split inside each subtype x length group."""
    groups = defaultdict(list)
    for r in rows.values():
        groups[(r["subtype"], r["length"])].append(r["id"])
    fold = {}
    for ids in groups.values():
        for i, id_ in enumerate(sorted(ids, key=lambda x: hashlib.sha1(x.encode()).hexdigest())):
            fold[id_] = i % 2
    return fold


def rates(ids, serve, meta):
    hits = [i for i in ids if meta[i]["same_answer"] == "True"]
    traps = [i for i in ids if meta[i]["same_answer"] == "False"]
    return (sum(serve(i) for i in hits) / len(hits) if hits else float("nan"),
            sum(serve(i) for i in traps) / len(traps) if traps else float("nan"))


def tune(ids, make_serve, n_thresholds, meta, target):
    """Thresholds maximising hits on ids with wrong answers <= target (ties: fewer wrong)."""
    best = None
    for ts in itertools.product(GRID, repeat=n_thresholds):
        hit, wrong = rates(ids, make_serve(ts), meta)
        if wrong <= target and (best is None or (hit, -wrong) > best[0]):
            best = ((hit, -wrong), ts)
    return best[1] if best else (1.01,) * n_thresholds  # nothing qualifies: never serve


def evaluate(names, scores, meta, fold, target):
    def make_serve(ts):
        return lambda i: all(float(scores[n][i]["score"]) >= t for n, t in zip(names, ts))
    served = {}
    chosen = []
    for k in (0, 1):
        tune_ids = [i for i in meta if fold[i] == k]
        test_ids = [i for i in meta if fold[i] != k]
        ts = tune(tune_ids, make_serve, len(names), meta, target)
        chosen.append(ts)
        serve = make_serve(ts)
        served.update({i: serve(i) for i in test_ids})
    everything = list(meta)
    very_long = [i for i in meta if meta[i]["length"] == "very_long"]
    return (rates(everything, served.get, meta), rates(very_long, served.get, meta), chosen)


def main():
    # Direct-API reruns (bench/conversations.py --suffix -api) are reported alongside.
    for base in list(SINGLES):
        if (SCORES / f"{base}-api.csv").exists():
            SINGLES[f"{base}-api"] = SINGLES[base] + " [API, temp 0]"
    for a, b in list(COMBOS):
        if (SCORES / f"{b}-api.csv").exists():
            COMBOS.append((a, f"{b}-api"))
    names = set(SINGLES) | {n for c in COMBOS for n in c}
    scores = {n: load(n) for n in names}
    meta = scores["full-jev"]
    fold = folds(meta)
    n_traps = sum(r["same_answer"] == "False" for r in meta.values())
    lines = ["# fow-cache: conversations, held-out", "",
             f"{len(meta)} pairs ({n_traps} traps). Two-fold: thresholds tuned on one half to keep wrong "
             "answers under the target, then scored on the other half; every pair is scored once.", ""]
    for target in TARGETS:
        lines += [f"## Tuned for <= {target:.0%} wrong answers", "",
                  "| strategy | hits served | traps wrong | very long: hits | very long: wrong | thresholds (fold 1 / fold 2) |",
                  "|---|---|---|---|---|---|"]
        rows = [(SINGLES[n], (n,)) for n in SINGLES]
        rows += [(f"{SINGLES[a]} AND {SINGLES[b]}", (a, b)) for a, b in COMBOS]
        for label, combo in rows:
            (h, w), (vh, vw), chosen = evaluate(combo, scores, meta, fold, target)
            ts = " / ".join(",".join(f"{t:.2f}" for t in c) for c in chosen)
            lines.append(f"| {label} | {h:.0%} | {w:.0%} | {vh:.0%} | {vw:.0%} | {ts} |")
        lines.append("")
    out = "\n".join(lines)
    (ROOT / "results" / "CONVERSATIONS_HELDOUT.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
