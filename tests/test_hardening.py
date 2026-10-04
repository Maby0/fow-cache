import asyncio
import time

from fow_cache import Entry, Guard, GuardedCache, InMemoryBackend
from fow_cache.adapters import store_lookup_check
from test_guard import FakeJev, FakeLLM, chat


class SlowJev(FakeJev):
    def noul(self, state, instructions):
        time.sleep(0.5)
        return super().noul(state, instructions)


class BrokenJev:
    def noul(self, state, instructions):
        raise ConnectionError("jev down")


def test_timeout_is_a_miss_and_returns_promptly():
    g = Guard(llm=FakeLLM(), jev=SlowJev(), timeout=0.1)
    t = time.monotonic()
    d = g.check(chat(g, "netflix").ask("cancel it"), chat(g, "netflix").ask("cancel it"))
    assert (d.serve, d.reason) == (False, "timeout") and time.monotonic() - t < 0.4


def test_error_is_a_miss():
    g = Guard(llm=FakeLLM(), jev=BrokenJev())
    d = g.check(chat(g, "netflix").ask("cancel it"), chat(g, "netflix").ask("cancel it"))
    assert (d.serve, d.reason) == (False, "error")


def test_different_context_stops_after_whole_check():
    g = Guard(llm=FakeLLM(), jev=FakeJev())
    d = g.check(chat(g, "netflix").ask("cancel it"), chat(g, "gym").ask("cancel it"))
    assert (d.serve, d.reason, d.rewrite_score) == (False, "whole_conversation", None)


def test_failed_facts_update_is_retried():
    calls = {"n": 0}

    def flaky(system, user):
        calls["n"] += 1
        if calls["n"] == 1:
            raise TimeoutError
        return '{"goal": "cancel netflix"}'

    g = Guard(llm=flaky, jev=FakeJev(), batch=2)
    c = g.conversation()
    c.add("cancel my netflix", "which plan?")
    c.add("premium", "ok")          # first fold attempt fails, nothing folded
    assert c.folded == 0
    c.add("thanks", "welcome")      # retried and succeeds
    assert c.folded == 2 and c.facts == {"goal": "cancel netflix"}


def test_state_round_trips():
    g = Guard(llm=FakeLLM(), jev=FakeJev())
    c = chat(g, "netflix")
    restored = g.conversation(c.to_dict())
    assert restored.to_dict() == c.to_dict()
    e = c.ask("cancel it")
    e.rewrite = "x"
    assert Entry.from_dict(e.to_dict()) == e


def test_async_api():
    g = Guard(llm=FakeLLM(), jev=FakeJev())
    c = g.conversation()

    async def run():
        for i in range(5):
            await c.aadd(f"msg {i}", "ok")
        return await g.acheck(c.ask("cancel it"), c.ask("cancel it"))

    assert asyncio.run(run()).serve


def test_guarded_cache_serves_only_matching_context():
    g = Guard(llm=FakeLLM(), jev=FakeJev())
    cache = GuardedCache(InMemoryBackend(), g)
    cache.store(chat(g, "netflix").ask("cancel it"), "Cancelled your Netflix premium plan.")
    hit = cache.lookup(chat(g, "netflix").ask("cancel it"))
    assert hit and hit.answer == "Cancelled your Netflix premium plan."
    assert cache.lookup(chat(g, "gym membership").ask("cancel it")) is None
    assert cache.lookup(chat(g, "netflix").ask("what's my balance?")) is None  # no candidate at all


def test_store_lookup_adapter_resets_between_pairs():
    store = []
    check = store_lookup_check(store.append, lambda t: float(t in store), store.clear)
    assert check("a", "a") == 1.0 and check("b", "a") == 0.0
    assert check([{"role": "user", "content": "x"}], [{"role": "user", "content": "x"}]) == 1.0
