# fow-cache (TypeScript)

**How often does your semantic cache serve the wrong answer?**

*fow = fly on the wall: it watches the whole conversation and speaks up when a cached
answer doesn't fit.*

A semantic cache reuses an LLM answer when a new question "means the same" as one it has
seen. Questions that differ by one word ("Track order 48213" vs "48231") score 0.99
similar, and in conversations, popular caches compare only the last message: "yes, cancel
it" about Netflix and "yes, cancel it" about a gym membership are the same string.

This is the TypeScript port of [fow-cache](https://github.com/Maby0/fow-cache) (also on
PyPI): the same benchmark data, the same guard, and the same results, verified to match the
Python package output exactly. Full findings, tables and the research log are in the
[main README](https://github.com/Maby0/fow-cache#readme).

```bash
npm install fow-cache
npm install @anthropic-ai/sdk          # for the guard's default LLM (optional peer)
npm install @langchain/core            # for the LangChain backend (optional peer)
```

## Test your cache

```ts
import { evaluate } from "fow-cache";

const report = await evaluate((cachedQ, newQ) => myCache.wouldHit(cachedQ, newQ));
console.log(report.toString());   // hit rate, wrong-answer rate, by category

const conv = await evaluate((cachedMsgs, newMsgs) => myCache.wouldHit(cachedMsgs, newMsgs),
  { dataset: "conversations", concurrency: 8 });
```

Checks can be async and return a boolean or a score (compared to `threshold`, default 0.5).
`report.bestThreshold(0.01)` finds the threshold with the most hits under a wrong-answer
budget. `ambiguous: "different" | "same" | "skip"` decides how pairs whose answer depends on
the application are scored (default: strict, as traps).

To run the benchmark through a real cache: `storeLookupCheck(store, lookup, reset)` for any
cache, or `langchainCheck(cache)` for a LangChain.js cache.

### In CI

```bash
npx fow-cache eval --check ./cache-check.js --max-wrong 0.05            # default export
npx fow-cache eval --check ./checks.mjs#wouldHit --dataset conversations
```

Exits 1 when more than `--max-wrong` of the traps get a wrong answer.

## The guard (multi-turn chats)

```ts
import { Guard, GuardedCache, InMemoryBackend, anthropicLlm, JevClient } from "fow-cache";

const guard = new Guard({ llm: anthropicLlm(), jev: new JevClient() });
const cache = new GuardedCache(new InMemoryBackend(), guard);   // or new LangChainBackend(yourCache)

async function handle(conversationId: string, userMessage: string) {
  const chat = guard.conversation(await loadState(conversationId));   // your storage
  const entry = chat.ask(userMessage);
  const hit = await cache.lookup(entry);
  const reply = hit ? hit.answer : await callYourModel(chat.messages, userMessage);
  if (!hit) await cache.store(entry, reply);
  await chat.add(userMessage, reply);        // every 4th exchange this updates the facts
  await saveState(conversationId, chat.toJSON());
  return reply;
}
```

- Every 4 exchanges, Claude Haiku 4.5 folds the chat into a short record of facts. On a
  candidate, both sides' final messages are rewritten into standalone requests and two
  [Jev](https://typesafe.ai) checks run (whole conversations, and the rewrites); the answer
  is served only if both pass. About 90% of genuine hits served, 3-6% of traps wrong,
  held-out on the benchmark.
- `check()` never throws: errors and timeouts (default 3 s; median ~1.2 s) are misses.
- Entries and state serialise to the same JSON as the Python package, so a cache written
  from Python can be read from TypeScript and the other way round.
- Backends: `InMemoryBackend`, `LangChainBackend`, or anything implementing
  `candidates(text, k)` and `store(text, answer, entry)`.
- Jev needs `TYPESAFE_API_KEY` or `OPENROUTER_API_KEY`; the Anthropic SDK reads
  `ANTHROPIC_API_KEY`. `llm` accepts any `(system, user) => Promise<string>`.

## Does it pay for itself?

```bash
npx fow-cache costs --model sonnet-5.5 --prompt-tokens 8000 --candidate-rate 0.2
```

Prints the guard's cost per turn and the hit rate at which it breaks even, for your model
and prompt size. Also available as `costs.breakEven(scenario)`.

## Licence

Code: MIT. Data: CC BY 4.0.
