"""Does a guarded semantic cache save money?

A cache hit saves one main-model turn. The guard costs Haiku calls (facts, rewrites) and
two Jev checks. break_even() is the share of turns that must be hits for the guard to
cost less than it saves. Token counts were measured on the benchmark's prompts and data
(about 4 characters per token); prices are list prices on 2026-10-03.
"""
from dataclasses import dataclass

PRICES = {  # $ per million tokens: input, output, cache read
    "haiku-4.5": (1.0, 5.0, 0.10),
    "sonnet-5.5": (2.0, 10.0, 0.20),
    "opus-5.5": (4.0, 20.0, 0.20),
}
GUARD_MODEL = "haiku-4.5"
JEV_INPUT = 0.042  # $ per million input tokens, output free

# (input, output) tokens per call, measured with bench/costs.py. "typical" = 3-17 message
# chats, "very_long" = 40-70. "batch" is already divided by the batch size (per turn).
TOKENS = {
    "typical": {"facts": (472, 72), "batch": (140, 18), "lite": (285, 25), "window": (143, 25),
                "full": (181, 25), "jev": (524, 0)},
    "very_long": {"facts": (484, 72), "batch": (152, 18), "lite": (304, 25), "window": (162, 25),
                  "full": (1035, 25), "jev": (2230, 0)},
}
GUARDS = {  # name: (always-on work per turn, rewrite used on candidates)
    "batched facts (default)": ("batch", "lite"),
    "facts every turn": ("facts", "lite"),
    "no facts, full-transcript rewrite": (None, "full"),
}


@dataclass
class Scenario:
    model: str = "sonnet-5.5"
    prompt_tokens: int = 8000  # system prompt + tools + history sent each turn
    new_tokens: int = 500
    output_tokens: int = 300
    prompt_caching: bool = True
    candidate_rate: float = 0.2  # share of turns where the embedding lookup finds a candidate
    size: str = "typical"


def turn_cost(s):
    """$ for one main-model turn, i.e. what a cache hit saves."""
    pin, pout, pread = PRICES[s.model]
    prefix = s.prompt_tokens * (pread if s.prompt_caching else pin)
    return (prefix + s.new_tokens * pin + s.output_tokens * pout) / 1e6


def guard_cost(s, guard="batched facts (default)"):
    """Expected guard $ per turn: always-on work plus, on candidates, both sides'
    rewrites (the cached side's computed lazily, worst case) and two Jev checks."""
    always, rewrite = GUARDS[guard]
    tokens = TOKENS[s.size]
    hin, hout, _ = PRICES[GUARD_MODEL]
    cost = 0.0
    if always:
        i, o = tokens[always]
        cost += (i * hin + o * hout) / 1e6
    i, o = tokens[rewrite]
    per_candidate = 2 * (i * hin + o * hout) / 1e6 + tokens["jev"][0] * JEV_INPUT / 1e6
    return cost + s.candidate_rate * per_candidate


def break_even(s, guard="batched facts (default)"):
    """Hit rate at which the guard pays for itself. Above s.candidate_rate it never can."""
    return guard_cost(s, guard) / turn_cost(s)


def report(s):
    lines = [f"Main model {s.model}, {s.prompt_tokens:,} prompt tokens "
             f"({'prompt-cached' if s.prompt_caching else 'no prompt caching'}), {s.new_tokens} new, "
             f"{s.output_tokens} out: a hit saves ${turn_cost(s):.4f}. "
             f"Candidates on {s.candidate_rate:.0%} of turns, {s.size.replace('_', ' ')} conversations.", ""]
    for g in GUARDS:
        be = break_even(s, g)
        note = "" if be <= s.candidate_rate else "  (never pays: above the candidate rate)"
        lines.append(f"  {g:<36} ${guard_cost(s, g):.5f}/turn   break-even hit rate {be:.0%}{note}")
    return "\n".join(lines)
