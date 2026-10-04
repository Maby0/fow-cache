import assert from "node:assert/strict";
import { test } from "node:test";
import { evaluate, loadConversations, loadQuestions } from "../src/index.js";

test("datasets load with balanced labels", () => {
  const qs = loadQuestions(), convs = loadConversations();
  assert.equal(qs.length, 600); assert.equal(qs.filter((q) => q.same_answer).length, 300);
  assert.equal(convs.length, 240); assert.equal(convs.filter((c) => c.same_answer).length, 120);
  assert.ok(convs.every((c) => c.a.at(-1)!.role === "user" && c.b.at(-1)!.role === "user"));
});

test("always serving gets every trap wrong", async () => {
  const rep = await evaluate(() => true);
  assert.equal(rep.hitRate, 1); assert.equal(rep.wrongRate, 1); assert.equal(rep.passes(0.05), false);
});

test("scores, thresholds and best threshold", async () => {
  const labels = new Map(loadQuestions().map((q) => [q.a + q.b, q.same_answer]));
  const rep = await evaluate((a, b) => (labels.get(a + b) ? 0.9 : 0.4), { ambiguous: "skip" });
  assert.deepEqual([rep.hitRate, rep.wrongRate], [1, 0]);
  assert.equal(rep.atThreshold(0.3).wrongRate, 1);
  assert.deepEqual(rep.bestThreshold(0), { threshold: 0.9, hitRate: 1 });
});

test("ambiguous setting", async () => {
  const strict = await evaluate(() => true), lenient = await evaluate(() => true, { ambiguous: "same" });
  const skipped = await evaluate(() => true, { ambiguous: "skip" });
  const n = loadQuestions().filter((q) => q.ambiguous).length;
  const hits = (r: typeof strict) => r.results.filter((x) => x.sameAnswer).length;
  assert.ok(n >= 4 && "complementary" in strict.byGroup() && "context_dependent" in strict.byGroup());
  assert.equal(hits(lenient), hits(strict) + n);
  assert.equal(skipped.results.length, 600 - n);
});

test("last-message check fails conversation traps; async checks and concurrency", async () => {
  const rep = await evaluate(async (a, b) => a.at(-1)!.content.toLowerCase().replace(/[?!. ]+$/, "") ===
    b.at(-1)!.content.toLowerCase().replace(/[?!. ]+$/, ""), { dataset: "conversations", concurrency: 16 });
  assert.ok(rep.wrongRate > 0.9);
});
