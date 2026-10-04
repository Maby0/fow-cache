# fow-cache results

600 pairs: 300 that should be served from cache (near-verbatim repeats and paraphrases), 300 traps that need a different answer.

## Each scorer at its default threshold

| scorer | should-hit served | near repeats | paraphrases | traps given a wrong answer | negation | entity swap | number/date | scope | one-word-edit traps | reworded traps |
|---|---|---|---|---|---|---|---|---|---|---|
| GPTCache defaults (ONNX albert, threshold 0.8) | 81% | 96% | 74% | 81% | 85% | 68% | 93% | 76% | 93% | 55% |
| RedisVL defaults (langcache-embed-v1, distance 0.1) | 51% | 89% | 32% | 11% | 17% | 4% | 15% | 9% | 17% | 0% |
| all-mpnet-base-v2 (old RedisVL default) at 0.90 | 49% | 85% | 30% | 27% | 29% | 13% | 53% | 11% | 39% | 1% |
| all-MiniLM-L6-v2 at 0.90 | 48% | 84% | 30% | 27% | 40% | 9% | 49% | 11% | 40% | 1% |
| bge-small-en-v1.5 at 0.90 | 63% | 88% | 50% | 34% | 44% | 19% | 48% | 25% | 48% | 5% |
| Jev yes/no check, detailed prompt, 0.5 | 98% | 100% | 97% | 1% | 1% | 0% | 1% | 0% | 1% | 0% |
| Jev yes/no check, one-line prompt, 0.5 | 100% | 100% | 100% | 2% | 3% | 0% | 4% | 0% | 1% | 2% |

## Best should-hit rate with wrong answers capped (any threshold)

| scorer | at <=1% wrong answers (threshold) | at <=5% wrong answers (threshold) |
|---|---|---|
| GPTCache defaults (ONNX albert, threshold 0.8) | 9% (0.993) | 22% (0.98) |
| RedisVL defaults (langcache-embed-v1, distance 0.1) | 31% (0.961) | 41% (0.935) |
| all-mpnet-base-v2 (old RedisVL default) at 0.90 | 14% (0.988) | 25% (0.972) |
| all-MiniLM-L6-v2 at 0.90 | 12% (0.992) | 29% (0.968) |
| bge-small-en-v1.5 at 0.90 | 17% (0.992) | 41% (0.964) |
| Jev yes/no check, detailed prompt, 0.5 | 100% (0.301) | 100% (0.181) |
| Jev yes/no check, one-line prompt, 0.5 | 100% (0.581) | 100% (0.391) |
