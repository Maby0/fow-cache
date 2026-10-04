/**
 * Does a guarded semantic cache save money? A cache hit saves one main-model turn; the guard
 * costs Haiku calls (facts, rewrites) and two Jev checks. breakEven() is the share of turns that
 * must be hits for the guard to cost less than it saves. Tables come from the Python package.
 */
import { GUARD_MODEL, GUARDS, JEV_INPUT, PRICES, TOKENS } from "./shared.js";

export type Model = keyof typeof PRICES;
export type GuardName = keyof typeof GUARDS;

export interface Scenario {
  model: Model;
  promptTokens: number; // system prompt + tools + history sent each turn
  newTokens: number;
  outputTokens: number;
  promptCaching: boolean;
  candidateRate: number; // share of turns where the embedding lookup finds a candidate
  size: keyof typeof TOKENS;
}

export const defaultScenario: Scenario = { model: "sonnet-5.5", promptTokens: 8000, newTokens: 500,
  outputTokens: 300, promptCaching: true, candidateRate: 0.2, size: "typical" };

/** $ for one main-model turn, i.e. what a cache hit saves. */
export function turnCost(s: Scenario): number {
  const [pin, pout, pread] = PRICES[s.model];
  return (s.promptTokens * (s.promptCaching ? pread : pin) + s.newTokens * pin + s.outputTokens * pout) / 1e6;
}

/** Expected guard $ per turn: always-on work, plus on candidates both sides' rewrites and two Jev checks. */
export function guardCost(s: Scenario, guard: GuardName = "batched facts (default)"): number {
  const [always, rewrite] = GUARDS[guard] as readonly [string | null, string];
  const tokens = TOKENS[s.size] as Record<string, readonly [number, number]>;
  const [hin, hout] = PRICES[GUARD_MODEL];
  let cost = 0;
  if (always) cost += (tokens[always][0] * hin + tokens[always][1] * hout) / 1e6;
  const [i, o] = tokens[rewrite];
  return cost + s.candidateRate * (2 * (i * hin + o * hout) / 1e6 + tokens.jev[0] * JEV_INPUT / 1e6);
}

/** Hit rate at which the guard pays for itself. Above s.candidateRate it never can. */
export function breakEven(s: Scenario, guard: GuardName = "batched facts (default)"): number {
  return guardCost(s, guard) / turnCost(s);
}

export function report(s: Scenario): string {
  const lines = [`Main model ${s.model}, ${s.promptTokens.toLocaleString("en-GB")} prompt tokens ` +
    `(${s.promptCaching ? "prompt-cached" : "no prompt caching"}), ${s.newTokens} new, ${s.outputTokens} out: ` +
    `a hit saves $${turnCost(s).toFixed(4)}. Candidates on ${Math.round(s.candidateRate * 100)}% of turns, ` +
    `${s.size.replace("_", " ")} conversations.`, ""];
  for (const g of Object.keys(GUARDS) as GuardName[]) {
    const be = breakEven(s, g);
    const note = be <= s.candidateRate ? "" : "  (never pays: above the candidate rate)";
    lines.push(`  ${g.padEnd(36)} $${guardCost(s, g).toFixed(5)}/turn   break-even hit rate ${Math.round(be * 100)}%${note}`);
  }
  return lines.join("\n");
}
