"""A guard for semantic caches in multi-turn chats.

The default design, chosen on the benchmark (see wiki/findings.md, Runs 5-9):

1. After every BATCH exchanges, an LLM (Haiku 4.5 by default) folds them into a short
   JSON record of facts. Do this off the request path, after the reply is sent.
2. When the cache finds a candidate, both sides' final messages are rewritten into
   standalone requests from their facts plus the messages since the last fold.
3. Two Jev checks run: whole conversations, and the two rewrites. Serve only if both
   pass. Held-out on the benchmark: about 90% of should-hit served, 3-6% of traps wrong.

The guard fails safe: if anything errors or the time budget runs out, the decision is a
miss (serve=False) and your app generates a fresh answer as it would without a cache.

    guard = Guard(llm=anthropic_llm(), jev=JevClient())
    chat = guard.conversation()               # or guard.conversation(saved_state)
    chat.add(user_msg, reply)                 # after each reply (aadd() in async code)
    saved_state = chat.to_dict()              # persist per conversation id
    entry = chat.ask(next_user_msg)           # snapshot to look up / store with an answer
    decision = guard.check(cached_entry, entry)   # acheck() in async code
"""
import asyncio
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from dataclasses import asdict, dataclass, field

from .prompts import CONV_INSTRUCTIONS, FACTS_BATCH_PROMPT, QUESTION_INSTRUCTIONS, REWRITE_LITE_PROMPT

log = logging.getLogger("fow_cache")

BATCH = 4  # exchanges per facts update
RECENT = 7  # minimum messages the rewrite sees verbatim
WHOLE_THRESHOLD = 0.70  # from two-fold held-out tuning (benchmark Run 6)
REWRITE_THRESHOLD = 0.15
TIMEOUT = 3.0  # seconds for a whole check; median is ~1.2 s, p90 ~1.5 s (Run 9)


def anthropic_llm(model="claude-haiku-4-5", client=None, max_tokens=1024, timeout=10.0):
    """llm(system, user) -> text, through the Anthropic SDK (pip install fow-cache[anthropic])."""
    import anthropic

    client = client or anthropic.Anthropic(timeout=timeout, max_retries=1)

    def llm(system, user):
        resp = client.messages.create(model=model, max_tokens=max_tokens, system=system,
                                      messages=[{"role": "user", "content": user}])
        return "".join(b.text for b in resp.content if b.type == "text").strip()

    return llm


def transcript(messages):
    return "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in messages)


def _parse_record(text):
    """The JSON object in an LLM reply (models sometimes add a fence or preamble), or None."""
    try:
        record = json.loads(text[text.index("{"):text.rindex("}") + 1])
        return record if isinstance(record, dict) else None
    except ValueError:
        return None


@dataclass
class Entry:
    """A conversation at the moment a user message arrives: what gets looked up, and
    what gets stored alongside a cached answer (via to_dict / from_dict)."""
    messages: list  # ends with the user message being answered
    facts: dict
    folded: int  # exchanges folded into facts
    rewrite: str = None  # filled lazily by the guard, then reused

    @property
    def final_message(self):
        return self.messages[-1]["content"]

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(list(d["messages"]), dict(d["facts"]), int(d["folded"]), d.get("rewrite"))


class Conversation:
    """Running state for one chat. Persist it between requests with to_dict() and
    restore it with guard.conversation(state)."""

    def __init__(self, guard, state=None):
        state = state or {}
        self.guard = guard
        self.messages = list(state.get("messages", []))
        self.facts = dict(state.get("facts", {}))
        self.folded = int(state.get("folded", 0))

    def to_dict(self):
        return {"messages": self.messages, "facts": self.facts, "folded": self.folded}

    def add(self, user, assistant):
        """Record one exchange. Every BATCH exchanges this makes one LLM call to update the
        facts, so call it after the reply has gone out. If the call fails, the exchanges
        stay unfolded and are retried on the next add()."""
        self.messages += [{"role": "user", "content": user}, {"role": "assistant", "content": assistant}]
        while len(self.messages) // 2 - self.folded >= self.guard.batch:
            block = self.messages[2 * self.folded:2 * (self.folded + self.guard.batch)]
            try:
                text = self.guard.llm(FACTS_BATCH_PROMPT, f"Current record:\n{json.dumps(self.facts)}\n\n"
                                      f"Latest exchanges:\n{transcript(block)}")
            except Exception:
                log.warning("fow-cache: facts update failed; will retry on the next exchange", exc_info=True)
                return
            record = _parse_record(text)
            if record is None:
                log.warning("fow-cache: facts update returned no JSON object; keeping the previous record")
            else:
                self.facts = record
            self.folded += self.guard.batch

    async def aadd(self, user, assistant):
        await asyncio.to_thread(self.add, user, assistant)

    def ask(self, user):
        return Entry(self.messages + [{"role": "user", "content": user}], dict(self.facts), self.folded)


@dataclass
class Decision:
    serve: bool
    reason: str  # "pass", "whole_conversation", "rewrite", "timeout" or "error"
    whole_score: float = None
    rewrite_score: float = None
    rewrites: tuple = field(default=())
    seconds: float = 0.0


class Guard:
    def __init__(self, llm=None, jev=None, batch=BATCH, whole_threshold=WHOLE_THRESHOLD,
                 rewrite_threshold=REWRITE_THRESHOLD, timeout=TIMEOUT, max_workers=16):
        if jev is None:
            from .jev import JevClient
            jev = JevClient(timeout=timeout, retries=1)
        self.llm = llm or anthropic_llm()
        self.jev, self.batch, self.timeout = jev, batch, timeout
        self.whole_threshold, self.rewrite_threshold = whole_threshold, rewrite_threshold
        # Long-lived pool: a timed-out check must not block the caller while its calls finish.
        self._pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="fow-cache")

    def conversation(self, state=None):
        return Conversation(self, state)

    def rewrite(self, entry):
        if entry.rewrite is None:
            start = max(0, min(2 * entry.folded, len(entry.messages) - RECENT))
            entry.rewrite = self.llm(REWRITE_LITE_PROMPT, f"Earlier conversation summary: {json.dumps(entry.facts)}\n\n"
                                     f"Recent messages:\n{transcript(entry.messages[start:])}")
        return entry.rewrite

    def check(self, cached, new):
        """Should `new` be answered with the answer stored for `cached`? Never raises:
        errors and timeouts come back as serve=False. Only the calling thread waits on
        pool tasks, so concurrent checks can't starve the pool."""
        t0 = time.monotonic()
        left = lambda: max(0.0, self.timeout - (time.monotonic() - t0))
        whole = self._pool.submit(self.jev.noul, {"cached_conversation": transcript(cached.messages),
                                                  "new_conversation": transcript(new.messages)}, CONV_INSTRUCTIONS)
        ra, rb = self._pool.submit(self.rewrite, cached), self._pool.submit(self.rewrite, new)
        try:
            w = whole.result(timeout=left())
            if w < self.whole_threshold:  # already a miss: don't wait for the rewrites
                ra.cancel(), rb.cancel()
                return Decision(False, "whole_conversation", w, seconds=time.monotonic() - t0)
            rewrites = (ra.result(timeout=left()), rb.result(timeout=left()))
            rw = self._pool.submit(self.jev.noul, {"cached_question": rewrites[0], "new_question": rewrites[1]},
                                   QUESTION_INSTRUCTIONS).result(timeout=left())
        except FutureTimeout:
            log.warning("fow-cache: check exceeded %.1fs; treating as a miss", self.timeout)
            return Decision(False, "timeout", seconds=time.monotonic() - t0)
        except Exception:
            log.warning("fow-cache: check failed; treating as a miss", exc_info=True)
            return Decision(False, "error", seconds=time.monotonic() - t0)
        serve = rw >= self.rewrite_threshold
        return Decision(serve, "pass" if serve else "rewrite", w, rw, rewrites, time.monotonic() - t0)

    async def acheck(self, cached, new):
        return await asyncio.to_thread(self.check, cached, new)

    def replay(self, messages):
        """Build an Entry from a full message list ending in a user message (for evaluation)."""
        chat = self.conversation()
        for i in range(0, len(messages) - 1, 2):
            chat.add(messages[i]["content"], messages[i + 1]["content"])
        return chat.ask(messages[-1]["content"])
