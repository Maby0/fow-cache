# Log

## [2026-09-29] build | Repo created, first benchmark run
- Scaffolded repo (uv, Python 3.12), 200 pairs, embedding + Jev scorers, report.
- Run 1 results and caveats in findings.md; prior art in prior-art.md.

## [2026-09-29] build | Round 2: 600 pairs, real defaults
- Added near repeats + 300 new-domain pairs (sub-agents), RedisVL default model, GPTCache real-library run, style breakdown in report.
- Found GPTCache's new JevEvaluation and reuse benchmark; findings.md updated. Label review sample in data/REVIEW_SAMPLE.md.

## [2026-10-02] build | Conversation benchmark (follow-up traps)
- 180 conversation pairs + spec; bench/conversations.py (9 strategies incl. Haiku-written notes/facts/rewrites) and bench/conv_report.py
- Results and failure analysis in findings.md (Run 3): last-message caching ~100% wrong on follow-ups; whole-conversation Jev best at <=17 messages

## [2026-10-03] build | Long conversations, hybrid, Claude Code backend
- 60 long pairs (40-70 messages); window-jev and hybrid-jev strategies; --haiku-via claude-cli (Haiku on the claude.ai plan); periodic atomic saves of the Haiku cache
- Findings Run 4: whole-conversation Jev degrades to 30% wrong on very long chats; rewrite safest; whole-conv AND rewrite looks best (needs held-out check)

## [2026-10-03] build | Held-out thresholds, rewrite-lite
- rewrite-lite-jev strategy (rewrite from facts v2 + last 7 messages); bench/conv_heldout.py (two-fold threshold tuning)
- Findings Run 5: whole-conversation Jev AND rewrite-lite = 80% hits / 2% wrong held-out (70% / 3% on 40-70 message chats)

## [2026-10-03] build | Cost model, batched facts
- bench/costs.py break-even calculator (results/COSTS.md); rewrite-window and rewrite-batch strategies
- Findings Run 6: batched facts (every 4 exchanges) beat per-turn facts on accuracy (92%/3% held-out) at ~2.5x lower cost; new recommended guard

## [2026-10-03] build | Batch sweep + package v0.1
- Batch sizes 2/4/8: 4 best (92% / 3% held-out); findings Run 7
- cache_catch package, CLI, Guard, cost model, tests, CI workflow, MIT + CC BY 4.0 licences, README rewrite

## [2026-10-04] build | Renamed fow-cache, live guard check
- Package/CLI/repo renamed; bench/guard_live.py: packaged Guard agrees with benchmark on 18/20 (findings Run 8)

## [2026-10-04] review | Human label review of 60 sampled pairs
- Mabon reviewed 40 question + 20 conversation pairs: 0 wrong, 10 ambiguous; `ambiguous` tag + evaluate(ambiguous=...) setting added; partial-reuse idea in ideas.md

## [2026-10-04] build | API run + latency
- Anthropic API backend (temp 0): guard 90% / 6% held-out (CLI 92% / 3%: noise at 120 traps); latency median 1.2 s; findings Run 9

## [2026-10-04] build | Production hardening + integrations
- Guard: time budget (default 3 s) and errors fail safe as misses, early exit when the whole-conversation check fails, no nested pool waits, saveable Conversation/Entry state, async (aadd/acheck), logging
- GuardedCache + InMemoryBackend + RedisVLBackend; adapters to evaluate a real cache (store_lookup_check, redisvl_check); CI job against a real Redis (redis-stack) service

## [2026-10-04] build | GPTCache and LangChain backends; Jev positioning
- GPTCacheBackend, LangChainBackend, gptcache_check, langchain_check; tests against the real libraries; CI backends job
- Decision: Jev stays the checker, README gains a Why Jev section (ideas.md)
