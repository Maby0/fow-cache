/** Test a real cache with evaluate(), instead of an approximation of it. Each pair runs against
 * an empty cache: store the cached side, look up the new side. */
import type { Message } from "./data.js";

type Side = string | Message[];
const text = (x: Side) => (Array.isArray(x) ? x[x.length - 1].content : x);

/** Generic adapter for any cache: store(text), lookup(text) -> score or boolean, reset() empties it. */
export function storeLookupCheck(store: (text: string) => unknown, lookup: (text: string) => boolean | number | Promise<boolean | number>,
  reset: () => unknown) {
  return async (a: Side, b: Side) => {
    await reset();
    await store(text(a));
    return lookup(text(b));
  };
}

/** LangChain.js cache hit (true/false) at the cache's own threshold. LangChain.js caches have no
 * clear(), so each pair gets its own llmKey (namespace-N) instead: use a dedicated cache, and note
 * that a semantic cache which ignores llmKey would see earlier pairs. */
export function langchainCheck(cache: { lookup(p: string, k: string): Promise<unknown[] | null>;
  update(p: string, k: string, v: Array<{ text: string }>): Promise<void> }, namespace = "fow-cache-eval") {
  let n = 0;
  return async (a: Side, b: Side) => {
    const key = `${namespace}-${n++}`;
    await cache.update(text(a), key, [{ text: "cached" }]);
    return (await cache.lookup(text(b), key)) != null;
  };
}
