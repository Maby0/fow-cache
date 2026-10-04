# Findings

## Run 1 (2026-09-29): 200 pairs, 3 local embedders, Jev

Full tables: `results/README.md`; chart: `results/tradeoff.png`.

- **Embeddings cannot separate the traps at any threshold.** For all three models
  (all-MiniLM-L6-v2, all-mpnet-base-v2, bge-small-en-v1.5) there is no threshold
  that keeps false hits at or under 5% while letting any paraphrase through. The
  worst traps score higher than almost every real paraphrase: "Track order 48213" vs
  "48231" is 0.994 on mpnet, "ibuprofen safe/unsafe with alcohol" 0.991, while the
  median paraphrase is 0.815.
- At a 0.90 threshold mpnet serves 35% of traps and only 18% of paraphrases.
  Negation and number/date traps are the worst (40% and 68% served at 0.90).
- **Jev** (jev-1.13 via OpenRouter, one yes/no question per pair, ~300 ms median,
  $0.003 for all 200): at 0.5, 95% paraphrase hits and 1% false hits (one trap, the
  prescription pair, arguably borderline). A **neutral one-line prompt** with no
  hints still gets 87% hits at 0% false hits (threshold 0.8), so the hinted prompt
  is not what's doing the work. Numbers/dates are a documented Jev weakness, yet it
  let none of those traps through.

## Caveats before publishing (must fix)

1. **Design bias.** Traps are minimal edits; paraphrases are loose rewordings. That
   is the worst case for embeddings. Add near-verbatim repeats that should hit
   (typos, casing, "please", punctuation), where embeddings do well, so the
   benchmark is fair.
2. **One author labelled everything** (Claude, in session). Needs independent
   review of every label, and ideally a second labeller.
3. **Small.** 200 pairs. Target ~1,000 across more domains.
4. **Not yet run:** the real GPTCache / RedisVL / vCache pipelines with their
   defaults, an LLM judge (e.g. Haiku 4.5), OpenAI text-embedding-3-small (vCache's
   default embedder).
5. Cost/latency framing: the judge only runs on candidate hits, but ~300 ms per
   check matters for voice use cases.

## Run 2 (2026-09-29): 600 pairs, real library defaults

Data: run-1 pairs plus 100 near-verbatim repeats and 300 pairs in 12 new domains
(written by three sub-agents, merged, deduplicated). 300 should-hit, 300 traps; 99 of
the traps are reworded as well as changed. Full tables: `results/README.md`.

| scorer at its shipped default | should-hit served | traps given a wrong answer |
|---|---|---|
| GPTCache 0.1.44 defaults (ONNX albert, 0.8), run through the real library | 81% | **81%** |
| RedisVL defaults (redis/langcache-embed-v1, distance 0.1 = similarity 0.9) | 51% | 11% |
| all-mpnet-base-v2 at 0.90 (RedisVL's old default) | 49% | 27% |
| Jev yes/no, one-line prompt, 0.5 | 100% | 2% |

- **The fairness fix worked as intended.** Embeddings serve 84-96% of near-verbatim
  repeats and almost never fall for reworded traps (0-5%). Their failure is specific:
  one-word-edit traps (17-93% served) and loose paraphrases (30-50% served).
- **GPTCache out of the box answers 93% of one-word-edit traps from cache.** My
  reconstructed score matched the library's own `get()` on 600/600 pairs, so this is
  the library's real behaviour, not a re-implementation.
- **RedisVL's caching-tuned model is the best embedding**: 11% wrong answers, but it
  only serves 32% of paraphrases.
- **Jev separates the set almost perfectly** (100% should-hit at <=1% wrong answers at
  some threshold, both prompts). Treat as too good to be true until caveat 6 is
  addressed.

### New findings about the landscape (2026-09-29)

- **GPTCache master already has a `JevEvaluation`** (added 2026-09-20 by
  xiaofanluan, apparently the same person as core contributor xiaofan-luan), not yet
  in a PyPI release (latest 0.1.44 is from 2024). It asks Jev several noul
  questions (task identical, context matches, format ok, freshness) and takes the
  minimum, threshold 0.70. It needs the cached *answer*, which our pairs don't have.
- **GPTCache also merged a reuse-compatibility benchmark** (PR #702, 2026-09-22):
  1,536 naturally occurring cases from vCache's LMArena and search-query datasets,
  model-assisted labels (Codex), Chinese README. Reports Jev at 99.7% precision /
  72.1% recall vs the default cross-encoder reranker at 42% precision.
- So "Jev beats embeddings as a cache checker" is already published inside
  GPTCache. What's still ours: deliberately built one-word traps, customer-service
  and voice-style traffic, testing the plain embedding + threshold setups people
  actually run, and an English README with a sharp chart.

### Caveats (updated)

1. ~~Design bias~~ addressed by near repeats and reworded traps.
2. Labels are all model-written (Claude and sub-agents). `data/REVIEW_SAMPLE.md` has
   40 pairs for human review (done 2026-10-04, see data/REVIEW_LOG.md); a second
   labeller is still needed.
3. 600 pairs; target ~1,000.
4. Not yet run: vCache, GPTCache's `JevEvaluation` (needs answers), an LLM judge
   (Haiku 4.5), OpenAI text-embedding-3-small.
5. Latency: Jev ~290 ms median per check (OpenRouter, London), $0.008-0.010 per 600.
6. **New: the data was written by LLMs and judged by an LLM-family model.** Pairs an
   LLM writes may be unusually easy for an LLM to judge. Real traffic (e.g. public
   support-ticket datasets) is needed before
   claiming Jev's near-perfect numbers.

## Run 3 (2026-10-02): conversations (follow-up traps)

Data: 180 conversation pairs in `data/conv-parts/` (spec: `data/CONVERSATIONS_SPEC.md`),
written by three sub-agents in billing, retail and services domains. 90 traps where the
final user messages match but earlier context changes the answer (context swap, detail
swap, intent flip), 90 should-hit. Lengths 3, 7 and 13-17 messages. Code:
`bench/conversations.py`, `bench/conv_report.py`; full tables `results/CONVERSATIONS.md`.
Haiku 4.5 (via OpenRouter) writes notes / facts / rewrites, cached in `results/derived/`.

| strategy (default threshold) | should-hit served | traps wrong |
|---|---|---|
| Last message only, RedisVL default embedder | 89% | **97%** |
| Last message only, Jev | 98% | 100% |
| Whole conversations, Jev | **100%** | 9% |
| 4-5 word notes per exchange (Mabon's first idea), Jev | 91% | 46% |
| Running facts v1, Jev | 91% | 10% |
| Facts v2 (persistent goal, fixed keys, previous reply verbatim) | 70% | 7% |
| Facts v3 (v2 + Jev told to judge what the final message depends on) | 81% | 7% |
| Standalone rewrite, Jev | 71% | 1% |

- **Last-message caching (GPTCache's default `last_content`) serves a wrong answer to
  nearly every follow-up trap**: the headline result.
- **Whole conversation → Jev wins at these lengths**: 93% hits at <=5% wrong. Jev
  input is ~$0.04/M tokens and latency didn't grow (270 ms median), so the case for
  summarising is accuracy on *much longer* chats, which this data doesn't test yet
  (max 17 messages).
- **4-5 word notes lose the details traps hinge on** (46% wrong).
- **Facts failure modes**: a long chat wanders and the record drops the original
  request (billing-018: Tue vs Thu spin class lost behind sauna questions); options
  summarised away ("the second one"); independently written records differ in wording
  and Jev reads that as a difference; Haiku mis-copied £75 as £375 once. v2 fixed the
  first two but a persistent goal made standalone questions in different chats look
  different (irrelevant_history 47%); v3's instructions recovered some of that.
- **Rewrite → Jev is the safest** (1% wrong) but serves fewest hits.
- Caveats: all labels model-written, one dataset author family; conversations are short.

Next: a long-conversation set (40-100 messages) to test whether whole-conversation Jev
degrades, which is where facts would earn their keep; and a hybrid (facts for older
turns + last N messages verbatim).

## Run 4 (2026-10-03): long conversations (40-70 messages) + hybrid

Added 60 long pairs (`data/conv-long/`, spec `data/CONVERSATIONS_LONG_SPEC.md`): key
detail in the first 6 messages, never repeated, a distractor (the other side's value)
mid-chat in every swap trap, and the last 8 messages identical across each trap pair.
New strategies: `window-jev` (last 7 messages only) and `hybrid-jev` (facts v2 for
older turns + last 7 messages verbatim). Haiku now optionally runs through Claude Code
(`--haiku-via claude-cli`); the long runs are Haiku-heavy (facts/notes take ~22 calls
per long conversation per strategy).

Very long chats only (30 traps, 30 should-hit), default thresholds:

| strategy | hits served | traps wrong |
|---|---|---|
| Last message only (any) | 83% | 100% |
| Last 7 messages only, Jev | 77% | 100% |
| Whole conversation, Jev | 100% | **30%** (3-14% on shorter chats) |
| 4-5 word notes, Jev | 93% | 63% |
| Running facts v1, Jev | 77% | 27% |
| Facts v2, Jev | 70% | 17% |
| Hybrid (facts v2 + last 7), Jev | 80% | 23% |
| Standalone rewrite, Jev | 53% | 3% |

- **Whole-conversation Jev does degrade with length** (30% wrong at 40-70 messages),
  confirming the hypothesis that motivated summarising. Summaries cut that (17-27%)
  but cost hits, and none is safe on its own.
- **Rewrite (Haiku writes a standalone version of the final message, at request
  time) is the safest single strategy.** Difference from running facts: it summarises
  *what this message refers to*, knowing the message, rather than everything that
  might matter later. Cost: a Haiku call on the request path (~1-2.5 s).
- **Combining two checks (serve only if both agree)**, from existing scores:
  whole-conversation Jev (0.5) AND rewrite Jev (0.25) gives 87% hits / 2% wrong overall,
  80% / 3% on very long chats. Hybrid AND rewrite: 81% / 1%. **Caution: thresholds
  picked on the same data, so optimistic; needs a held-out split.**
- Small samples: 30 very-long traps, so each trap is 3.3 points.

## Run 5 (2026-10-03): held-out thresholds + rewrite-lite

- New `rewrite-lite-jev`: Haiku writes the standalone version of the final message from
  the running facts v2 (kept up to date off the request path) plus the last 7 messages,
  instead of the whole transcript, so the request-path call stays small. Alone at 0.5:
  76% hits / 7% wrong (full rewrite: 66% / 2%).
- New `bench/conv_heldout.py`: two-fold, thresholds tuned on one half (split within each
  subtype x length group), scored on the other; table in `results/CONVERSATIONS_HELDOUT.md`.

Held-out, tuned for <=1% wrong on the tuning half:

| strategy | hits | wrong | very long hits | very long wrong |
|---|---|---|---|---|
| Whole conversation | 48% | 2% | 33% | 3% |
| Rewrite from whole transcript | 15% | 1% | 3% | 0% |
| **Whole conversation AND rewrite-lite** | **80%** | **2%** | **70%** | **3%** |
| Whole conversation AND full rewrite | 78% | 4% | 60% | 7% |

- **The winner is two checks that must agree**: whole conversation to Jev, with the
  rewrite-lite check as a veto. It holds up on unseen pairs, and it's cheaper than the
  full rewrite. Mabon's running-facts idea earns its place here as the input to the
  rewrite rather than as the check itself.
- Tuning for <=5% overshoots on the test half (whole-conv AND rewrite-lite: 98% hits but
  8% wrong; 13% on very long), so with this little data tune to a stricter target than
  you want. Thresholds also move between folds (e.g. rewrite veto 0.20 vs 0.05).
- Simplest decent single option: full rewrite at 0.25 gives 87% / 4% held-out.
- Request path for the winner: one small Haiku call + two Jev calls in parallel. Haiku
  latency through the CLI (~5 s here) is CLI overhead and not representative; measure
  via the API before quoting.
- Caveats unchanged: model-written data and labels, 120 traps (30 very long).

## Run 6 (2026-10-03): cheaper guards + cost model

Question from Mabon: does the Haiku summarising cost cancel out the cache savings?
New `bench/costs.py` (break-even hit rate per guard; token counts measured from the
benchmark prompts at ~4 chars/token, OpenRouter list prices 2026-10-03; output
`results/COSTS.md`). New strategies: `rewrite-window-jev` (rewrite from last 7
messages, no facts) and `rewrite-batch-jev` (facts updated once per 4 exchanges, rewrite
from those facts plus every message since the last batch).

Held-out (two-fold), tuned for <=1% wrong:

| strategy | hits | wrong | very long hits | very long wrong |
|---|---|---|---|---|
| Whole conv AND rewrite-lite (facts every turn) | 80% | 2% | 70% | 3% |
| **Whole conv AND rewrite-batch (facts every 4 turns)** | **92%** | **3%** | **90%** | **3%** |
| Whole conv AND rewrite-window (no facts) | 48% | 2% | 33% | 3% |

Cost (Sonnet 5.5 main model, prompt-cached, 8k-token prompt, 20% candidate rate):
facts every turn $0.0010/turn, break-even 18% hit rate; batched $0.0004, 7%; no facts
$0.0001, 2% (but accuracy collapses: the window rewrite misses details from early in
the chat, 100% wrong on very long traps at 0.5).

- **Batching the facts is both cheaper (~2.5x) and more accurate** than updating
  every turn. Likely cause (unverified): 4x fewer rewrites of the record means fewer
  chances to drop or mangle a detail, and the rewrite sees more raw recent messages
  (7-13 instead of 7). Worth a follow-up with batch sizes 2/4/8.
- Facts are needed: without them the rewrite can't recover details from early turns.
- **The always-on facts update is the cost that matters**; request-path calls only
  run on candidates. With a cheap main model (Haiku 4.5) the per-turn facts version
  never pays at a 20% candidate rate (break-even 36%); batched breaks even at 14%.
- New recommended guard: whole-conversation Jev AND rewrite-batch Jev.

## Run 7 (2026-10-03): batch-size sweep, package v0.1

Batch-size sweep, whole conversation AND rewrite from batched facts, held-out, tuned
for <=1% wrong: every exchange (facts v2 per turn) 80% hits / 2% wrong; every 2: 78% / 2%;
**every 4: 92% / 3%**; every 8: 87% / 6%. 4 stays the default. The curve isn't monotonic,
so part of the gap is noise (120 traps); the "fewer record rewrites lose fewer details"
explanation from Run 6 doesn't hold cleanly (8 is worse on wrong answers).

Packaged as `cache_catch` (no core dependencies; extras `embeddings`, `anthropic`,
`bench`): `evaluate()` + `Report`, bundled data, `checks` (embedding, last_message, Jev,
guard), `Guard` (batch 4, thresholds 0.70 whole / 0.15 rewrite from Run 6's held-out
folds), `costs` and the `cache-catch` CLI (`eval --max-wrong` for CI, `costs`). Prompts
live in `cache_catch/prompts.py` and the bench imports them (cache keys verified
unchanged). 12 tests with fake LLM/Jev; wheel verified in a clean environment; CLI
embedder run reproduces the bench (48.3% / 26.7% vs 49% / 27%: threshold-edge pairs
differ with per-text encoding).

## Run 8 (2026-10-04): live guard check; renamed fow-cache

Project renamed cache-catch -> fow-cache ("fly on the wall"). `bench/guard_live.py` runs
the packaged `Guard` end to end on 20 pairs (6 very long), Haiku via Claude Code CLI,
Jev via OpenRouter: agrees with the benchmark's combined decision on **18/20**; served
9/10 should-hit and 1/10 traps. Both disagreements came from the rewrite score
(retail-052 hit missed at rewrite 0.13; long-services-010 intent-flip trap served at
whole 0.75 / rewrite 0.54). CLI Haiku isn't temperature 0, so rewrites vary between
runs; rerun via the API (`--haiku-via anthropic`) before quoting live numbers.

## Run 9 (2026-10-04): direct Anthropic API (temperature 0) + latency

`--haiku-via anthropic` (SDK 1.x: temperature via `extra_body`, Haiku 4.5 still honours
it; separate cache `results/derived/haiku-anthropic.json`; outputs suffixed `-api`).
1,659 Haiku calls, median 1.04 s.

Held-out, tuned for <=1% wrong:

| guard | CLI run | API run (temp 0) |
|---|---|---|
| whole AND rewrite-batch | 92% / 3% (very long 90% / 3%) | **90% / 6%** (very long 87% / 10%) |
| whole AND full-transcript rewrite | 78% / 4% | 85% / 4% |

- The Run 6 "batched beats full-transcript" gap mostly disappears on the API run;
  differences of 3-4 traps out of 120 are noise. Neither guard meets its <=1% tuning
  target on held-out pairs: real wrong-answer rate is ~3-6%. Publish ~90% / ~5% with both
  runs shown, and say the dataset is too small to separate the two guards.
- Very long chats remain the weak spot (10% wrong on the API run).
- Live packaged Guard via the API, 30 pairs: agrees with the benchmark on 29/30; served
  15/15 hits, 1/15 traps. **Request-path latency: median 1,233 ms, p90 1,542 ms, max
  4,282 ms** (both sides' rewrites uncached, i.e. worst case; Jev via OpenRouter from
  London). Against a full generation of ~3-10 s, a guarded hit still saves time, but far
  less than an unguarded ~0.1 s hit.
- Next to make the numbers sharper: more traps (especially very long), which the sweep
  and more data would give.
