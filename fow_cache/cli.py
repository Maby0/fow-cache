"""fow-cache command line.

  fow-cache eval --embedder sentence-transformers/all-mpnet-base-v2 --threshold 0.9
  fow-cache eval --dataset conversations --embedder redis/langcache-embed-v1 --max-wrong 0.05
  fow-cache eval --check mypkg.cache:would_hit --json
  fow-cache costs --model haiku-4.5 --candidate-rate 0.1
"""
import argparse
import importlib
import json
import sys

from . import costs
from .evaluate import evaluate


def _load_callable(spec):
    module, _, name = spec.partition(":")
    return getattr(importlib.import_module(module), name)


def cmd_eval(args):
    if args.check:
        check = _load_callable(args.check)
    elif args.embedder:
        from .checks import embedding_check
        check = embedding_check(args.embedder)
    elif args.jev:
        from .checks import jev_check
        check = jev_check()
    else:
        sys.exit("choose one of --check, --embedder or --jev")
    if args.dataset == "conversations" and not args.check:
        from .checks import last_message
        check = last_message(check)  # built-in checks compare final messages, like GPTCache's default
    rep = evaluate(check, args.dataset, args.threshold, args.workers, args.ambiguous)
    print(json.dumps(rep.to_dict(), indent=2) if args.json else rep)
    if args.max_wrong is not None and not rep.passes(args.max_wrong):
        print(f"\nFAIL: {rep.wrong_rate:.1%} of traps got a wrong answer (max {args.max_wrong:.1%})", file=sys.stderr)
        sys.exit(1)


def cmd_costs(args):
    s = costs.Scenario(args.model, args.prompt_tokens, args.new_tokens, args.output_tokens,
                       not args.no_prompt_caching, args.candidate_rate, "very_long" if args.long else "typical")
    print(costs.report(s))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="fow-cache", description="How often does your semantic cache serve the wrong answer?")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("eval", help="score a cache-hit decision on the benchmark")
    e.add_argument("--dataset", choices=["questions", "conversations"], default="questions")
    e.add_argument("--check", help="module:function taking (cached, new) and returning bool or a score")
    e.add_argument("--embedder", help="sentence-transformers model name (needs fow-cache[embeddings])")
    e.add_argument("--jev", action="store_true", help="Jev yes/no check (needs TYPESAFE_API_KEY or OPENROUTER_API_KEY)")
    e.add_argument("--threshold", type=float, default=0.5, help="serve when score >= threshold (default 0.5)")
    e.add_argument("--max-wrong", type=float, help="exit 1 if more than this share of traps get a wrong answer (for CI)")
    e.add_argument("--ambiguous", choices=["different", "same", "skip"], default="different",
                   help="score pairs whose answer depends on the application as traps (default), hits, or skip them")
    e.add_argument("--workers", type=int, default=1)
    e.add_argument("--json", action="store_true")
    e.set_defaults(fn=cmd_eval)
    c = sub.add_parser("costs", help="break-even hit rate for the guard")
    c.add_argument("--model", choices=list(costs.PRICES), default="sonnet-5.5")
    c.add_argument("--prompt-tokens", type=int, default=8000)
    c.add_argument("--new-tokens", type=int, default=500)
    c.add_argument("--output-tokens", type=int, default=300)
    c.add_argument("--no-prompt-caching", action="store_true")
    c.add_argument("--candidate-rate", type=float, default=0.2)
    c.add_argument("--long", action="store_true", help="use very long (40-70 message) conversation sizes")
    c.set_defaults(fn=cmd_costs)
    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
