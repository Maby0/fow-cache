/**
 * A guard for semantic caches in multi-turn chats (a port of fow_cache.guard).
 *
 * 1. After every BATCH exchanges, an LLM (Claude Haiku 4.5 by default) folds them into a short
 *    JSON record of facts. Do this off the request path, after the reply is sent.
 * 2. When the cache finds a candidate, both sides' final messages are rewritten into standalone
 *    requests from their facts plus the messages since the last fold.
 * 3. Two Jev checks run: whole conversations, and the two rewrites. Serve only if both pass.
 *
 * check() never throws: errors and timeouts come back as a miss, so your app answers normally.
 * Entries and conversation state serialise to the same JSON as the Python package.
 */
import type { Message } from "./data.js";
import { JevClient, type Jev } from "./jev.js";
import {
  BATCH, CONV_INSTRUCTIONS, FACTS_BATCH_PROMPT, QUESTION_INSTRUCTIONS, RECENT, REWRITE_LITE_PROMPT,
  REWRITE_THRESHOLD, TIMEOUT_MS, WHOLE_THRESHOLD,
} from "./shared.js";

/** llm(system, user) -> text. */
export type Llm = (system: string, user: string) => Promise<string>;

/** An Llm backed by the Anthropic SDK (npm install @anthropic-ai/sdk). */
export function anthropicLlm({ model = "claude-haiku-4-5", maxTokens = 1024, timeoutMs = 10_000, client }:
  { model?: string; maxTokens?: number; timeoutMs?: number; client?: any } = {}): Llm {
  let ready: Promise<any> | undefined;
  const getClient = () => (ready ??= client ? Promise.resolve(client)
    : import("@anthropic-ai/sdk").then(({ default: Anthropic }) => new Anthropic({ timeout: timeoutMs, maxRetries: 1 })));
  return async (system, user) => {
    const c = await getClient();
    const response = await c.messages.create({ model, max_tokens: maxTokens, system,
      messages: [{ role: "user", content: user }] });
    return response.content.filter((b: { type: string }) => b.type === "text")
      .map((b: { text: string }) => b.text).join("").trim();
  };
}

export function transcript(messages: Message[]): string {
  return messages.map((m) => `${m.role[0].toUpperCase()}${m.role.slice(1)}: ${m.content}`).join("\n");
}

function parseRecord(text: string): Record<string, unknown> | null {
  try {
    const record = JSON.parse(text.slice(text.indexOf("{"), text.lastIndexOf("}") + 1));
    return record && typeof record === "object" && !Array.isArray(record) ? record : null;
  } catch {
    return null;
  }
}

/** A conversation at the moment a user message arrives: what gets looked up, and what gets
 * stored alongside a cached answer. JSON keys match the Python package's Entry.to_dict(). */
export interface Entry {
  messages: Message[];
  facts: Record<string, unknown>;
  folded: number;
  rewrite: string | null;
}

export interface ConversationState {
  messages: Message[];
  facts: Record<string, unknown>;
  folded: number;
}

export interface FoldResult {
  facts: Record<string, unknown>;
  folded: number;
}

/** Apply a background fold() result to the latest saved state. Messages always come from
 * `state`, so exchanges recorded while the fold ran are kept; facts come from whichever has
 * folded further, so a slow fold never overwrites a newer one. */
export function mergeFold(state: ConversationState, update: FoldResult): ConversationState {
  if (update.folded <= (state.folded ?? 0)) return state;
  return { ...state, facts: update.facts, folded: update.folded };
}

export class Conversation {
  messages: Message[];
  facts: Record<string, unknown>;
  folded: number;

  constructor(private guard: Guard, state?: Partial<ConversationState>) {
    this.messages = [...(state?.messages ?? [])];
    this.facts = { ...(state?.facts ?? {}) };
    this.folded = state?.folded ?? 0;
  }

  toJSON(): ConversationState {
    return { messages: this.messages, facts: this.facts, folded: this.folded };
  }

  /** Record one exchange. No model call, so it's safe on the request path. */
  record(user: string, assistant: string): void {
    this.messages.push({ role: "user", content: user }, { role: "assistant", content: assistant });
  }

  /** True when BATCH or more exchanges are waiting to be folded into the facts. */
  get foldDue(): boolean {
    return this.messages.length / 2 - this.folded >= this.guard.batch;
  }

  /** Fold waiting exchanges into the facts: one LLM call per BATCH exchanges. Run it off the
   * request path, e.g. after the reply has gone out. If a call fails, the exchanges stay
   * unfolded and are retried on the next fold(). Never throws. Resolves to the fold result,
   * for mergeFold() when saving from a background job. */
  async fold(): Promise<FoldResult> {
    const batch = this.guard.batch;
    while (this.foldDue) {
      const block = this.messages.slice(2 * this.folded, 2 * (this.folded + batch));
      let text: string;
      try {
        text = await this.guard.llm(FACTS_BATCH_PROMPT,
          `Current record:\n${JSON.stringify(this.facts)}\n\nLatest exchanges:\n${transcript(block)}`);
      } catch (e) {
        this.guard.log("facts update failed; will retry on the next fold", e);
        break;
      }
      const record = parseRecord(text);
      if (record) this.facts = record;
      else this.guard.log("facts update returned no JSON object; keeping the previous record");
      this.folded += batch;
    }
    return { facts: this.facts, folded: this.folded };
  }

  /** record() then fold(), in one call. Every BATCH exchanges this waits on an LLM call, so
   * call it after the reply has gone out, or use record() and fold() separately. */
  async add(user: string, assistant: string): Promise<void> {
    this.record(user, assistant);
    await this.fold();
  }

  ask(user: string): Entry {
    return { messages: [...this.messages, { role: "user", content: user }], facts: { ...this.facts },
      folded: this.folded, rewrite: null };
  }
}

export interface Decision {
  serve: boolean;
  reason: "pass" | "whole_conversation" | "rewrite" | "timeout" | "error";
  wholeScore?: number;
  rewriteScore?: number;
  rewrites?: [string, string];
  ms: number;
}

/** The yes/no model: a function (state, instructions) => probability of yes (0 to 1), or an
 * object with that as a noul() method, like JevClient (the default). The thresholds were tuned
 * on Jev's probabilities: a decider that answers only 1 or 0 works with them as they are; one
 * with its own probabilities needs its own. */
export type Decider = Jev | ((state: Record<string, unknown>, instructions: string) => Promise<number>);

export interface GuardOptions {
  llm?: Llm;
  decider?: Decider;
  /** @deprecated The older name for decider. */
  jev?: Decider;
  batch?: number;
  wholeThreshold?: number;
  rewriteThreshold?: number;
  timeoutMs?: number;
  /** Called with warnings (failed facts updates, timeouts, errors). Default: console.warn. */
  onWarning?: (message: string, error?: unknown) => void;
}

class Timeout extends Error {}

function deadline<T>(p: Promise<T>, msLeft: number): Promise<T> {
  let timer: ReturnType<typeof setTimeout>;
  return Promise.race([
    p, new Promise<never>((_, reject) => { timer = setTimeout(() => reject(new Timeout()), Math.max(0, msLeft)); }),
  ]).finally(() => clearTimeout(timer));
}

export class Guard {
  readonly llm: Llm;
  readonly decider: Decider;
  readonly batch: number;
  readonly wholeThreshold: number;
  readonly rewriteThreshold: number;
  readonly timeoutMs: number;
  private onWarning: (message: string, error?: unknown) => void;

  private decide: (state: Record<string, unknown>, instructions: string) => Promise<number>;

  constructor({ llm, decider, jev, batch = BATCH, wholeThreshold = WHOLE_THRESHOLD, rewriteThreshold = REWRITE_THRESHOLD,
    timeoutMs = TIMEOUT_MS, onWarning }: GuardOptions = {}) {
    this.llm = llm ?? anthropicLlm();
    if (decider && jev) throw new TypeError("pass decider or jev, not both");
    const d = decider ?? jev ?? new JevClient({ timeoutMs, retries: 1 });
    this.decider = d;
    this.decide = typeof d === "function" ? d : (state, instructions) => d.noul(state, instructions);
    this.batch = batch;
    this.wholeThreshold = wholeThreshold;
    this.rewriteThreshold = rewriteThreshold;
    this.timeoutMs = timeoutMs;
    this.onWarning = onWarning ?? ((m, e) => console.warn(`fow-cache: ${m}`, e ?? ""));
  }

  /** @deprecated The older name for decider. */
  get jev(): Decider {
    return this.decider;
  }

  log(message: string, error?: unknown) {
    this.onWarning(message, error);
  }

  conversation(state?: Partial<ConversationState>): Conversation {
    return new Conversation(this, state);
  }

  async rewrite(entry: Entry): Promise<string> {
    if (entry.rewrite == null) {
      const start = Math.max(0, Math.min(2 * entry.folded, entry.messages.length - RECENT));
      entry.rewrite = await this.llm(REWRITE_LITE_PROMPT,
        `Earlier conversation summary: ${JSON.stringify(entry.facts)}\n\nRecent messages:\n${transcript(entry.messages.slice(start))}`);
    }
    return entry.rewrite;
  }

  /** Should `next` be answered with the answer stored for `cached`? Never throws. */
  async check(cached: Entry, next: Entry): Promise<Decision> {
    const t0 = Date.now();
    const left = () => this.timeoutMs - (Date.now() - t0);
    const whole = this.decide({ cached_conversation: transcript(cached.messages),
      new_conversation: transcript(next.messages) }, CONV_INSTRUCTIONS);
    const rewrites = Promise.all([this.rewrite(cached), this.rewrite(next)]);
    whole.catch(() => {}); rewrites.catch(() => {}); // settled later or abandoned: never unhandled
    try {
      const w = await deadline(whole, left());
      if (w < this.wholeThreshold) return { serve: false, reason: "whole_conversation", wholeScore: w, ms: Date.now() - t0 };
      const rw2 = await deadline(rewrites, left());
      const rw = await deadline(this.decide({ cached_question: rw2[0], new_question: rw2[1] }, QUESTION_INSTRUCTIONS), left());
      const serve = rw >= this.rewriteThreshold;
      return { serve, reason: serve ? "pass" : "rewrite", wholeScore: w, rewriteScore: rw, rewrites: rw2, ms: Date.now() - t0 };
    } catch (e) {
      const timeout = e instanceof Timeout;
      this.log(timeout ? `check exceeded ${this.timeoutMs}ms; treating as a miss` : "check failed; treating as a miss",
        timeout ? undefined : e);
      return { serve: false, reason: timeout ? "timeout" : "error", ms: Date.now() - t0 };
    }
  }

  /** Build an Entry from a full message list ending in a user message (for evaluation). */
  async replay(messages: Message[]): Promise<Entry> {
    const chat = this.conversation();
    for (let i = 0; i + 1 < messages.length; i += 2) await chat.add(messages[i].content, messages[i + 1].content);
    return chat.ask(messages[messages.length - 1].content);
  }
}
