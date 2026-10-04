#!/usr/bin/env node
/**
 * fow-cache command line.
 *
 *   npx fow-cache eval --check ./my-cache-check.js --max-wrong 0.05
 *   npx fow-cache eval --check ./checks.mjs#wouldHit --dataset conversations --json
 *   npx fow-cache costs --model haiku-4.5 --candidate-rate 0.1
 */
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { parseArgs } from "node:util";
import { evaluate, type Ambiguous } from "./evaluate.js";
import { defaultScenario, report, type Model } from "./costs.js";

const HELP = `usage: fow-cache eval --check <file.js[#export]> [--dataset questions|conversations] [--threshold 0.5]
                      [--max-wrong 0.05] [--ambiguous different|same|skip] [--concurrency 1] [--json]
       fow-cache costs [--model sonnet-5.5|haiku-4.5|opus-5.5] [--prompt-tokens 8000] [--new-tokens 500]
                       [--output-tokens 300] [--no-prompt-caching] [--candidate-rate 0.2] [--long]

The --check module exports a function (cached, next) => boolean | score (default export, or #name).`;

async function evalCommand(argv: string[]) {
  const { values } = parseArgs({ args: argv, options: {
    check: { type: "string" }, dataset: { type: "string", default: "questions" },
    threshold: { type: "string", default: "0.5" }, "max-wrong": { type: "string" },
    ambiguous: { type: "string", default: "different" }, concurrency: { type: "string", default: "1" },
    json: { type: "boolean", default: false },
  } });
  if (!values.check) throw new Error("eval needs --check <file.js[#export]>");
  const [file, name = "default"] = values.check.split("#");
  const mod = await import(pathToFileURL(resolve(file)).href);
  const check = mod[name];
  if (typeof check !== "function") throw new Error(`${file} has no function export "${name}"`);
  const rep = await evaluate(check, { dataset: values.dataset as "questions", threshold: Number(values.threshold),
    ambiguous: values.ambiguous as Ambiguous, concurrency: Number(values.concurrency) });
  console.log(values.json ? JSON.stringify(rep, null, 2) : rep.toString());
  const maxWrong = values["max-wrong"];
  if (maxWrong !== undefined && !rep.passes(Number(maxWrong))) {
    console.error(`\nFAIL: ${(rep.wrongRate * 100).toFixed(1)}% of traps got a wrong answer (max ${(Number(maxWrong) * 100).toFixed(1)}%)`);
    process.exitCode = 1;
  }
}

function costsCommand(argv: string[]) {
  const { values } = parseArgs({ args: argv, options: {
    model: { type: "string", default: defaultScenario.model }, "prompt-tokens": { type: "string" },
    "new-tokens": { type: "string" }, "output-tokens": { type: "string" },
    "no-prompt-caching": { type: "boolean", default: false }, "candidate-rate": { type: "string" },
    long: { type: "boolean", default: false },
  } });
  const num = (v: string | undefined, d: number) => (v === undefined ? d : Number(v));
  console.log(report({
    model: values.model as Model,
    promptTokens: num(values["prompt-tokens"], defaultScenario.promptTokens),
    newTokens: num(values["new-tokens"], defaultScenario.newTokens),
    outputTokens: num(values["output-tokens"], defaultScenario.outputTokens),
    promptCaching: !values["no-prompt-caching"],
    candidateRate: num(values["candidate-rate"], defaultScenario.candidateRate),
    size: values.long ? "very_long" : "typical",
  }));
}

const [command, ...rest] = process.argv.slice(2);
try {
  if (command === "eval") await evalCommand(rest);
  else if (command === "costs") costsCommand(rest);
  else { console.log(HELP); if (command && command !== "--help" && command !== "-h") process.exitCode = 2; }
} catch (e) {
  console.error(`fow-cache: ${(e as Error).message}\n\n${HELP}`);
  process.exitCode = 2;
}
