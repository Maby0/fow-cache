import { FACTS_BATCH_PROMPT } from "../src/shared.js";
import type { Guard } from "../src/guard.js";

/** Facts record the first user message of a block; rewrites echo the summary plus final message. */
export class FakeLlm {
  calls: string[] = [];
  llm = async (system: string, user: string): Promise<string> => {
    this.calls.push(system);
    if (system === FACTS_BATCH_PROMPT) {
      const first = user.split("Latest exchanges:\nUser: ")[1].split("\n")[0];
      return JSON.stringify({ goal: first });
    }
    const summary = user.split("Earlier conversation summary: ")[1].split("\n")[0];
    return `${summary} | ${user.trimEnd().split("User: ").at(-1)}`;
  };
}

/** Yes when the two texts are identical (whole conversations: compare first lines). */
export class FakeJev {
  async noul(state: Record<string, unknown>): Promise<number> {
    let [a, b] = Object.values(state) as string[];
    if (a.includes("\n")) [a, b] = [a.split("\n")[0], b.split("\n")[0]];
    return a === b ? 0.9 : 0.1;
  }
}

export async function chat(guard: Guard, topic: string, n = 5) {
  const c = guard.conversation();
  await c.add(`I want to cancel my ${topic}`, "Sure, which plan?");
  for (let i = 0; i < n - 1; i++) await c.add(`side question ${i}`, `answer ${i}`);
  return c;
}
