# Long conversation pairs: spec

Same format, label rule and subtypes as `CONVERSATIONS_SPEC.md` (read that first), but
the conversations are **long**, to test whether strategies that read the whole chat
degrade, and whether summaries keep what matters. Files go in `data/conv-long/`.

## What's different

- **Length: 40-70 messages per conversation** (both conversations in a pair within ~10
  messages of each other). Alternating user / assistant, starting and ending with a user
  message.
- **The key detail is established early** (within the first 6 messages) and is not
  repeated afterwards, except where noted below. Then the chat wanders for a long time:
  several side questions on different topics, clarifications, small talk, a problem that
  gets resolved, the assistant giving long-ish policy answers. Realistic, not padding.
- **Then the final user message comes back to the key detail implicitly**: "ok, go
  ahead and book it", "so what do I owe in total?", "can you cancel that one then?",
  "send it to the address I gave you".
- **Distractors (at least half of the traps):** the *other* conversation's value appears
  somewhere in the middle in a role that doesn't matter. E.g. A books Tuesday and later
  says "my friend went on Thursday and loved it"; B books Thursday and says "I can't do
  Tuesdays". A strategy that just checks "is Thursday mentioned" will get it wrong.
- **Recent turns must not give the answer away for traps**: the last ~8 messages of the
  two conversations in a trap pair should be the same or near-identical, so only the early
  context distinguishes them.

## Mix per batch of 20

- Traps (`same_answer: false`): 4 `context_swap`, 4 `detail_swap`, 2 `intent_flip`
  (for intent_flip, the decisive proposal is made early and the user only agrees at the
  end: "Shall I set up the cancellation once we've sorted your bill?" ... long detour
  ... "yes go ahead").
- Should-hit (`same_answer: true`): 3 `same_context_reworded`, 4 `irrelevant_history`
  (final message fully standalone; the long histories are about different things), 3
  `same_context_extra_chatter` (same key facts, one conversation has a long extra detour).

Validate before finishing: parses, alternation, start/end on user, lengths 40-70,
subtype counts, unique ids, and that for every trap the final user messages match apart
from case/punctuation.
