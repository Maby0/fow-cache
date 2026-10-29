# Where fow-cache could plug in (as of 2026-10-29)

A source-level survey of public gateways, chat platforms and semantic-cache libraries:
does the "same last message, different context" problem show up there, and where would
the guard go? Repos were shallow-cloned from their default branches on 2026-10-29 and read,
not run. Line numbers will drift. Claims marked *unverified* were not confirmed in code.

## The pattern

Very few open-source chat stacks have a semantic cache, and the ones that do sidestep
multi-turn chats in one of three ways:

- **Match the last message only** (the bug): Higress `ai-cache` (`cacheKeyStrategy=lastQuestion`
  by default), GPTCache (`last_content` pre-processor by default), langgraph-redis
  `SemanticCacheMiddleware`, Dify's Annotation Reply, elysiajs/arona.
- **Match the whole prompt** (rarely hits after the first turns): LiteLLM (all message
  contents concatenated, `get_semantic_cache_prompt_from_messages`), LangChain chat models
  (the cache key is the serialised message list, system prompt included), Bifrost.
- **Give up on long chats**: Bifrost skips caching past `conversation_history_threshold`
  (default 3 messages); LiteLLM added `max_messages=4` on 2026-10-07
  ([77fc331](https://github.com/BerriAI/litellm/commit/77fc3315e55b5dc22a99b4f3c0a7d76eb7e8c367)).
- APISIX `ai-cache` is in between: it embeds the last message and hashes the rest into an
  exact-match partition, so it is safe but multi-turn chats rarely hit.

## Best targets

| Project | Why | Where the guard goes | Effort |
|---|---|---|---|
| Dify (Python, ~160k stars) | Annotation Reply is a curated FAQ semantic cache: `search_by_vector(query, top_k=1)` on the final query, no context check, then `direct_output` (`api/core/app/features/annotation_reply/annotation_reply.py`). Support bots are a core use case. | Wrap `AnnotationReplyFeature.query` with history from `TokenBufferMemory`; fold as a Celery task (`api/tasks/`). State fits the `Conversation` row. | Medium |
| langgraph-redis (Python, Redis-maintained) | `SemanticCacheMiddleware._extract_prompt` takes the last user message, with no thread or user scoping (`langgraph/middleware/redis/semantic_cache.py`). Already on RedisVL. | An optional `guard=` on the middleware; `request.messages` has the whole conversation. | Small |
| LiteLLM (Python, ~62k stars) | Most reach; the `max_messages` cutoff shows the pain. Pitch: lift the cutoff safely. | Subclass `BaseCache`: `async_get_cache(key, **kwargs)` gets `messages`; session id from `x-litellm-session-id`. *Unverified:* the proxy config can't name a custom cache (closed enum), so set `litellm.cache.cache` from a callback module. | Medium |
| Flowise (TS, ~56k stars) | Many support bots; only exact-match cache nodes today. | A community node, or Agentflow v2 Custom Function → Condition → Direct Reply. | Small–medium |
| elysiajs/arona (TS) | Live docs chatbot: semantic lookup on the raw last message even with history, only for prompts ≤72 chars (`src/modules/ai/service.ts`). | A small TS backend over its Redis KNN. Shows off the TS port. | Medium |

## Fits, but blocked

- **Chatwoot Captain** (Rails, support): the reply already runs as a Sidekiq job with the
  full conversation, but it's Ruby and under `enterprise/` (Chatwoot Enterprise License).
  FAQ pairs are a RAG tool, not a short-circuit.
- **Higress** (Go → proxy-Wasm), **APISIX** (Lua), **Bifrost** (Go): no Python/TS runtime
  in the plugin. Route: a small fow-cache HTTP service the plugin calls.

## Poor fit or not applicable

- Open WebUI: easiest hook (a Pipe function gets `__chat_id__` and `body.messages` and can
  return a string), but mostly personal assistants, so little repetition.
- LibreChat, LobeChat: personal assistants, tool-heavy; no plugin hook for this.
- Portkey gateway: "semantic" cache mode exists in the config schema but not in the
  open-source code. Kong: `ai-semantic-cache` is Enterprise-only. Envoy AI Gateway and
  Helicone: no semantic cache. Rasa OSS: no LLM calls (CALM is in Rasa Pro).

## Libraries

- **RedisVL `SemanticCache`**: entry id is `sha256(prompt + filters)`, so entries with
  the same prompt overwrite. fow-cache's `RedisVLBackend` hit this (only the latest chat
  ending in "cancel it" survived); fixed 2026-10-29 with a per-context filter. Metadata is
  a free dict, `num_results=k` works.
- **GPTCache**: last release 0.1.44 (2024-08). A 2026-09-22 burst added Anthropic adapters
  and a `JevEvaluation` (`gptcache/similarity_evaluation/jev.py`) that asks Jev about
  reuse compatibility. It sees the two questions and the cached answer, not the
  conversations, so it can't catch the context case. One candidate per lookup.
- **LangChain** semantic caches (Redis, Mongo Atlas, Cassandra, Cosmos, OpenSearch,
  SingleStore): `lookup`/`update` keyed on prompt + `llm_string`, one result, no metadata.
  `langchain-redis` inherits RedisVL's overwrite.
- **Upstash `@upstash/semantic-cache`** (TS, last push 2024-11): `topK: 1`, upsert by key,
  metadata is only the value. A fow-cache backend should use `@upstash/vector` directly
  (`query({topK: k, includeMetadata})`, `upsert` with a fresh id): about 30 lines.
  *Unverified:* metadata size limit.
- LlamaIndex, Vercel AI SDK: no LLM semantic cache found (code search only). Semantic
  Kernel: a concept sample only.

## Caveat

"Fits" means the code allows it. Reusing an answer across users is only safe when it
doesn't depend on that user's data or retrieved documents, which makes curated FAQ
answers (Dify annotations, Chatwoot FAQ pairs) the sweet spot.

## Next

1. Fix the RedisVL overwrite (done 2026-10-29).
2. Dify integration as the flagship demo: "context-safe annotation reply".
3. PR to langgraph-redis: optional guard on `SemanticCacheMiddleware`.
4. LiteLLM: an issue with benchmark numbers before any PR.
