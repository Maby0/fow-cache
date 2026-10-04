# Does the guard pay for itself?

A hit saves one main-model turn; the guard costs Haiku + Jev calls. Break-even is the share of turns that must be cache hits for the guard to cost less than it saves. Token counts are estimates (4 characters per token) measured on the benchmark data; prices are 2026-10-03 list prices. Real hit and candidate rates need real traffic.

## typical (3-17 messages), sonnet-5.5, no prompt caching

Main model sonnet-5.5, 8,000 prompt tokens (no prompt caching), 500 new, 300 out: a hit saves $0.0200. Candidate rate 20%.

| guard | guard cost per turn | break-even hit rate |
|---|---|---|
| whole AND rewrite-lite (facts every turn) | $0.00100 | 5% |
| whole AND rewrite-batch (facts every 4 turns) | $0.00040 | 2% |
| whole AND rewrite-window (no facts) | $0.00011 | 1% |
| whole AND rewrite (full transcript, no facts) | $0.00013 | 1% |

## typical (3-17 messages), sonnet-5.5, prompt caching

Main model sonnet-5.5, 8,000 prompt tokens (prompt-cached), 500 new, 300 out: a hit saves $0.0056. Candidate rate 20%.

| guard | guard cost per turn | break-even hit rate |
|---|---|---|
| whole AND rewrite-lite (facts every turn) | $0.00100 | 18% |
| whole AND rewrite-batch (facts every 4 turns) | $0.00040 | 7% |
| whole AND rewrite-window (no facts) | $0.00011 | 2% |
| whole AND rewrite (full transcript, no facts) | $0.00013 | 2% |

## typical (3-17 messages), haiku-4.5, prompt caching

Main model haiku-4.5, 8,000 prompt tokens (prompt-cached), 500 new, 300 out: a hit saves $0.0028. Candidate rate 20%.

| guard | guard cost per turn | break-even hit rate |
|---|---|---|
| whole AND rewrite-lite (facts every turn) | $0.00100 | 36% (above the candidate rate: never pays) |
| whole AND rewrite-batch (facts every 4 turns) | $0.00040 | 14% |
| whole AND rewrite-window (no facts) | $0.00011 | 4% |
| whole AND rewrite (full transcript, no facts) | $0.00013 | 5% |

## very long (40-70 messages), sonnet-5.5, no prompt caching

Main model sonnet-5.5, 8,000 prompt tokens (no prompt caching), 500 new, 300 out: a hit saves $0.0200. Candidate rate 20%.

| guard | guard cost per turn | break-even hit rate |
|---|---|---|
| whole AND rewrite-lite (facts every turn) | $0.00104 | 5% |
| whole AND rewrite-batch (facts every 4 turns) | $0.00043 | 2% |
| whole AND rewrite-window (no facts) | $0.00013 | 1% |
| whole AND rewrite (full transcript, no facts) | $0.00048 | 2% |

## very long (40-70 messages), sonnet-5.5, prompt caching

Main model sonnet-5.5, 8,000 prompt tokens (prompt-cached), 500 new, 300 out: a hit saves $0.0056. Candidate rate 20%.

| guard | guard cost per turn | break-even hit rate |
|---|---|---|
| whole AND rewrite-lite (facts every turn) | $0.00104 | 18% |
| whole AND rewrite-batch (facts every 4 turns) | $0.00043 | 8% |
| whole AND rewrite-window (no facts) | $0.00013 | 2% |
| whole AND rewrite (full transcript, no facts) | $0.00048 | 9% |

## very long (40-70 messages), haiku-4.5, prompt caching

Main model haiku-4.5, 8,000 prompt tokens (prompt-cached), 500 new, 300 out: a hit saves $0.0028. Candidate rate 20%.

| guard | guard cost per turn | break-even hit rate |
|---|---|---|
| whole AND rewrite-lite (facts every turn) | $0.00104 | 37% (above the candidate rate: never pays) |
| whole AND rewrite-batch (facts every 4 turns) | $0.00043 | 15% |
| whole AND rewrite-window (no facts) | $0.00013 | 5% |
| whole AND rewrite (full transcript, no facts) | $0.00048 | 17% |
