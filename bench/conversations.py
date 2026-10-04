"""Score multi-turn conversation pairs (data/conv-parts/*.jsonl) with several ways of
deciding a semantic-cache hit inside a chat:

  last-*     only the final user message, which is what GPTCache does by default
  full-jev   both whole transcripts sent to Jev
  notes-jev  a running 4-5 word note per exchange (written by Haiku), plus the final message
  facts-jev  a running JSON record of facts (updated by Haiku after every exchange), plus the final message
  window-jev the last few messages of each conversation, verbatim
  hybrid-jev facts v2 for everything before the last few messages, plus those messages verbatim
  rewrite-*  the final message rewritten by Haiku into a standalone question, then compared

Haiku output is cached in results/derived/ so re-runs only pay for what changed.
Needs OPENROUTER_API_KEY (Jev and Haiku both go through OpenRouter)."""
import argparse
import csv
import hashlib
import json
import os
import subprocess
import tempfile
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fow_cache.prompts import (CONV_INSTRUCTIONS, FACTS_BATCH_PROMPT, FACTS_PROMPT_V2,
                                  REWRITE_LITE_PROMPT, REWRITE_PROMPT)
from jev import INSTRUCTIONS, load_env_file, provider

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "conv-scores"
DERIVED = ROOT / "results" / "derived"
HAIKU = "anthropic/claude-haiku-4.5"
EMBEDDERS = {"langcache": "redis/langcache-embed-v1", "mpnet": "sentence-transformers/all-mpnet-base-v2"}

FACTS_PROMPT = """You keep a compact running record of a customer-service conversation. It is used later to decide whether a cached reply can be reused for another conversation.

Given the current record (JSON) and the latest exchange, return the updated record as one JSON object and nothing else.

Rules:
- Keys are short snake_case. Values are short strings.
- Copy names, IDs, order and account numbers, amounts, dates, times, places, product and plan names exactly as written. Never paraphrase or round them.
- Always include "topic" (what the conversation is about right now) and "pending" (what the assistant last offered, proposed or asked the user, or "" if nothing).
- At most 8 keys. Drop facts that no longer matter.
- Ignore pleasantries and small talk."""

BATCH = 4  # exchanges folded into the facts per update in the batched variant

FACTS2_INSTRUCTIONS = CONV_INSTRUCTIONS + (
    " The context records were written independently, so their wording and key names "
    "may differ: only differences in meaning count."
)

FACTS3_INSTRUCTIONS = (
    "A cache stored the assistant's reply to final_message in the cached conversation. "
    "Would that exact same reply be a correct and complete reply to final_message in the "
    "new conversation? First decide what each final_message refers to: a standalone "
    "question refers only to itself, while a short reply such as 'yes', 'book it', 'the "
    "second one' or 'how much is that?' refers to previous_assistant_message and the "
    "context. Answer no if the two final messages end up referring to different things, "
    "such as a different product, account, order, number, date, time, place or person, or "
    "a different action being agreed to. Differences in the context that the final "
    "messages do not depend on don't matter, and the context records were written "
    "independently, so differences in wording or key names don't matter either."
)

NOTES_PROMPT = """Summarise this exchange from a customer-service chat in 4 or 5 words. Return only those words."""


def load_pairs():
    pairs = []
    for path in sorted((ROOT / "data" / "conv-parts").glob("*.jsonl")) + sorted((ROOT / "data" / "conv-long").glob("*.jsonl")):
        pairs += [json.loads(line) for line in open(path) if line.strip()]
    return pairs


def length_bucket(p):
    n = max(len(p["a"]), len(p["b"]))
    return "short" if n <= 4 else "medium" if n <= 8 else "long" if n <= 20 else "very_long"


def transcript(conv):
    return "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in conv)


def exchanges(conv):
    """(user, assistant) pairs before the final user message."""
    return [(conv[i]["content"], conv[i + 1]["content"]) for i in range(0, len(conv) - 1, 2)]


def post(url, key, body, timeout=60):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(5):
        try:
            t = time.monotonic()
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r), time.monotonic() - t
        except Exception as e:  # retry transient failures
            err = e
            time.sleep(2 ** attempt)
    raise RuntimeError(err)


def claude_cli(system, user):
    """Haiku through the local Claude Code CLI, billed to the logged-in claude.ai plan
    instead of an API key. No tools, settings, MCP servers or thinking, run from an empty
    directory so no CLAUDE.md is picked up. Not temperature 0, so outputs can differ
    slightly from the API path."""
    cmd = ["claude", "-p", user, "--model", "claude-haiku-4-5", "--system-prompt", system,
           "--tools", "", "--setting-sources", "", "--strict-mcp-config",
           "--no-session-persistence", "--output-format", "json"]
    env = dict(os.environ, MAX_THINKING_TOKENS="0")
    for attempt in range(5):
        t = time.monotonic()
        with tempfile.TemporaryDirectory() as cwd:
            r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=180)
        try:
            out = json.loads(r.stdout)
            if not out.get("is_error"):
                return out["result"].strip(), time.monotonic() - t
            err = out.get("result")
        except json.JSONDecodeError:
            err = r.stderr[-300:] or r.stdout[-300:]
        time.sleep(2 ** attempt * 5)  # usage-limit or transient errors: back off
    raise RuntimeError(f"claude -p failed: {err}")


class Derived:
    """Disk cache of Haiku outputs, keyed by prompt kind + input hash."""

    def __init__(self, key, via="openrouter"):
        self.key = key
        self.via = via
        # Direct-API outputs (temperature 0) get their own cache so they never mix with the
        # OpenRouter/CLI outputs in haiku.json.
        self.path = DERIVED / ("haiku-anthropic.json" if via == "anthropic" else "haiku.json")
        self.client = None
        if via == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic()
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {}
        self.lock = threading.Lock()
        self.latencies = []

    def haiku(self, system, user, max_tokens=300):
        h = hashlib.sha1(json.dumps([system, user]).encode()).hexdigest()
        if h in self.data:
            return self.data[h]
        if self.via == "claude-cli":
            text, latency = claude_cli(system, user)
        elif self.via == "anthropic":
            t = time.monotonic()
            resp = self.client.messages.create(model="claude-haiku-4-5", max_tokens=max_tokens, extra_body={"temperature": 0},
                                               system=system, messages=[{"role": "user", "content": user}])
            latency = time.monotonic() - t
            text = "".join(b.text for b in resp.content if b.type == "text").strip()
        else:
            resp, latency = post("https://openrouter.ai/api/v1/chat/completions", self.key, {
                "model": HAIKU, "temperature": 0, "max_tokens": max_tokens,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            })
            text = resp["choices"][0]["message"]["content"].strip()
        with self.lock:
            self.data[h] = text
            self.latencies.append(latency)
            if len(self.latencies) % 200 == 0:
                self.save()
        return text

    def save(self):
        DERIVED.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, indent=0))
        tmp.replace(self.path)

    def facts(self, conv, prompt=FACTS_PROMPT):
        record = {}
        for u, a in exchanges(conv):
            text = self.haiku(prompt, f"Current record:\n{json.dumps(record)}\n\nLatest exchange:\nUser: {u}\nAssistant: {a}")
            try:  # Haiku sometimes wraps the JSON in a fence or a preamble
                record = json.loads(text[text.index("{"):text.rindex("}") + 1])
            except ValueError:
                pass  # keep the previous record rather than lose context
        return record

    def facts_batched(self, conv, batch=BATCH):
        """Facts updated once per BATCH exchanges (one Haiku call per block) instead of
        after every exchange: roughly a third of the always-on cost."""
        record, ex = {}, exchanges(conv)
        for i in range(0, len(ex) - len(ex) % batch, batch):
            block = "\n".join(f"User: {u}\nAssistant: {a}" for u, a in ex[i:i + batch])
            text = self.haiku(FACTS_BATCH_PROMPT, f"Current record:\n{json.dumps(record)}\n\nLatest exchanges:\n{block}")
            try:
                record = json.loads(text[text.index("{"):text.rindex("}") + 1])
            except ValueError:
                pass
        return record

    def notes(self, conv):
        return [self.haiku(NOTES_PROMPT, f"User: {u}\nAssistant: {a}", max_tokens=30) for u, a in exchanges(conv)]

    def rewrite(self, conv):
        return self.haiku(REWRITE_PROMPT, transcript(conv), max_tokens=150)

    def rewrite_window(self, conv):
        """Rewrite from the last few messages only: no always-on work at all."""
        return self.haiku(REWRITE_PROMPT, transcript(conv[-RECENT:]), max_tokens=150)

    def rewrite_batched(self, conv, batch=BATCH):
        """Rewrite from batched facts plus every message since the last batch (at least
        the last RECENT), as it would run in production between batch updates."""
        done = (len(exchanges(conv)) // batch) * batch
        tail = conv[min(2 * done, len(conv) - RECENT):] if len(conv) > RECENT else conv
        earlier = self.facts_batched(conv[:2 * done], batch) if done else {}
        return self.haiku(REWRITE_LITE_PROMPT, f"Earlier conversation summary: {json.dumps(earlier)}\n\n"
                          f"Recent messages:\n{transcript(tail)}", max_tokens=150)

    def rewrite_lite(self, conv):
        """Rewrite from the running facts (already maintained off the request path) plus
        the last few messages, so the request-path call stays small however long the chat."""
        earlier = self.facts(conv[:-RECENT], FACTS_PROMPT_V2) if len(conv) > RECENT else {}
        return self.haiku(REWRITE_LITE_PROMPT, f"Earlier conversation summary: {json.dumps(earlier)}\n\n"
                          f"Recent messages:\n{transcript(conv[-RECENT:])}", max_tokens=150)


def jev(state, instructions, endpoint, key, model):
    resp, latency = post(endpoint, key, {
        "model": model, "state": state,
        "questions": {"same_answer": {"type": "noul", "instructions": instructions}},
    }, timeout=30)
    return resp["answers"]["same_answer"]["noul"], latency


RECENT = 7  # messages kept verbatim by the window and hybrid strategies: 3 exchanges + the final message

HYBRID_INSTRUCTIONS = (
    "A cache stored the assistant's reply to the final message of recent_messages in the "
    "cached conversation. Would that exact same reply be a correct and complete reply to "
    "the final message of recent_messages in the new conversation? earlier_context is a "
    "summary of everything said before recent_messages. First decide what each final "
    "message refers to, using recent_messages and earlier_context. Answer no if the two "
    "final messages end up referring to different things, such as a different product, "
    "account, order, number, date, time, place or person, or a different action being "
    "agreed to. Differences that the final messages do not depend on don't matter, and the "
    "summaries were written independently, so differences in wording or key names don't "
    "matter either."
)


def jev_states(p, d, names):
    """(state, instructions) for each requested Jev-based strategy. Lazy, so Haiku is
    only called for the strategies being run."""
    a, b = p["a"], p["b"]
    last_a, last_b = a[-1]["content"], b[-1]["content"]

    def prev(c):
        return c[-2]["content"] if len(c) > 1 else ""

    def facts2(c):
        return {"context": d.facts(c, FACTS_PROMPT_V2), "previous_assistant_message": prev(c), "final_message": c[-1]["content"]}

    def hybrid(c):
        return {"earlier_context": d.facts(c[:-RECENT], FACTS_PROMPT_V2) if len(c) > RECENT else {},
                "recent_messages": transcript(c[-RECENT:])}

    build = {
        "last-jev": lambda: ({"cached_question": last_a, "new_question": last_b}, INSTRUCTIONS),
        "full-jev": lambda: ({"cached_conversation": transcript(a), "new_conversation": transcript(b)}, CONV_INSTRUCTIONS),
        "window-jev": lambda: ({"cached_recent_messages": transcript(a[-RECENT:]), "new_recent_messages": transcript(b[-RECENT:])}, CONV_INSTRUCTIONS),
        "notes-jev": lambda: ({"cached": {"notes": d.notes(a), "final_message": last_a},
                               "new": {"notes": d.notes(b), "final_message": last_b}}, CONV_INSTRUCTIONS),
        "facts-jev": lambda: ({"cached": {"context": d.facts(a), "final_message": last_a},
                               "new": {"context": d.facts(b), "final_message": last_b}}, CONV_INSTRUCTIONS),
        "facts2-jev": lambda: ({"cached": facts2(a), "new": facts2(b)}, FACTS2_INSTRUCTIONS),
        "facts3-jev": lambda: ({"cached": facts2(a), "new": facts2(b)}, FACTS3_INSTRUCTIONS),
        "hybrid-jev": lambda: ({"cached": hybrid(a), "new": hybrid(b)}, HYBRID_INSTRUCTIONS),
        "rewrite-lite-jev": lambda: ({"cached_question": d.rewrite_lite(a), "new_question": d.rewrite_lite(b)}, INSTRUCTIONS),
        "rewrite-window-jev": lambda: ({"cached_question": d.rewrite_window(a), "new_question": d.rewrite_window(b)}, INSTRUCTIONS),
        "rewrite-batch-jev": lambda: ({"cached_question": d.rewrite_batched(a), "new_question": d.rewrite_batched(b)}, INSTRUCTIONS),
        "rewrite-batch2-jev": lambda: ({"cached_question": d.rewrite_batched(a, 2), "new_question": d.rewrite_batched(b, 2)}, INSTRUCTIONS),
        "rewrite-batch8-jev": lambda: ({"cached_question": d.rewrite_batched(a, 8), "new_question": d.rewrite_batched(b, 8)}, INSTRUCTIONS),
        "rewrite-jev": lambda: ({"cached_question": d.rewrite(a), "new_question": d.rewrite(b)}, INSTRUCTIONS),
    }
    return {n: build[n]() for n in names}


SUFFIX = ""  # appended to output names, e.g. "-api" for a direct-API run


def write(name, pairs, scores, latencies=None):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / f"{name}{SUFFIX}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "subtype", "length", "same_answer", "score", "latency_s"])
        for i, (p, s) in enumerate(zip(pairs, scores)):
            w.writerow([p["id"], p["subtype"], length_bucket(p), p["same_answer"], f"{s:.4f}",
                        f"{latencies[i]:.3f}" if latencies else ""])


def run_embeddings(pairs, d, only):
    from sentence_transformers import SentenceTransformer
    texts = {"last": ([p["a"][-1]["content"] for p in pairs], [p["b"][-1]["content"] for p in pairs])}
    if any(n.startswith("rewrite-") for n in only):
        with ThreadPoolExecutor(max_workers=8) as ex:
            texts["rewrite"] = (list(ex.map(lambda p: d.rewrite(p["a"]), pairs)),
                                list(ex.map(lambda p: d.rewrite(p["b"]), pairs)))
    for short, model_name in EMBEDDERS.items():
        model = None
        for kind, (ta, tb) in texts.items():
            name = f"{kind}-{short}"
            if name not in only:
                continue
            model = model or SentenceTransformer(model_name)
            ea = model.encode(ta, normalize_embeddings=True)
            eb = model.encode(tb, normalize_embeddings=True)
            write(name, pairs, (ea * eb).sum(axis=1))
            print(f"wrote {name}")


def main():
    jev_names = ["last-jev", "full-jev", "window-jev", "notes-jev", "facts-jev", "facts2-jev", "facts3-jev", "hybrid-jev", "rewrite-jev", "rewrite-lite-jev", "rewrite-window-jev", "rewrite-batch-jev", "rewrite-batch2-jev", "rewrite-batch8-jev"]
    embed_names = [f"{k}-{e}" for k in ("last", "rewrite") for e in EMBEDDERS]
    ap = argparse.ArgumentParser()
    ap.add_argument("--env-file", action="append", default=[], help="repeatable")
    ap.add_argument("--haiku-via", choices=["openrouter", "claude-cli", "anthropic"], default="openrouter",
                    help="claude-cli: Haiku through Claude Code on your claude.ai plan; anthropic: the Anthropic API "
                         "(ANTHROPIC_API_KEY), temperature 0, separate output cache")
    ap.add_argument("--suffix", default="", help="appended to output CSV names, e.g. -api")
    ap.add_argument("--only", help="comma-separated strategies (default: all): " + ",".join(jev_names + embed_names))
    args = ap.parse_args()
    global SUFFIX
    SUFFIX = args.suffix
    for f in args.env_file:
        load_env_file(f)
    only = args.only.split(",") if args.only else jev_names + embed_names
    pairs = load_pairs()
    endpoint, key, model = provider()
    d = Derived(key, args.haiku_via)
    try:
        run_embeddings(pairs, d, only)
        wanted = [n for n in jev_names if n in only]
        if wanted:
            with ThreadPoolExecutor(max_workers=8) as ex:
                states = list(ex.map(lambda p: jev_states(p, d, wanted), pairs))
            d.save()
            for name in wanted:
                with ThreadPoolExecutor(max_workers=8) as ex:
                    res = list(ex.map(lambda s: jev(*s[name], endpoint, key, model), states))
                write(name, pairs, [r[0] for r in res], [r[1] for r in res])
                lat = sorted(r[1] for r in res)
                print(f"wrote {name}; median Jev latency {lat[len(lat)//2]*1000:.0f} ms")
    finally:
        d.save()
    if d.latencies:
        lat = sorted(d.latencies)
        print(f"{len(lat)} new Haiku calls; median {lat[len(lat)//2]*1000:.0f} ms (off the request path)")


if __name__ == "__main__":
    main()
