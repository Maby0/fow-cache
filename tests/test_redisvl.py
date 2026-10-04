"""Runs against a real Redis (with the query engine) when REDIS_URL is set, as in CI."""
import hashlib
import os

import pytest

if not os.environ.get("FOW_REQUIRE_REDIS"):  # CI sets this, so a broken setup fails instead of skipping
    pytest.importorskip("redisvl")
    if not os.environ.get("REDIS_URL"):
        pytest.skip("REDIS_URL not set", allow_module_level=True)

from redisvl.extensions.cache.llm import SemanticCache  # noqa: E402
from redisvl.utils.vectorize import CustomVectorizer  # noqa: E402

from fow_cache import Guard, GuardedCache  # noqa: E402
from fow_cache.adapters import redisvl_check, redisvl_threshold  # noqa: E402
from fow_cache.cache import RedisVLBackend  # noqa: E402
from test_guard import FakeJev, FakeLLM, chat  # noqa: E402


def embed(text):
    """Deterministic toy embedding: bag of hashed words, so identical texts match exactly."""
    v = [0.0] * 64
    for w in text.lower().split():
        v[int(hashlib.md5(w.strip("?.!,").encode()).hexdigest(), 16) % 64] += 1.0
    n = sum(x * x for x in v) ** 0.5 or 1.0
    return [x / n for x in v]


@pytest.fixture
def cache():
    c = SemanticCache(name=f"fow-test-{os.getpid()}", distance_threshold=0.2, overwrite=True,
                      redis_url=os.environ["REDIS_URL"], vectorizer=CustomVectorizer(embed=embed))
    yield c
    c.delete()


def test_redisvl_check_scores_similarity(cache):
    check = redisvl_check(cache)
    assert check("Track order 48213", "track order 48213?") > 0.99
    assert check("Track order 48213", "what are your opening hours") < redisvl_threshold(cache)


def test_guarded_cache_on_redisvl(cache):
    g = Guard(llm=FakeLLM(), jev=FakeJev())
    gc = GuardedCache(RedisVLBackend(cache), g)
    gc.store(chat(g, "netflix").ask("cancel it"), "Cancelled your Netflix plan.")
    assert gc.lookup(chat(g, "netflix").ask("cancel it")).answer == "Cancelled your Netflix plan."
    assert gc.lookup(chat(g, "gym").ask("cancel it")) is None
