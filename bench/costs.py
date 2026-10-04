"""Does a guarded semantic cache save money? Compares the guard's cost per turn with what
a cache hit saves (one main-model turn), and prints the break-even hit rate.

Guard token counts are measured from the benchmark's own prompts and data (roughly 4
characters per token), at the benchmark's typical and very long conversation sizes.
Prices: OpenRouter list prices on 2026-10-03; Jev from TypeSafe's docs.

  python bench/costs.py                                  # standard scenarios -> results/COSTS.md
  python bench/costs.py --model sonnet-5.5 --prompt-tokens 8000 --candidate-rate 0.2
"""
import argparse
import json
import statistics as st
from pathlib import Path

import conversations as c

ROOT = Path(__file__).resolve().parent.parent
PRICES = {  # $ per million tokens: input, output, cache read
    "haiku-4.5": (1.0, 5.0, 0.10),
    "sonnet-5.5": (2.0, 10.0, 0.20),
    "opus-5.5": (4.0, 20.0, 0.20),
}
JEV_IN = 0.042  # $/M input, output free
GUARDS = {
    # name: (always-on Haiku calls per turn, request-path rewrite kind)
    "whole AND rewrite-lite (facts every turn)": ("facts", "lite"),
    "whole AND rewrite-batch (facts every 4 turns)": ("batch", "lite"),
    "whole AND rewrite-window (no facts)": (None, "window"),
    "whole AND rewrite (full transcript, no facts)": (None, "full"),
}


def tok(s):
    return len(s) / 4


def measure(convs):
    """Average input/output tokens for each guard component on these conversations."""
    record = 120  # typical facts record size in tokens
    ex = [tok(u) + tok(a) for x in convs for u, a in c.exchanges(x)]
    out = json.loads((c.DERIVED / "haiku.json").read_text()).values()
    facts_out = st.median(tok(v) for v in out if v.lstrip().startswith("{")) if out else 60
    full = st.mean(tok(c.transcript(x)) for x in convs)
    recent = st.mean(tok(c.transcript(x[-c.RECENT:])) for x in convs)
    return {
        "facts": (tok(c.FACTS_PROMPT_V2) + record + st.mean(ex), facts_out),
        "batch": ((tok(c.FACTS_BATCH_PROMPT) + record + c.BATCH * st.mean(ex)) / c.BATCH, facts_out / c.BATCH),
        "lite": (tok(c.REWRITE_LITE_PROMPT) + record + recent, 25),
        "window": (tok(c.REWRITE_PROMPT) + recent, 25),
        "full": (tok(c.REWRITE_PROMPT) + full, 25),
        "jev": (tok(c.CONV_INSTRUCTIONS) + 2 * full + tok(c.INSTRUCTIONS) + 60, 0),
    }


def guard_cost(m, always, rewrite, candidate_rate):
    """Expected $ per turn. Always-on facts run every turn; on a candidate, both sides'
    rewrites (the cached side computed lazily) plus the two Jev checks."""
    hin, hout, _ = PRICES["haiku-4.5"]
    cost = 0.0
    if always:
        i, o = m[always]
        cost += (i * hin + o * hout) / 1e6
    i, o = m[rewrite]
    per_candidate = 2 * (i * hin + o * hout) / 1e6 + m["jev"][0] * JEV_IN / 1e6
    return cost + candidate_rate * per_candidate


def turn_cost(model, prompt_tokens, new_tokens, output_tokens, prompt_caching):
    pin, pout, pread = PRICES[model]
    prefix = prompt_tokens * (pread if prompt_caching else pin)
    return (prefix + new_tokens * pin + output_tokens * pout) / 1e6


def table(m, model, prompt_tokens, new_tokens, output_tokens, prompt_caching, candidate_rate):
    saving = turn_cost(model, prompt_tokens, new_tokens, output_tokens, prompt_caching)
    rows = [f"Main model {model}, {prompt_tokens:,} prompt tokens "
            f"({'prompt-cached' if prompt_caching else 'no prompt caching'}), {new_tokens} new, {output_tokens} out: "
            f"a hit saves ${saving:.4f}. Candidate rate {candidate_rate:.0%}.", "",
            "| guard | guard cost per turn | break-even hit rate |", "|---|---|---|"]
    for name, (always, rewrite) in GUARDS.items():
        g = guard_cost(m, always, rewrite, candidate_rate)
        be = g / saving
        verdict = f"{be:.0%}" if be <= candidate_rate else f"{be:.0%} (above the candidate rate: never pays)"
        rows.append(f"| {name} | ${g:.5f} | {verdict} |")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=PRICES)
    ap.add_argument("--prompt-tokens", type=int, default=8000, help="system prompt + tools + history")
    ap.add_argument("--new-tokens", type=int, default=500)
    ap.add_argument("--output-tokens", type=int, default=300)
    ap.add_argument("--no-prompt-caching", action="store_true")
    ap.add_argument("--candidate-rate", type=float, default=0.2, help="share of turns where the embedding lookup finds a candidate")
    ap.add_argument("--long", action="store_true", help="use very long (40-70 message) conversation sizes")
    args = ap.parse_args()
    pairs = c.load_pairs()
    convs = [p[s] for p in pairs for s in "ab"]
    sizes = {"typical (3-17 messages)": [x for x in convs if len(x) <= 20],
             "very long (40-70 messages)": [x for x in convs if len(x) > 20]}
    if args.model:
        m = measure(sizes["very long (40-70 messages)" if args.long else "typical (3-17 messages)"])
        print("\n".join(table(m, args.model, args.prompt_tokens, args.new_tokens, args.output_tokens,
                              not args.no_prompt_caching, args.candidate_rate)))
        return
    lines = ["# Does the guard pay for itself?", "",
             "A hit saves one main-model turn; the guard costs Haiku + Jev calls. Break-even is the share of "
             "turns that must be cache hits for the guard to cost less than it saves. Token counts are "
             "estimates (4 characters per token) measured on the benchmark data; prices are 2026-10-03 list "
             "prices. Real hit and candidate rates need real traffic.", ""]
    for size, sel in sizes.items():
        m = measure(sel)
        for model, caching in [("sonnet-5.5", False), ("sonnet-5.5", True), ("haiku-4.5", True)]:
            lines += [f"## {size}, {model}, {'prompt caching' if caching else 'no prompt caching'}", ""]
            lines += table(m, model, 8000, 500, 300, caching, 0.2) + [""]
    out = "\n".join(lines)
    (ROOT / "results" / "COSTS.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
