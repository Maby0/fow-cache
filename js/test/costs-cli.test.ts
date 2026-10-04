import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { writeFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { costs, langchainCheck, storeLookupCheck } from "../src/index.js";

const cli = join(process.cwd(), "dist", "cli.js");

test("batched guard is cheaper; prompt caching raises break-even", () => {
  const s = costs.defaultScenario;
  assert.ok(costs.guardCost(s) < costs.guardCost(s, "facts every turn"));
  assert.ok(costs.breakEven({ ...s, promptCaching: true }) > costs.breakEven({ ...s, promptCaching: false }));
});

test("cli costs and eval --max-wrong", () => {
  assert.match(execFileSync("node", [cli, "costs", "--model", "haiku-4.5"]).toString(), /break-even hit rate/);
  const dir = mkdtempSync(join(tmpdir(), "fow-"));
  writeFileSync(join(dir, "check.mjs"), "export default () => true;\nexport const never = () => false;\n");
  const fail = spawnSync("node", [cli, "eval", "--check", join(dir, "check.mjs"), "--max-wrong", "0.05"]);
  assert.equal(fail.status, 1); assert.match(fail.stderr.toString(), /FAIL/);
  const pass = spawnSync("node", [cli, "eval", "--check", `${join(dir, "check.mjs")}#never`, "--max-wrong", "0.05", "--json"]);
  assert.equal(pass.status, 0); assert.equal(JSON.parse(pass.stdout.toString()).wrong_rate, 0);
});

test("adapters reset between pairs", async () => {
  const store: string[] = [];
  const check = storeLookupCheck((t) => store.push(t), (t) => store.includes(t), () => { store.length = 0; });
  assert.equal(await check("a", "a"), true); assert.equal(await check("b", "a"), false);
  const { InMemoryCache } = await import("@langchain/core/caches");
  const lc = langchainCheck(new InMemoryCache());
  assert.equal(await lc("Track order 48213", "Track order 48213"), true);
  assert.equal(await lc("Track order 48213", "Track order 48231"), false);
});
