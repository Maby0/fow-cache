"""Ask Jev (TypeSafe) one yes/no question per pair: would the cached answer be a
correct answer to the new question? Score is the probability of yes.

Needs OPENROUTER_API_KEY (or TYPESAFE_API_KEY) in the environment, or an env file
passed as --env-file."""
import argparse
import csv
import json
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from fow_cache.prompts import QUESTION_INSTRUCTIONS as INSTRUCTIONS  # noqa: E402


NEUTRAL_INSTRUCTIONS = (
    "Would the answer to cached_question also be a correct answer to new_question?"
)


def provider():
    if os.environ.get("TYPESAFE_API_KEY"):
        return ("https://api.typesafe.ai/v1/systemone", os.environ["TYPESAFE_API_KEY"], "jev-latest")
    return ("https://openrouter.ai/api/alpha/decisions", os.environ["OPENROUTER_API_KEY"], "~typesafe/jev-latest")


def ask(pair, endpoint, key, model, instructions=INSTRUCTIONS):
    body = {
        "model": model,
        "state": {"cached_question": pair["a"], "new_question": pair["b"]},
        "questions": {"same_answer": {"type": "noul", "instructions": instructions}},
    }
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    for attempt in range(4):
        try:
            t = time.monotonic()
            with urllib.request.urlopen(req, timeout=30) as r:
                resp = json.load(r)
            latency = time.monotonic() - t
            ans = resp["answers"]["same_answer"]
            return ans["noul"], latency, resp.get("model", model), resp.get("usage", {}).get("cost")
        except Exception as e:  # retry transient failures, then give up on this pair
            err = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"{pair['id']}: {err}")


def load_env_file(path):
    for line in Path(path).expanduser().read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env-file")
    ap.add_argument("--neutral", action="store_true", help="bare prompt with no hints about what makes answers differ")
    args = ap.parse_args()
    if args.env_file:
        load_env_file(args.env_file)
    endpoint, key, model = provider()
    with open(ROOT / "data" / "pairs.jsonl") as f:
        pairs = [json.loads(line) for line in f]
    with ThreadPoolExecutor(max_workers=8) as ex:
        prompt = NEUTRAL_INSTRUCTIONS if args.neutral else INSTRUCTIONS
        results = list(ex.map(lambda p: ask(p, endpoint, key, model, prompt), pairs))
    out = ROOT / "results" / "scores" / ("jev-neutral.csv" if args.neutral else "jev.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "category", "same_answer", "score", "latency_s"])
        for p, (score, latency, _, _) in zip(pairs, results):
            w.writerow([p["id"], p["category"], p["same_answer"], f"{score:.4f}", f"{latency:.3f}"])
    costs = [c for *_, c in results if c is not None]
    lat = sorted(r[1] for r in results)
    print(f"wrote {out}; model {results[0][2]}; median latency {lat[len(lat)//2]*1000:.0f} ms"
          + (f"; total cost ${sum(costs):.4f}" if costs else ""))


if __name__ == "__main__":
    main()
