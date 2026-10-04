/**
 * GuardedCache: your existing semantic cache finds candidates, the guard decides.
 *
 *   const cache = new GuardedCache(new LangChainBackend(myLangChainCache), guard);
 *   const hit = await cache.lookup(entry);
 *   const reply = hit ? hit.answer : await callYourModel(...);
 *   if (!hit) await cache.store(entry, reply);
 *
 * Packed values use the same JSON as the Python package, so a cache written by one can be
 * read by the other.
 */
import type { Decision, Entry, Guard } from "./guard.js";

export interface Hit {
  answer: string;
  decision: Decision;
  cached: Entry;
}

export interface Backend {
  /** Up to k [answer, entry] candidates for this final user message, best first. */
  candidates(text: string, k: number): Promise<Array<[string, Entry]>>;
  store(text: string, answer: string, entry: Entry): Promise<void>;
}

export function pack(answer: string, entry: Entry): string {
  return JSON.stringify({ fow_cache: 1, answer, entry });
}

/** [answer, entry] from a packed value, or null for values fow-cache didn't write. */
export function unpack(value: unknown): [string, Entry] | null {
  try {
    const d = JSON.parse(String(value));
    return d && d.fow_cache === 1 ? [d.answer, d.entry] : null;
  } catch {
    return null;
  }
}

const norm = (s: string) => s.toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, "").split(/\s+/).filter(Boolean).join(" ");

/** Candidates by a similarity function over final messages; for tests and small apps.
 * Default: case- and punctuation-insensitive exact match. */
export class InMemoryBackend implements Backend {
  private items: Array<[string, string, Entry]> = [];

  constructor(private similarity: (a: string, b: string) => number = (a, b) => (norm(a) === norm(b) ? 1 : 0),
    private threshold = 0.5) {}

  async candidates(text: string, k: number): Promise<Array<[string, Entry]>> {
    return this.items.map(([t, answer, entry]) => [this.similarity(t, text), answer, entry] as const)
      .filter(([score]) => score >= this.threshold).sort((x, y) => y[0] - x[0]).slice(0, k)
      .map(([, answer, entry]) => [answer, entry]);
  }

  async store(text: string, answer: string, entry: Entry): Promise<void> {
    this.items.push([text, answer, entry]);
  }
}

/** Wraps any LangChain.js cache (BaseCache from @langchain/core), e.g. a semantic cache from a
 * vector-store integration. The answer and entry are packed as JSON in the stored generation's
 * text, so use a cache (or namespace) dedicated to the guard. One candidate per lookup. */
export class LangChainBackend implements Backend {
  constructor(private cache: { lookup(prompt: string, llmKey: string): Promise<Array<{ text: string }> | null>;
    update(prompt: string, llmKey: string, value: Array<{ text: string }>): Promise<void> },
    private namespace = "fow-cache") {}

  async candidates(text: string): Promise<Array<[string, Entry]>> {
    const generations = (await this.cache.lookup(text, this.namespace)) ?? [];
    const found = generations.length ? unpack(generations[0].text) : null;
    return found ? [found] : [];
  }

  async store(text: string, answer: string, entry: Entry): Promise<void> {
    await this.cache.update(text, this.namespace, [{ text: pack(answer, entry) }]);
  }
}

export class GuardedCache {
  /** k: candidates checked per lookup, best first; the first that passes is served. */
  constructor(readonly backend: Backend, readonly guard: Guard, readonly k = 3) {}

  async lookup(entry: Entry): Promise<Hit | null> {
    const last = entry.messages[entry.messages.length - 1].content;
    for (const [answer, cached] of await this.backend.candidates(last, this.k)) {
      const decision = await this.guard.check(cached, entry);
      if (decision.serve) return { answer, decision, cached };
    }
    return null;
  }

  async store(entry: Entry, answer: string): Promise<void> {
    await this.backend.store(entry.messages[entry.messages.length - 1].content, answer, entry);
  }
}
