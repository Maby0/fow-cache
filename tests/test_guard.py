import json

from fow_cache import Guard
from fow_cache.prompts import FACTS_BATCH_PROMPT


class FakeLLM:
    """Facts record the first user message; rewrites echo the summary plus final message."""

    def __init__(self):
        self.calls = []

    def __call__(self, system, user):
        self.calls.append(system)
        if system == FACTS_BATCH_PROMPT:
            first = user.split("Latest exchanges:\nUser: ", 1)[1].split("\n", 1)[0]
            return json.dumps({"goal": first})
        summary = user.split("Earlier conversation summary: ", 1)[1].split("\n", 1)[0]
        return summary + " | " + user.rstrip().rsplit("User: ", 1)[1]


class FakeJev:
    """Yes when the two texts given to it are identical apart from labels."""

    def noul(self, state, instructions):
        a, b = list(state.values())
        if isinstance(a, str) and "\n" in a:  # whole conversations: compare first lines
            a, b = a.split("\n", 1)[0], b.split("\n", 1)[0]
        return 0.9 if a == b else 0.1


def chat(guard, topic, n=5):
    c = guard.conversation()
    c.add(f"I want to cancel my {topic}", "Sure, which plan?")
    for i in range(n - 1):
        c.add(f"side question {i}", f"answer {i}")
    return c


def test_facts_fold_every_batch():
    llm = FakeLLM()
    g = Guard(llm=llm, jev=FakeJev(), batch=4)
    c = chat(g, "netflix", n=5)
    assert c.folded == 4 and llm.calls.count(FACTS_BATCH_PROMPT) == 1
    assert c.facts == {"goal": "I want to cancel my netflix"}


def test_same_final_message_different_context_is_not_served():
    g = Guard(llm=FakeLLM(), jev=FakeJev())
    cached = chat(g, "netflix").ask("cancel it")
    new = chat(g, "gym membership").ask("cancel it")
    d = g.check(cached, new)
    assert not d.serve and d.whole_score < g.whole_threshold


def test_same_context_is_served_and_rewrite_is_reused():
    llm = FakeLLM()
    g = Guard(llm=llm, jev=FakeJev())
    cached = chat(g, "netflix").ask("cancel it")
    assert g.check(cached, chat(g, "netflix").ask("cancel it")).serve
    calls = len(llm.calls)
    g.check(cached, chat(g, "netflix").ask("cancel it"))
    # cached side's rewrite is memoised on the entry; only the new side is rewritten
    assert len(llm.calls) - calls == 1 + 1  # one facts fold for the new chat, one rewrite
