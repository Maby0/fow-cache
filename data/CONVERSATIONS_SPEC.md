# Conversation pairs: spec

Tests semantic caching inside multi-turn chats. Each line of a `data/conv-parts/*.jsonl`
file is one pair of conversations:

```json
{"id": "conv-billing-001", "subtype": "context_swap", "same_answer": false,
 "a": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, {"role": "user", "content": "..."}],
 "b": [...],
 "note": "one line: why the label is what it is"}
```

- `a` is the **cached** conversation: the assistant's reply to its final user message
  was stored in the cache. `b` is the **new** conversation. Both alternate user /
  assistant and **both end with a user message**.
- **The label rule.** `same_answer` is true only if one assistant reply would be a
  correct and complete reply to the final user message of *both* conversations, given
  everything said before it in each. If a reply would need to differ in any fact,
  name, number, product, action or yes/no outcome, it's false.
- Should-hit pairs must not depend on user-specific data that differs between the two
  (one customer's order status must never be served to another).

## Subtypes (10 of each per batch of 60)

Traps, `same_answer: false`. The final user messages are **identical**, or differ only
in trivial wording (case, "please", punctuation):

- `context_swap`: earlier turns are about a different thing (Netflix vs gym membership),
  so "cancel it" means something different.
- `detail_swap`: same topic, but one detail earlier differs (order 48213 vs 48231,
  premium vs basic plan, Tuesday vs Thursday, Manchester vs Leeds branch).
- `intent_flip`: the assistant's previous turn proposed a different action, so a short
  reply like "yes", "go ahead", "the second one" means something different
  ("Shall I cancel it?" vs "Shall I renew it?").

Should-hit, `same_answer: true`:

- `same_context_reworded`: same facts and same question, but the earlier turns are worded
  differently (different phrasing, different order of details). The final message may
  also be lightly reworded.
- `irrelevant_history`: the final user message is fully standalone ("What are your
  opening hours on Saturday?") and identical in both; the earlier turns are about
  different, unrelated things that don't change the answer.
- `same_context_extra_chatter`: same facts, but one conversation has extra small talk or
  an irrelevant side question earlier on.

## Length mix (per batch of 60, spread across subtypes)

- 20 short: 2-4 messages each
- 20 medium: 6-8 messages
- 20 long: 12-20 messages. Long ones should feel real: the key detail is mentioned
  early and then the chat wanders (other questions, clarifications) before the final
  message.

## Style

- UK English, realistic customer-service / assistant chat. Assistant turns are short,
  helpful and plausible. User turns vary: terse, chatty, typos sometimes.
- Final user messages in traps should be the short, context-dependent kind people
  really send: "cancel it", "yes please", "how much is that one?", "and for the other
  order?", "book it", "the second option", "what about Thursday?".
- Don't reuse the same template across pairs: vary products, names, numbers, wording.
- Fictional businesses and people only.
