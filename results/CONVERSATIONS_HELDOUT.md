# fow-cache: conversations, held-out

240 pairs (120 traps). Two-fold: thresholds tuned on one half to keep wrong answers under the target, then scored on the other half; every pair is scored once.

## Tuned for <= 1% wrong answers

| strategy | hits served | traps wrong | very long: hits | very long: wrong | thresholds (fold 1 / fold 2) |
|---|---|---|---|---|---|
| Whole conversation | 48% | 2% | 33% | 3% | 0.90 / 0.75 |
| Hybrid (facts + last 7) | 21% | 2% | 7% | 7% | 0.80 / 0.95 |
| Running facts v1 | 7% | 1% | 7% | 0% | 0.85 / 0.90 |
| Rewrite from whole transcript | 15% | 1% | 3% | 0% | 0.85 / 1.01 |
| Rewrite from facts + last 7 | 0% | 0% | 0% | 0% | 1.01 / 1.01 |
| Rewrite from last 7 only | 0% | 0% | 0% | 0% | 1.01 / 1.01 |
| Rewrite from batched facts + recent | 11% | 1% | 7% | 3% | 1.01 / 0.95 |
| Rewrite, facts every 2 exchanges | 18% | 1% | 20% | 0% | 0.85 / 1.01 |
| Rewrite, facts every 8 exchanges | 43% | 1% | 37% | 0% | 0.65 / 0.90 |
| Rewrite from whole transcript [API, temp 0] | 39% | 1% | 37% | 3% | 1.01 / 0.40 |
| Rewrite from batched facts + recent [API, temp 0] | 52% | 2% | 37% | 3% | 0.95 / 0.65 |
| Whole conversation AND Rewrite from whole transcript | 78% | 4% | 60% | 7% | 0.25,0.45 / 0.70,0.05 |
| Whole conversation AND Rewrite from facts + last 7 | 80% | 2% | 70% | 3% | 0.75,0.20 / 0.70,0.05 |
| Hybrid (facts + last 7) AND Rewrite from facts + last 7 | 26% | 2% | 17% | 7% | 0.50,0.65 / 0.95,0.05 |
| Whole conversation AND Rewrite from last 7 only | 48% | 2% | 33% | 3% | 0.90,0.05 / 0.75,0.05 |
| Whole conversation AND Rewrite from batched facts + recent | 92% | 3% | 90% | 3% | 0.65,0.15 / 0.70,0.05 |
| Whole conversation AND Rewrite, facts every 2 exchanges | 78% | 2% | 70% | 3% | 0.75,0.20 / 0.70,0.05 |
| Whole conversation AND Rewrite, facts every 8 exchanges | 87% | 6% | 83% | 7% | 0.25,0.35 / 0.70,0.05 |
| Whole conversation AND Rewrite from whole transcript [API, temp 0] | 85% | 4% | 70% | 3% | 0.55,0.30 / 0.70,0.05 |
| Whole conversation AND Rewrite from batched facts + recent [API, temp 0] | 90% | 6% | 87% | 10% | 0.35,0.40 / 0.70,0.05 |

## Tuned for <= 5% wrong answers

| strategy | hits served | traps wrong | very long: hits | very long: wrong | thresholds (fold 1 / fold 2) |
|---|---|---|---|---|---|
| Whole conversation | 85% | 8% | 80% | 17% | 0.75 / 0.55 |
| Hybrid (facts + last 7) | 48% | 2% | 27% | 7% | 0.70 / 0.85 |
| Running facts v1 | 32% | 3% | 23% | 7% | 0.70 / 0.85 |
| Rewrite from whole transcript | 87% | 4% | 80% | 7% | 0.25 / 0.25 |
| Rewrite from facts + last 7 | 29% | 3% | 27% | 7% | 0.65 / 1.01 |
| Rewrite from last 7 only | 0% | 0% | 0% | 0% | 1.01 / 1.01 |
| Rewrite from batched facts + recent | 94% | 6% | 93% | 3% | 0.25 / 0.20 |
| Rewrite, facts every 2 exchanges | 84% | 4% | 87% | 13% | 0.25 / 0.50 |
| Rewrite, facts every 8 exchanges | 91% | 5% | 93% | 10% | 0.25 / 0.45 |
| Rewrite from whole transcript [API, temp 0] | 84% | 8% | 73% | 7% | 0.30 / 0.15 |
| Rewrite from batched facts + recent [API, temp 0] | 94% | 8% | 90% | 10% | 0.30 / 0.20 |
| Whole conversation AND Rewrite from whole transcript | 95% | 8% | 97% | 13% | 0.65,0.10 / 0.55,0.05 |
| Whole conversation AND Rewrite from facts + last 7 | 98% | 8% | 100% | 13% | 0.55,0.20 / 0.55,0.05 |
| Hybrid (facts + last 7) AND Rewrite from facts + last 7 | 61% | 4% | 57% | 7% | 0.25,0.25 / 0.85,0.05 |
| Whole conversation AND Rewrite from last 7 only | 91% | 9% | 87% | 20% | 0.70,0.20 / 0.55,0.05 |
| Whole conversation AND Rewrite from batched facts + recent | 97% | 8% | 100% | 3% | 0.65,0.15 / 0.40,0.10 |
| Whole conversation AND Rewrite, facts every 2 exchanges | 95% | 7% | 100% | 10% | 0.65,0.10 / 0.55,0.05 |
| Whole conversation AND Rewrite, facts every 8 exchanges | 95% | 8% | 100% | 10% | 0.65,0.15 / 0.55,0.05 |
| Whole conversation AND Rewrite from whole transcript [API, temp 0] | 97% | 8% | 93% | 10% | 0.55,0.10 / 0.55,0.05 |
| Whole conversation AND Rewrite from batched facts + recent [API, temp 0] | 98% | 9% | 97% | 17% | 0.35,0.30 / 0.55,0.05 |
