"""End-to-end check of the packaged Guard against real models on a sample of conversation
pairs, compared with the benchmark's combined decision for the same pairs
(full-jev >= 0.70 AND rewrite-batch-jev >= 0.15).

  uv run python bench/guard_live.py --env-file .env --n 20             # Haiku via the Anthropic API
  uv run python bench/guard_live.py --env-file .env --haiku-via claude-cli
"""
import argparse
import csv
import hashlib
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

from conversations import OUT, claude_cli
from jev import load_env_file

from fow_cache import Guard, anthropic_llm, load_conversations
from fow_cache.jev import JevClient


def sample(items, n):
    """n pairs, half traps, spread over lengths, chosen deterministically."""
    key = lambda i: hashlib.sha1(i["id"].encode()).hexdigest()
    by_label = {lab: sorted((i for i in items if i["same_answer"] == lab), key=key) for lab in (True, False)}
    picked = []
    for lab, group in by_label.items():
        longs = [i for i in group if len(i["a"]) > 20][: n // 6]
        picked += longs + [i for i in group if i not in longs][: n // 2 - len(longs)]
    return picked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env-file", action="append", default=[], help="repeatable")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--haiku-via", choices=["anthropic", "claude-cli"], default="anthropic")
    args = ap.parse_args()
    for f in args.env_file:
        load_env_file(f)
    llm = (lambda system, user: claude_cli(system, user)[0]) if args.haiku_via == "claude-cli" else anthropic_llm()
    guard = Guard(llm=llm, jev=JevClient(provider="openrouter"))
    bench = {}
    for name in ("full-jev", "rewrite-batch-jev"):
        with open(OUT / f"{name}.csv") as f:
            for r in csv.DictReader(f):
                bench.setdefault(r["id"], {})[name] = float(r["score"])
    pairs = sample(load_conversations(), args.n)

    latencies = []

    def run(p):
        cached, new = guard.replay(p["a"]), guard.replay(p["b"])  # facts: off the request path
        t = time.monotonic()
        d = guard.check(cached, new)  # request path: both rewrites + two Jev checks
        latencies.append(time.monotonic() - t)
        b = bench[p["id"]]
        return p, d, b["full-jev"] >= 0.70 and b["rewrite-batch-jev"] >= 0.15

    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(run, pairs))
    agree = sum(d.serve == expected for _, d, expected in results)
    hits = [d.serve for p, d, _ in results if p["same_answer"]]
    wrong = [d.serve for p, d, _ in results if not p["same_answer"]]
    print(f"{len(results)} pairs: guard agrees with the benchmark decision on {agree}/{len(results)}")
    print(f"guard served {sum(hits)}/{len(hits)} should-hit, {sum(wrong)}/{len(wrong)} traps")
    lat = sorted(latencies)
    print(f"request-path latency per check (both rewrites uncached, worst case): median "
          f"{statistics.median(lat)*1000:.0f} ms, p90 {lat[int(len(lat)*0.9)]*1000:.0f} ms, max {lat[-1]*1000:.0f} ms")
    for p, d, expected in results:
        flag = "" if d.serve == expected else "   <- differs from benchmark"
        print(f"  {p['id']:<26} {p['subtype']:<27} label={'hit ' if p['same_answer'] else 'trap'} "
              f"serve={d.serve!s:<5} whole={d.whole_score:.2f} rewrite={d.rewrite_score:.2f}{flag}")


if __name__ == "__main__":
    main()
