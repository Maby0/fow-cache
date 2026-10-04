import assert from "node:assert/strict";
import { test } from "node:test";
import { Guard, GuardedCache, InMemoryBackend, LangChainBackend, unpack } from "../src/index.js";
import { FACTS_BATCH_PROMPT } from "../src/shared.js";
import { chat, FakeJev, FakeLlm } from "./fakes.js";

const quiet = { onWarning: () => {} };

test("facts fold every batch", async () => {
  const f = new FakeLlm();
  const g = new Guard({ llm: f.llm, jev: new FakeJev(), ...quiet });
  const c = await chat(g, "netflix");
  assert.equal(c.folded, 4); assert.equal(f.calls.filter((s) => s === FACTS_BATCH_PROMPT).length, 1);
  assert.deepEqual(c.facts, { goal: "I want to cancel my netflix" });
});

test("same final message, different context: not served, rewrites skipped", async () => {
  const g = new Guard({ llm: new FakeLlm().llm, jev: new FakeJev(), ...quiet });
  const d = await g.check((await chat(g, "netflix")).ask("cancel it"), (await chat(g, "gym")).ask("cancel it"));
  assert.equal(d.serve, false); assert.equal(d.reason, "whole_conversation"); assert.equal(d.rewriteScore, undefined);
});

test("same context is served and the cached rewrite is reused", async () => {
  const f = new FakeLlm();
  const g = new Guard({ llm: f.llm, jev: new FakeJev(), ...quiet });
  const cached = (await chat(g, "netflix")).ask("cancel it");
  assert.equal((await g.check(cached, (await chat(g, "netflix")).ask("cancel it"))).serve, true);
  const before = f.calls.length;
  await g.check(cached, (await chat(g, "netflix")).ask("cancel it"));
  assert.equal(f.calls.length - before, 2); // one fold for the new chat, one rewrite (cached side memoised)
});

test("timeouts and errors are misses, promptly", async () => {
  const slow = { noul: () => new Promise<number>((r) => setTimeout(() => r(0.9), 500)) };
  let g = new Guard({ llm: new FakeLlm().llm, jev: slow, timeoutMs: 100, ...quiet });
  const t = Date.now();
  let d = await g.check((await chat(g, "x")).ask("q"), (await chat(g, "x")).ask("q"));
  assert.deepEqual([d.serve, d.reason], [false, "timeout"]); assert.ok(Date.now() - t < 400);
  g = new Guard({ llm: new FakeLlm().llm, jev: { noul: async () => { throw new Error("down"); } }, ...quiet });
  d = await g.check((await chat(g, "x")).ask("q"), (await chat(g, "x")).ask("q"));
  assert.deepEqual([d.serve, d.reason], [false, "error"]);
});

test("a failed facts update is retried", async () => {
  let n = 0;
  const llm = async () => { if (++n === 1) throw new Error("timeout"); return '{"goal": "cancel netflix"}'; };
  const g = new Guard({ llm, jev: new FakeJev(), batch: 2, ...quiet });
  const c = g.conversation();
  await c.add("cancel my netflix", "which plan?"); await c.add("premium", "ok");
  assert.equal(c.folded, 0);
  await c.add("thanks", "welcome");
  assert.equal(c.folded, 2); assert.deepEqual(c.facts, { goal: "cancel netflix" });
});

test("state round-trips through JSON", async () => {
  const g = new Guard({ llm: new FakeLlm().llm, jev: new FakeJev(), ...quiet });
  const c = await chat(g, "netflix");
  assert.deepEqual(g.conversation(JSON.parse(JSON.stringify(c))).toJSON(), c.toJSON());
});

test("GuardedCache serves only matching context", async () => {
  const g = new Guard({ llm: new FakeLlm().llm, jev: new FakeJev(), ...quiet });
  const cache = new GuardedCache(new InMemoryBackend(), g);
  await cache.store((await chat(g, "netflix")).ask("cancel it"), "Cancelled your Netflix plan.");
  assert.equal((await cache.lookup((await chat(g, "netflix")).ask("Cancel it!")))?.answer, undefined); // fake Jev is exact
  assert.equal((await cache.lookup((await chat(g, "netflix")).ask("cancel it")))?.answer, "Cancelled your Netflix plan.");
  assert.equal(await cache.lookup((await chat(g, "gym")).ask("cancel it")), null);
});

test("LangChain backend round trip, ignoring entries fow-cache didn't write", async () => {
  const { InMemoryCache } = await import("@langchain/core/caches");
  const lc = new InMemoryCache();
  await lc.update("cancel it", "fow-cache", [{ text: "a plain cached answer" }]);
  const backend = new LangChainBackend(lc);
  assert.deepEqual(await backend.candidates("cancel it"), []);
  const g = new Guard({ llm: new FakeLlm().llm, jev: new FakeJev(), ...quiet });
  const cache = new GuardedCache(backend, g);
  await cache.store((await chat(g, "netflix")).ask("cancel it"), "Cancelled.");
  assert.equal((await cache.lookup((await chat(g, "netflix")).ask("cancel it")))?.answer, "Cancelled.");
});

test("reads entries packed by the Python package", () => {
  const fromPython = process.env.FOW_PY_PACKED ?? PY_PACKED;
  assert.deepEqual(unpack(fromPython), ["Cancelled your Netflix plan.",
    { messages: [{ role: "user", content: "cancel it" }], facts: { goal: "cancel netflix" }, folded: 0, rewrite: null }]);
});

const PY_PACKED = "{\"fow_cache\": 1, \"answer\": \"Cancelled your Netflix plan.\", \"entry\": {\"messages\": [{\"role\": \"user\", \"content\": \"cancel it\"}], \"facts\": {\"goal\": \"cancel netflix\"}, \"folded\": 0, \"rewrite\": null}}";
