/**
 * Load the bundled benchmark data (the same files the Python package ships).
 *
 * questions:      single question pairs: near_repeat and paraphrase (should hit),
 *                 negation, entity_swap, number_date and scope (traps)
 * conversations:  pairs of multi-turn chats whose final user messages match: same_context_reworded,
 *                 irrelevant_history, same_context_extra_chatter (should hit), context_swap,
 *                 detail_swap and intent_flip (traps)
 */
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

export type Message = { role: "user" | "assistant"; content: string };

export interface QuestionPair {
  id: string;
  category: string;
  a: string; // cached question
  b: string; // new question
  same_answer: boolean;
  style?: string;
  ambiguous?: "complementary" | "context_dependent";
}

export interface ConversationPair {
  id: string;
  subtype: string;
  a: Message[]; // cached conversation, ends with a user message
  b: Message[];
  same_answer: boolean;
  note?: string;
  ambiguous?: "complementary" | "context_dependent";
}

// dist/data.js -> ../data in the published package; build-test/src/data.js -> ../../data in tests.
const here = dirname(fileURLToPath(import.meta.url));
const dataDir = [join(here, "..", "data"), join(here, "..", "..", "data")].find((d) => existsSync(join(d, "pairs.jsonl")))
  ?? join(here, "..", "data");

function readJsonl<T>(path: string): T[] {
  return readFileSync(path, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l) as T);
}

function readDir<T>(dir: string): T[] {
  return readdirSync(join(dataDir, dir)).filter((f) => f.endsWith(".jsonl")).sort()
    .flatMap((f) => readJsonl<T>(join(dataDir, dir, f)));
}

export function loadQuestions(): QuestionPair[] {
  return readJsonl<QuestionPair>(join(dataDir, "pairs.jsonl"));
}

export function loadConversations(): ConversationPair[] {
  return [...readDir<ConversationPair>("conv-parts"), ...readDir<ConversationPair>("conv-long")];
}

export function lengthBucket(item: { a: unknown[]; b: unknown[] }): string {
  const n = Math.max(item.a.length, item.b.length);
  return n <= 4 ? "short" : n <= 8 ? "medium" : n <= 20 ? "long" : "very_long";
}
