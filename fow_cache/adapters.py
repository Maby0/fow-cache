"""Test a real cache with evaluate(), instead of an approximation of it.

Each pair runs against an empty cache: store the cached side, look up the new side,
report the similarity of the nearest entry. Evaluate at your cache's own threshold:

    from redisvl.extensions.cache.llm import SemanticCache
    from fow_cache import evaluate
    from fow_cache.adapters import redisvl_check

    cache = SemanticCache(name="fow-eval", distance_threshold=0.1, overwrite=True)
    report = evaluate(redisvl_check(cache), threshold=redisvl_threshold(cache))

For conversations, the cache is keyed on the final user message, as RedisVL and GPTCache
do by default: evaluate(redisvl_check(cache), dataset="conversations", ...).
"""


def _text(x):
    return x[-1]["content"] if isinstance(x, list) else x


def store_lookup_check(store, lookup, reset):
    """Generic adapter for any cache. store(text), lookup(text) -> score or bool,
    reset() empties the cache between pairs."""
    def check(a, b):
        reset()
        store(_text(a))
        return lookup(_text(b))
    return check


def redisvl_check(cache):
    """Similarity (1 - cosine distance) of the nearest entry in a redisvl SemanticCache.
    The cache is cleared before every pair, so use a dedicated cache name."""
    def lookup(text):
        hits = cache.check(prompt=text, num_results=1, distance_threshold=2.0)  # always return the nearest
        return 1.0 - float(hits[0]["vector_distance"]) if hits else 0.0

    return store_lookup_check(lambda text: cache.store(prompt=text, response="cached"), lookup, cache.clear)


def redisvl_threshold(cache):
    """The similarity threshold equivalent to the cache's own distance_threshold."""
    return 1.0 - float(cache.distance_threshold)


def gptcache_check(make_cache):
    """GPTCache hit (True/False) at its own threshold. make_cache() must return a freshly
    initialised gptcache.Cache (one per pair, since GPTCache has no clear()), e.g.

        def make_cache():
            c = Cache()
            init_similar_cache(data_dir=tempfile.mkdtemp(), cache_obj=c)
            return c

    GPTCache's score isn't exposed, so threshold sweeps aren't available."""
    from gptcache.adapter.api import get, put

    def check(a, b):
        cache = make_cache()
        put(_text(a), "cached", cache_obj=cache)
        return get(_text(b), cache_obj=cache) is not None

    return check


def langchain_check(cache, namespace="fow-cache-eval"):
    """LangChain cache hit (True/False) at the cache's own threshold. The cache is cleared
    before every pair, so use a dedicated one."""
    from langchain_core.outputs import Generation

    return store_lookup_check(lambda text: cache.update(text, namespace, [Generation(text="cached")]),
                              lambda text: cache.lookup(text, namespace) is not None, cache.clear)
