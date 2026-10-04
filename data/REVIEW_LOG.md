# Human label review

Labels were written by language models. This file records the human review of a
sample: who decided what, and the rules that came out of it.

## Rules

- **Ambiguous pairs**: whether they share an answer depends on the application, so it's
  a setting, not a label: `evaluate(..., ambiguous="different" | "same" | "skip")`,
  default "different" (strict). Tagged `"ambiguous": "<reason>"`. Decided by Mabon ap
  Gwyn, 2026-10-04. Reasons:
  - `complementary`: two sides of the same question ("which deductions are lawful?" vs
    "which are illegal?", "make my repo public" vs "make it private").
  - `context_dependent`: same answer only if the business works a certain way ("my
    child's school report" vs "their end-of-year report": same if the school issues one
    report a year).
- **Partial reuse** (cached answer + a small question-specific addition) doesn't change
  labels: for a plain cache those pairs are still different. See wiki/ideas.md.

## Decisions (data/REVIEW_SAMPLE.md, reviewer: Mabon ap Gwyn)

| # | id | verdict |
|---|---|---|
| 1 | entity_swap-b024 | label correct |
| 2 | negation-a023 | complementary |
| 3 | scope-a022 | label correct |
| 4 | number_date-b018 | label correct |
| 5 | number_date-b019 | label correct |
| 6 | scope-a014 | label correct |
| 7 | negation-a025 | complementary |
| 8 | entity_swap-b019 | label correct |
| 9 | negation-b016 | complementary |
| 10 | negation-b019 | complementary |
| 11 | negation-a016 | complementary |
| 12 | negation-a018 | complementary |
| 13 | entity_swap-a015 | label correct |
| 14 | negation-b022 | complementary |
| 15 | number_date-b025 | label correct |
| 16 | number_date-008 | label correct (prompted the partial-reuse idea, wiki/ideas.md) |
| 17 | scope-015 | label correct |
| 18 | negation-022 | label correct |
| 19 | number_date-a002 | label correct (partial-reuse idea) |
| 20 | scope-010 | label correct |
| 21 | negation-b004 | label correct (partial-reuse candidate: cached fact + "so no, it's not non-transferable") |
| 22 | number_date-a013 | label correct |
| 23 | negation-a008 | label correct (partial-reuse candidate, but the cached compulsory list doesn't contain the optional subjects: the "insufficient" case) |
| 24 | number_date-b009 | label correct |
| 25 | number_date-002 | label correct |
| 26 | paraphrase-a015 | label correct |
| 27 | paraphrase-044 | label correct |
| 28 | paraphrase-057 | label correct |
| 29 | paraphrase-a012 | label correct |
| 30 | paraphrase-a005 | label correct |
| 31 | paraphrase-b023 | label correct |
| 32 | paraphrase-b026 | label correct |
| 33 | paraphrase-a045 | ambiguous: context_dependent (same only if the school issues one report a year) |
| 34 | paraphrase-a035 | label correct (one answer can cover both: "potholes to X, sinkholes to Y") |
| 35 | paraphrase-051 | label correct |
| 36 | near_repeat-070 | label correct |
| 37 | near_repeat-087 | label correct |
| 38 | near_repeat-055 | label correct |
| 39 | near_repeat-039 | label correct |
| 40 | near_repeat-036 | label correct |

**Summary (question sample, 40 pairs):** 0 labels wrong; 8 tagged ambiguous (7
complementary, 1 context dependent). All 8 sat in categories labelled with confidence,
so the remaining 560 unreviewed pairs likely hold more: worth a sweep.

## Decisions (data/REVIEW_SAMPLE_CONVERSATIONS.md, reviewer: Mabon ap Gwyn)

| # | id | verdict |
|---|---|---|
| 1 | conv-retail-003 | label correct |
| 2 | conv-billing-005 | label correct |
| 3 | conv-retail-010 | label correct |
| 4 | conv-retail-011 | label correct |
| 5 | conv-retail-017 | ambiguous: context_dependent (the late show's 18+ rule is only in the writer's note, never in the chat) |
| 6 | conv-billing-020 | label correct (cut-off stated in the chat, message 4) |
| 7 | conv-long-billing-006 | label correct |
| 8 | conv-retail-023 | label correct |
| 9 | conv-billing-024 | label correct |
| 10 | conv-services-030 | label correct |
| 11 | conv-services-033 | label correct |
| 12 | conv-billing-037 | label correct |
| 13 | conv-services-039 | label correct |
| 14 | conv-long-services-013 | label correct (dates stated in both chats) |
| 15 | conv-retail-042 | label correct |
| 16 | conv-services-046 | ambiguous: context_dependent (the chat was about specific branches; delivery may vary by branch) |
| 17 | conv-services-050 | label correct |
| 18 | conv-retail-053 | label correct |
| 19 | conv-retail-056 | label correct |
| 20 | conv-services-058 | label correct |

**Summary (conversation sample, 20 pairs):** 0 labels wrong; 2 tagged ambiguous
(context dependent). Pattern: the data-writing agents sometimes relied on facts that
appear only in their own note, not in the chat (row 5), or on scope the chat leaves
open (row 16).

**Overall (60 pairs reviewed):** no label was wrong outright; 10 of 60 (17%) were
ambiguous. Next: a sweep of the unreviewed 780 pairs for likely-ambiguous ones, for
human confirmation.
