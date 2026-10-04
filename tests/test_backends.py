"""GuardedCache and evaluate adapters against real GPTCache and LangChain caches, in
exact-match configurations so no embedding model is needed."""
import os
import tempfile

import pytest

from fow_cache import Guard, GuardedCache
from fow_cache.adapters import gptcache_check, langchain_check
from fow_cache.cache import GPTCacheBackend, LangChainBackend
from test_guard import FakeJev, FakeLLM, chat

REQUIRE = bool(os.environ.get("FOW_REQUIRE_BACKENDS"))  # CI: fail rather than skip


def _need(module):
    if REQUIRE:
        return __import__(module)
    return pytest.importorskip(module)


def gptcache_exact():
    _need("gptcache")
    from gptcache import Cache
    from gptcache.manager.factory import manager_factory
    from gptcache.processor.pre import get_prompt

    c = Cache()
    c.init(pre_embedding_func=get_prompt, data_manager=manager_factory("map", data_dir=tempfile.mkdtemp()))
    return c


def langchain_memory():
    _need("langchain_core")
    from langchain_core.caches import InMemoryCache

    return InMemoryCache()


@pytest.mark.parametrize("make_backend", [lambda: GPTCacheBackend(gptcache_exact()),
                                          lambda: LangChainBackend(langchain_memory())],
                         ids=["gptcache", "langchain"])
def test_guarded_cache_round_trip(make_backend):
    g = Guard(llm=FakeLLM(), jev=FakeJev())
    cache = GuardedCache(make_backend(), g)
    cache.store(chat(g, "netflix").ask("cancel it"), "Cancelled your Netflix plan.")
    assert cache.lookup(chat(g, "netflix").ask("cancel it")).answer == "Cancelled your Netflix plan."
    assert cache.lookup(chat(g, "gym").ask("cancel it")) is None       # candidate found, guard says no
    assert cache.lookup(chat(g, "netflix").ask("hello")) is None       # no candidate


def test_backends_ignore_entries_fow_cache_did_not_write():
    lc = langchain_memory()
    from langchain_core.outputs import Generation

    lc.update("cancel it", "fow-cache", [Generation(text="a plain cached answer")])
    assert LangChainBackend(lc).candidates("cancel it", 3) == []


def test_langchain_check():
    check = langchain_check(langchain_memory())
    assert check("Track order 48213", "Track order 48213") is True
    assert check("Track order 48213", "Track order 48231") is False


def test_gptcache_check():
    _need("gptcache")
    check = gptcache_check(gptcache_exact)
    assert check("Track order 48213", "Track order 48213") is True
    assert check("Track order 48213", "Track order 48231") is False
