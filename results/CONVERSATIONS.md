# fow-cache: conversations

240 pairs of conversations: 120 should be served from cache, 120 are traps where the final messages match but earlier context changes the answer.

## Each strategy at its default threshold

| strategy | should-hit served | same context reworded | irrelevant history | same context extra chatter | traps given a wrong answer | context swap | detail swap | intent flip |
|---|---|---|---|---|---|---|---|---|
| Last message only, RedisVL default embedder (0.90) | 88% | 64% | 100% | 97% | 98% | 100% | 100% | 92% |
| Last message only, all-mpnet-base-v2 (0.90) | 86% | 56% | 100% | 100% | 100% | 100% | 100% | 100% |
| Last message only, Jev | 98% | 92% | 100% | 100% | 100% | 100% | 100% | 100% |
| Whole conversations, Jev | 100% | 100% | 100% | 100% | 15% | 5% | 31% | 8% |
| Last 7 messages only, Jev | 89% | 82% | 86% | 100% | 37% | 31% | 60% | 17% |
| 4-5 word notes per exchange + last message, Jev | 92% | 95% | 98% | 85% | 50% | 21% | 64% | 67% |
| Running facts + last message, Jev | 88% | 82% | 90% | 90% | 14% | 12% | 14% | 17% |
| Running facts v2 (goal, fixed keys) + previous reply + last message, Jev | 71% | 77% | 48% | 90% | 11% | 7% | 17% | 8% |
| Running facts v2 + previous reply + last message, Jev asked what the final message depends on | 78% | 85% | 62% | 90% | 9% | 7% | 12% | 8% |
| Hybrid: facts v2 for older turns + last 7 messages verbatim, Jev | 92% | 92% | 86% | 100% | 10% | 5% | 14% | 11% |
| Standalone rewrite, RedisVL default embedder (0.90) | 48% | 33% | 45% | 64% | 10% | 0% | 19% | 11% |
| Standalone rewrite, all-mpnet-base-v2 (0.90) | 45% | 31% | 45% | 59% | 26% | 0% | 64% | 11% |
| Standalone rewrite, Jev | 66% | 72% | 55% | 72% | 2% | 0% | 2% | 3% |
| Standalone rewrite from facts + last 7 messages, Jev | 76% | 74% | 76% | 77% | 7% | 2% | 12% | 6% |
| Standalone rewrite from last 7 messages only, Jev | 75% | 64% | 79% | 82% | 33% | 31% | 48% | 19% |
| Standalone rewrite from batched facts (every 4 exchanges) + recent messages, Jev | 75% | 74% | 67% | 85% | 2% | 0% | 5% | 0% |
| Standalone rewrite, facts every 2 exchanges, Jev | 78% | 69% | 79% | 85% | 3% | 2% | 5% | 3% |
| Standalone rewrite, facts every 8 exchanges, Jev | 80% | 74% | 79% | 87% | 2% | 0% | 7% | 0% |

## Wrong answers and hits by conversation length

| strategy | traps wrong, short | traps wrong, medium | traps wrong, long | traps wrong, very_long | hits served, short | hits served, medium | hits served, long | hits served, very_long | median latency |
|---|---|---|---|---|---|---|---|---|---|
| Last message only, RedisVL default embedder (0.90) | 90% | 100% | 100% | 100% | 83% | 87% | 97% | 83% | local |
| Last message only, all-mpnet-base-v2 (0.90) | 100% | 100% | 100% | 100% | 79% | 83% | 97% | 83% | local |
| Last message only, Jev | 100% | 100% | 100% | 100% | 97% | 100% | 97% | 97% | 384 ms |
| Whole conversations, Jev | 3% | 13% | 14% | 30% | 100% | 100% | 100% | 100% | 381 ms |
| Last 7 messages only, Jev | 3% | 13% | 31% | 100% | 100% | 100% | 81% | 77% | 378 ms |
| 4-5 word notes per exchange + last message, Jev | 35% | 50% | 52% | 63% | 97% | 90% | 90% | 93% | 378 ms |
| Running facts + last message, Jev | 3% | 13% | 14% | 27% | 97% | 93% | 84% | 77% | 376 ms |
| Running facts v2 (goal, fixed keys) + previous reply + last message, Jev | 6% | 7% | 14% | 17% | 83% | 70% | 61% | 70% | 372 ms |
| Running facts v2 + previous reply + last message, Jev asked what the final message depends on | 0% | 3% | 14% | 20% | 90% | 77% | 81% | 67% | 374 ms |
| Hybrid: facts v2 for older turns + last 7 messages verbatim, Jev | 3% | 3% | 10% | 23% | 100% | 100% | 90% | 80% | 377 ms |
| Standalone rewrite, RedisVL default embedder (0.90) | 10% | 20% | 7% | 3% | 55% | 57% | 48% | 30% | local |
| Standalone rewrite, all-mpnet-base-v2 (0.90) | 32% | 30% | 21% | 20% | 48% | 63% | 45% | 23% | local |
| Standalone rewrite, Jev | 0% | 3% | 0% | 3% | 59% | 87% | 65% | 53% | 377 ms |
| Standalone rewrite from facts + last 7 messages, Jev | 0% | 3% | 10% | 13% | 86% | 80% | 65% | 73% | 371 ms |
| Standalone rewrite from last 7 messages only, Jev | 0% | 3% | 31% | 100% | 62% | 87% | 68% | 83% | 381 ms |
| Standalone rewrite from batched facts (every 4 exchanges) + recent messages, Jev | 0% | 3% | 0% | 3% | 86% | 80% | 65% | 70% | 378 ms |
| Standalone rewrite, facts every 2 exchanges, Jev | 0% | 3% | 0% | 10% | 86% | 90% | 55% | 80% | 364 ms |
| Standalone rewrite, facts every 8 exchanges, Jev | 0% | 3% | 0% | 7% | 86% | 83% | 71% | 80% | 373 ms |

## Best should-hit rate with wrong answers capped (any threshold)

| strategy | at <=1% wrong (threshold) | at <=5% wrong (threshold) |
|---|---|---|
| Last message only, RedisVL default embedder (0.90) | 0% (None) | 0% (None) |
| Last message only, all-mpnet-base-v2 (0.90) | 0% (None) | 0% (None) |
| Last message only, Jev | 22% (0.961) | 32% (0.951) |
| Whole conversations, Jev | 41% (0.821) | 89% (0.691) |
| Last 7 messages only, Jev | 8% (0.851) | 19% (0.811) |
| 4-5 word notes per exchange + last message, Jev | 0% (None) | 0% (None) |
| Running facts + last message, Jev | 18% (0.831) | 51% (0.701) |
| Running facts v2 (goal, fixed keys) + previous reply + last message, Jev | 19% (0.821) | 42% (0.681) |
| Running facts v2 + previous reply + last message, Jev asked what the final message depends on | 17% (0.831) | 48% (0.641) |
| Hybrid: facts v2 for older turns + last 7 messages verbatim, Jev | 22% (0.851) | 72% (0.671) |
| Standalone rewrite, RedisVL default embedder (0.90) | 28% (0.965) | 41% (0.924) |
| Standalone rewrite, all-mpnet-base-v2 (0.90) | 14% (0.998) | 16% (0.993) |
| Standalone rewrite, Jev | 43% (0.821) | 87% (0.241) |
| Standalone rewrite from facts + last 7 messages, Jev | 17% (0.961) | 60% (0.671) |
| Standalone rewrite from last 7 messages only, Jev | 3% (0.971) | 13% (0.961) |
| Standalone rewrite from batched facts (every 4 exchanges) + recent messages, Jev | 31% (0.901) | 95% (0.201) |
| Standalone rewrite, facts every 2 exchanges, Jev | 35% (0.841) | 92% (0.241) |
| Standalone rewrite, facts every 8 exchanges, Jev | 67% (0.621) | 90% (0.291) |
