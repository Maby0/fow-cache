import json

import pytest

from fow_cache import Guard, merge_fold
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


def test_record_makes_no_model_call_and_fold_catches_up():
    llm = FakeLLM()
    c = Guard(llm=llm, jev=FakeJev(), batch=2).conversation()
    c.record("cancel my netflix", "which plan?")
    c.record("premium", "ok")
    assert llm.calls == [] and c.fold_due
    assert c.fold() == {"facts": {"goal": "cancel my netflix"}, "folded": 2}
    assert not c.fold_due and llm.calls == [FACTS_BATCH_PROMPT]


def test_merge_fold_keeps_newer_messages_and_newer_facts():
    g = Guard(llm=FakeLLM(), jev=FakeJev(), batch=2)
    c = g.conversation()
    c.record("cancel my netflix", "which plan?")
    c.record("premium", "ok")
    background = g.conversation(c.to_dict())  # the worker's copy
    c.record("thanks", "welcome")  # the next request saves first
    latest = c.to_dict()
    merged = merge_fold(latest, background.fold())
    assert merged["messages"] == latest["messages"] and merged["folded"] == 2
    assert merged["facts"] == {"goal": "cancel my netflix"}
    assert merge_fold(merged, {"facts": {"goal": "stale"}, "folded": 0}) is merged


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


def test_decider_can_be_a_plain_function():
    jev = FakeJev()
    calls = []

    def decider(state, instructions):
        calls.append(sorted(state))
        return jev.noul(state, instructions)

    g = Guard(llm=FakeLLM(), decider=decider)
    assert g.check(chat(g, "netflix").ask("cancel it"), chat(g, "netflix").ask("cancel it")).serve
    assert not g.check(chat(g, "netflix").ask("cancel it"), chat(g, "gym").ask("cancel it")).serve
    assert ["cached_conversation", "new_conversation"] in calls and ["cached_question", "new_question"] in calls


def test_jev_is_the_older_name_for_decider():
    j = FakeJev()
    g = Guard(llm=FakeLLM(), jev=j)
    assert g.decider is j and g.jev is j
    with pytest.raises(TypeError):
        Guard(llm=FakeLLM(), decider=j, jev=j)
