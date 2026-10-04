"""GPTCache with every setting left at its default (init_similar_cache(): ONNX
paraphrase-albert embedding, sqlite + faiss, SearchDistanceEvaluation, threshold 0.8).

For each pair: a fresh cache, put(a), get(b). A returned answer is a hit. The score
column is GPTCache's own normalised rank, so the report can sweep thresholds; the
`default_hit` column is what the library actually did at its default threshold."""
import os

# faiss and onnxruntime each load OpenMP; on macOS the clash segfaults without these.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import csv
import json
import tempfile
from pathlib import Path

from gptcache import Cache
from gptcache.adapter.api import get, init_similar_cache, put
from gptcache.embedding import Onnx
from gptcache.similarity_evaluation import SearchDistanceEvaluation

ROOT = Path(__file__).resolve().parent.parent


def main():
    with open(ROOT / "data" / "pairs.jsonl") as f:
        pairs = [json.loads(line) for line in f]
    onnx = Onnx()
    # transformers 5 removed encode_plus, which GPTCache 0.1.44 still calls; the
    # tokenizer's __call__ is the documented equivalent and gives identical ids.
    tok = onnx.tokenizer
    tok.encode_plus = lambda text, **kw: tok(text, return_token_type_ids=True, return_attention_mask=True, **kw)
    evaluation = SearchDistanceEvaluation()
    lo, hi = evaluation.range()
    rows = []
    # GPTCache flushes each index at interpreter exit, so keep the dirs until then.
    parent = tempfile.mkdtemp(prefix="fow-cache-gptcache-")
    for i, p in enumerate(pairs):
        d = f"{parent}/{i}"
        Path(d).mkdir()
        if True:  # one fresh cache per pair
            cache = Cache()
            init_similar_cache(data_dir=d, cache_obj=cache, embedding=onnx)
            put(p["a"], f"ANSWER::{p['id']}", cache_obj=cache)
            hit = get(p["b"], cache_obj=cache) == f"ANSWER::{p['id']}"
            # Recompute the rank GPTCache compares against its threshold.
            res = cache.data_manager.search(onnx.to_embeddings(p["b"]), top_k=1)
            rank = evaluation.evaluation({}, {"search_result": res[0]}) if res else lo
            rows.append((p, (rank - lo) / (hi - lo), hit))
    out = ROOT / "results" / "scores" / "gptcache-default.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "category", "same_answer", "score", "default_hit"])
        for p, score, hit in rows:
            w.writerow([p["id"], p["category"], p["same_answer"], f"{score:.4f}", hit])
    agree = sum((s >= 0.8) == h for _, s, h in rows)
    print(f"wrote {out}; score>=0.8 agrees with library get() on {agree}/{len(rows)} pairs")


if __name__ == "__main__":
    main()
