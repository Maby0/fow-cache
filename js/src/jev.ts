/** Minimal client for TypeSafe's Jev yes/no checks, direct or through OpenRouter. Jev has no
 * official SDK; this posts its documented JSON request shape. */

const ENDPOINTS = {
  typesafe: ["https://api.typesafe.ai/v1/systemone", "jev-latest"],
  openrouter: ["https://openrouter.ai/api/alpha/decisions", "~typesafe/jev-latest"],
} as const;

export interface JevOptions {
  apiKey?: string;
  provider?: keyof typeof ENDPOINTS;
  timeoutMs?: number;
  retries?: number;
}

export interface Jev {
  noul(state: Record<string, unknown>, instructions: string): Promise<number>;
}

/** noul(state, instructions) -> probability of yes, 0 to 1. Reads TYPESAFE_API_KEY, else
 * OPENROUTER_API_KEY, unless apiKey/provider are given. */
export class JevClient implements Jev {
  private endpoint: string;
  private model: string;
  private apiKey: string;
  private timeoutMs: number;
  private retries: number;

  constructor({ apiKey, provider, timeoutMs = 30_000, retries = 4 }: JevOptions = {}) {
    const env = process.env;
    provider ??= env.TYPESAFE_API_KEY ? "typesafe" : "openrouter";
    [this.endpoint, this.model] = ENDPOINTS[provider];
    const key = apiKey ?? (provider === "typesafe" ? env.TYPESAFE_API_KEY : env.OPENROUTER_API_KEY);
    if (!key) throw new Error("Jev needs TYPESAFE_API_KEY or OPENROUTER_API_KEY");
    this.apiKey = key;
    this.timeoutMs = timeoutMs;
    this.retries = retries;
  }

  async noul(state: Record<string, unknown>, instructions: string): Promise<number> {
    const body = JSON.stringify({ model: this.model, state,
      questions: { same_answer: { type: "noul", instructions } } });
    let lastError: unknown;
    for (let attempt = 0; attempt <= this.retries; attempt++) {
      try {
        const res = await fetch(this.endpoint, {
          method: "POST", body, signal: AbortSignal.timeout(this.timeoutMs),
          headers: { Authorization: `Bearer ${this.apiKey}`, "Content-Type": "application/json" },
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as { answers: { same_answer: { noul: number } } };
        return Number(json.answers.same_answer.noul);
      } catch (e) {
        lastError = e;
        if (attempt < this.retries) await new Promise((r) => setTimeout(r, 1000 * 2 ** attempt));
      }
    }
    throw new Error(`Jev request failed: ${String(lastError)}`);
  }
}
