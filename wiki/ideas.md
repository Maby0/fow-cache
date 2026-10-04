# Ideas

## Partial reuse / answer adaptation (Mabon, 2026-10-04)

From the label review (rows 16 and 19): when a pair is a near miss ("annual leave after
1 year" vs "after 5 years", "Lifetime ISA at 39" vs "at 41"), don't throw the cached
answer away. Give it plus the new question to a small model, which writes only the
question-specific part ("Lifetime ISAs can be opened from 18 up to 39" + "so no, not at
41").

- **Three outcomes instead of two:** serve as-is, adapt, miss (full main-model call).
- **Gate:** "is the new question answerable from the cached answer?" (not "same answer?").
  Jev can ask it; the adapter must be allowed to answer "insufficient" instead of guessing.
- **Main risk:** the cached answer lacks what's needed (the 1-year leave answer says "25
  days" but leave grows with service), and the adapter fabricates the rest.
- **Rough cost** (cost-model prices): Haiku adapt ~500 in / 30 out = ~$0.0007 vs a
  prompt-cached Sonnet 5.5 turn ~$0.0056, so ~85-90% saved when it works; latency
  sits between a hit and a full call.
- **Benchmark needs:** cached answers for each pair (the data has questions only; GPTCache's
  JevEvaluation needs answers too) and a second label, `answerable_from_cached`. Metrics:
  adaptation success rate, confident-wrong adaptation rate.
- Not offered by GPTCache, RedisVL or vCache as far as we know (unverified).
- Plan: after the label review; candidate for v0.3.
- **Examples from the review** (data/REVIEW_LOG.md): rows 16, 19, 21, 23. Row 21 is the
  easy case (cached answer holds the fact; the adapter rephrases). Row 23 is the hard one:
  "compulsory GCSEs are X, Y, Z" doesn't contain the optional subjects, so the adapter
  would be generating new facts. Partial reuse only pays when the cached answer carries
  most of what's needed; the gate has to send cases like 23 to a full call.

## Decision: Jev stays the checker (Mabon, 2026-10-04)

Considered offering Haiku as an alternative yes/no checker (no third-party key). Rejected:
Jev is far cheaper ($0.042/M input, output free vs Haiku $1/$5) and faster (~270-380 ms vs
~1 s median here), and it's genuinely new in the market. fow-cache is positioned as a
product built on Jev: Haiku generates (facts, rewrites), Jev decides.
