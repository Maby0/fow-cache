"""GuardedCache: your existing semantic cache finds candidates, the guard decides.

    from redisvl.extensions.cache.llm import SemanticCache
    from fow_cache import Guard, GuardedCache
    from fow_cache.cache import RedisVLBackend

    cache = GuardedCache(RedisVLBackend(SemanticCache(name="chat", distance_threshold=0.3)), Guard())

    entry = chat.ask(user_message)          # chat = guard.conversation(saved_state)
    hit = cache.lookup(entry)
    if hit:
        reply = hit.answer
    else:
        reply = call_your_model(...)
        cache.store(entry, reply)

The backend only has to find candidates, so give it a looser threshold than you would
unguarded: the guard does the precise check. Candidates are found by the final user
message, the way GPTCache and RedisVL work by default.
"""
import asyncio
import json
from dataclasses import dataclass

from .guard import Decision, Entry


@dataclass
class Hit:
    answer: str
    decision: Decision
    cached: Entry


class InMemoryBackend:
    """Candidates by a similarity function over final messages; for tests and small apps.
    similarity(a, b) -> 0..1, default case- and punctuation-insensitive exact match."""

    def __init__(self, similarity=None, threshold=0.5):
        self.similarity = similarity or (lambda a, b: float(_norm(a) == _norm(b)))
        self.threshold, self.items = threshold, []

    def candidates(self, text, k):
        scored = sorted(((self.similarity(t, text), answer, entry) for t, answer, entry in self.items),
                        key=lambda x: -x[0])
        return [(answer, entry) for score, answer, entry in scored[:k] if score >= self.threshold]

    def store(self, text, answer, entry):
        self.items.append((text, answer, entry))


def _norm(s):
    return " ".join("".join(c for c in s.lower() if c.isalnum() or c.isspace()).split())


class RedisVLBackend:
    """Wraps a redisvl SemanticCache (pip install fow-cache[redis]). The guard's entry is
    stored in the cache entry's metadata."""

    KEY = "fow_entry"

    def __init__(self, semantic_cache):
        self.cache = semantic_cache

    def candidates(self, text, k):
        hits = self.cache.check(prompt=text, num_results=k, return_fields=["response", "metadata"])
        return [(h["response"], (h.get("metadata") or {}).get(self.KEY)) for h in hits
                if (h.get("metadata") or {}).get(self.KEY)]

    def store(self, text, answer, entry):
        self.cache.store(prompt=text, response=answer, metadata={self.KEY: entry})


def _pack(answer, entry):
    return json.dumps({"fow_cache": 1, "answer": answer, "entry": entry})


def _unpack(value):
    """(answer, entry) from a packed value, or None for values fow-cache didn't write."""
    try:
        d = json.loads(value)
    except (TypeError, ValueError):
        return None
    return (d["answer"], d["entry"]) if isinstance(d, dict) and d.get("fow_cache") == 1 else None


class GPTCacheBackend:
    """Wraps an initialised gptcache.Cache (e.g. from gptcache.adapter.api.init_similar_cache).
    GPTCache stores only a question and an answer, so the answer and the guard's entry are
    packed together as JSON: use a cache dedicated to the guard. GPTCache returns at most
    one candidate per lookup."""

    def __init__(self, cache_obj):
        self.cache = cache_obj

    def candidates(self, text, k):
        from gptcache.adapter.api import get

        found = _unpack(get(text, cache_obj=self.cache))
        return [found] if found else []

    def store(self, text, answer, entry):
        from gptcache.adapter.api import put

        put(text, _pack(answer, entry), cache_obj=self.cache)


class LangChainBackend:
    """Wraps any LangChain cache (langchain_core.caches.BaseCache), e.g. a semantic cache from
    langchain-community or a vector-store integration. The answer and the guard's entry are
    packed as JSON in the stored generation's text, so use a cache (or `namespace`) dedicated
    to the guard. LangChain caches return at most one entry per lookup."""

    def __init__(self, cache, namespace="fow-cache"):
        self.cache, self.namespace = cache, namespace  # passed as LangChain's llm_string

    def candidates(self, text, k):
        generations = self.cache.lookup(text, self.namespace) or []
        found = [_unpack(g.text) for g in generations[:1]]
        return [f for f in found if f]

    def store(self, text, answer, entry):
        from langchain_core.outputs import Generation

        self.cache.update(text, self.namespace, [Generation(text=_pack(answer, entry))])


class GuardedCache:
    def __init__(self, backend, guard, k=3):
        """k: candidates checked per lookup, best first; the first that passes is served."""
        self.backend, self.guard, self.k = backend, guard, k

    def lookup(self, entry):
        for answer, cached in self.backend.candidates(entry.final_message, self.k):
            cached_entry = Entry.from_dict(cached)
            decision = self.guard.check(cached_entry, entry)
            if decision.serve:
                return Hit(answer, decision, cached_entry)
        return None

    def store(self, entry, answer):
        self.backend.store(entry.final_message, answer, entry.to_dict())

    async def alookup(self, entry):
        return await asyncio.to_thread(self.lookup, entry)

    async def astore(self, entry, answer):
        await asyncio.to_thread(self.store, entry, answer)
