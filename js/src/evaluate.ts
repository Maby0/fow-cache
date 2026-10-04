/**
 * Run a cache-hit decision against the benchmark and report how often it serves a cached
 * answer it should (hits) and one it shouldn't (wrong answers).
 */
import { lengthBucket, loadConversations, loadQuestions, type Message } from "./data.js";

export interface Result {
  id: string;
  group: string; // category (questions), subtype (conversations), or the ambiguous reason
  length: string; // conversations only
  sameAnswer: boolean;
  score: number;
  served: boolean;
}

export type Ambiguous = "different" | "same" | "skip";
type Score = boolean | number;
export type QuestionCheck = (cached: string, next: string) => Score | Promise<Score>;
export type ConversationCheck = (cached: Message[], next: Message[]) => Score | Promise<Score>;

export class Report {
  constructor(readonly dataset: string, readonly threshold: number, readonly results: Result[]) {}

  private rate(pred: (r: Result) => boolean): number {
    const sel = this.results.filter(pred);
    return sel.length ? sel.filter((r) => r.served).length / sel.length : NaN;
  }

  /** Share of should-hit items served from cache. */
  get hitRate(): number {
    return this.rate((r) => r.sameAnswer);
  }

  /** Share of traps given a wrong cached answer. */
  get wrongRate(): number {
    return this.rate((r) => !r.sameAnswer);
  }

  /** {group: served rate}: the hit rate for hit groups, the wrong-answer rate for traps. */
  byGroup(): Record<string, number> {
    const groups = [...new Set(this.results.map((r) => r.group))];
    return Object.fromEntries(groups.map((g) => [g, this.rate((r) => r.group === g)]));
  }

  passes(maxWrong: number): boolean {
    return this.wrongRate <= maxWrong;
  }

  /** The same scores re-judged at another threshold, without re-running the check. */
  atThreshold(threshold: number): Report {
    return new Report(this.dataset, threshold, this.results.map((r) => ({ ...r, served: r.score >= threshold })));
  }

  /** The threshold with the most hits while wrong answers stay <= maxWrong. Picked on this
   * data, so optimistic: confirm on held-out traffic. */
  bestThreshold(maxWrong: number): { threshold: number | null; hitRate: number } {
    let best = { threshold: null as number | null, hitRate: 0 };
    for (const t of [...new Set(this.results.map((r) => r.score))].sort((x, y) => x - y)) {
      const rep = this.atThreshold(t);
      if (rep.wrongRate <= maxWrong && rep.hitRate > best.hitRate) best = { threshold: t, hitRate: rep.hitRate };
    }
    return best;
  }

  toJSON() {
    return { dataset: this.dataset, threshold: this.threshold, n: this.results.length,
      hit_rate: this.hitRate, wrong_rate: this.wrongRate, by_group: this.byGroup() };
  }

  toString(): string {
    const groups = this.byGroup();
    const hits = Object.keys(groups).filter((g) => this.results.some((r) => r.group === g && r.sameAnswer));
    const traps = Object.keys(groups).filter((g) => !hits.includes(g));
    const pct = (x: number) => `${(x * 100).toFixed(1)}%`.padStart(6);
    return [
      `fow-cache: ${this.dataset}, ${this.results.length} pairs, threshold ${this.threshold}`, "",
      `  should-hit served         ${pct(this.hitRate)}`,
      ...hits.map((g) => `    ${g.padEnd(23)}${pct(groups[g])}`),
      `  traps given wrong answer  ${pct(this.wrongRate)}`,
      ...traps.map((g) => `    ${g.padEnd(23)}${pct(groups[g])}`),
    ].join("\n");
  }
}

export interface EvaluateOptions {
  threshold?: number;
  /** How to score pairs whose answer equivalence depends on the application: "different"
   * (default, strict) counts them as traps, "same" as hits, "skip" leaves them out. */
  ambiguous?: Ambiguous;
  /** Checks run in parallel batches of this size (useful for API-backed checks). */
  concurrency?: number;
}

export function evaluate(check: QuestionCheck, opts?: EvaluateOptions & { dataset?: "questions" }): Promise<Report>;
export function evaluate(check: ConversationCheck, opts: EvaluateOptions & { dataset: "conversations" }): Promise<Report>;
export async function evaluate(check: QuestionCheck | ConversationCheck,
  { dataset = "questions", threshold = 0.5, ambiguous = "different", concurrency = 1 }:
    EvaluateOptions & { dataset?: "questions" | "conversations" } = {}): Promise<Report> {
  if (!["different", "same", "skip"].includes(ambiguous)) throw new Error(`ambiguous must be different, same or skip`);
  let items: Array<{ id: string; a: any; b: any; same_answer: boolean; ambiguous?: string; category?: string; subtype?: string }> =
    dataset === "conversations" ? loadConversations() : loadQuestions();
  if (ambiguous === "skip") items = items.filter((i) => !i.ambiguous);
  const scores: number[] = new Array(items.length);
  for (let i = 0; i < items.length; i += concurrency) {
    await Promise.all(items.slice(i, i + concurrency).map(async (item, j) => {
      const s = await (check as (a: unknown, b: unknown) => Score | Promise<Score>)(item.a, item.b);
      scores[i + j] = typeof s === "boolean" ? (s ? 1 : 0) : Number(s);
    }));
  }
  const results = items.map((item, i): Result => ({
    id: item.id,
    group: item.ambiguous ?? item.category ?? item.subtype ?? "",
    length: dataset === "conversations" ? lengthBucket(item) : "",
    sameAnswer: item.ambiguous ? ambiguous === "same" : item.same_answer,
    score: scores[i],
    served: scores[i] >= threshold,
  }));
  return new Report(dataset, threshold, results);
}
