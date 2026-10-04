"""Score every pair with embedding cosine similarity, the way a threshold-based
semantic cache decides a hit. Writes one CSV of per-pair scores per model."""
import csv
import json
import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
MODELS = [
    "redis/langcache-embed-v1",  # RedisVL SemanticCache default since 0.6.0
    "sentence-transformers/all-MiniLM-L6-v2",
    "sentence-transformers/all-mpnet-base-v2",
    "BAAI/bge-small-en-v1.5",
]


def load_pairs():
    with open(ROOT / "data" / "pairs.jsonl") as f:
        return [json.loads(line) for line in f]


def main(models):
    pairs = load_pairs()
    out_dir = ROOT / "results" / "scores"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in models:
        model = SentenceTransformer(name)
        a = model.encode([p["a"] for p in pairs], normalize_embeddings=True)
        b = model.encode([p["b"] for p in pairs], normalize_embeddings=True)
        sims = (a * b).sum(axis=1)
        path = out_dir / f"embed-{name.split('/')[-1]}.csv"
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "category", "same_answer", "score"])
            for p, s in zip(pairs, sims):
                w.writerow([p["id"], p["category"], p["same_answer"], f"{s:.4f}"])
        print(f"wrote {path}")


if __name__ == "__main__":
    main(sys.argv[1:] or MODELS)
