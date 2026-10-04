"""Run a cache-hit decision against the benchmark and report how often it serves a
cached answer it should (hits) and one it shouldn't (wrong answers)."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from .data import length_bucket, load_conversations, load_questions


@dataclass
class Result:
    id: str
    group: str  # category (questions) or subtype (conversations)
    length: str  # conversations only, else ""
    same_answer: bool
    score: float
    served: bool


@dataclass
class Report:
    dataset: str
    threshold: float
    results: list = field(default_factory=list)

    def _rate(self, pred):
        sel = [r for r in self.results if pred(r)]
        return sum(r.served for r in sel) / len(sel) if sel else float("nan")

    @property
    def hit_rate(self):
        """Share of should-hit items served from cache."""
        return self._rate(lambda r: r.same_answer)

    @property
    def wrong_rate(self):
        """Share of traps given a wrong cached answer."""
        return self._rate(lambda r: not r.same_answer)

    def by_group(self):
        """{group: served rate}: for hit groups that's the hit rate, for traps the wrong-answer rate."""
        return {g: self._rate(lambda r, g=g: r.group == g) for g in dict.fromkeys(r.group for r in self.results)}

    def passes(self, max_wrong):
        return self.wrong_rate <= max_wrong

    def at_threshold(self, threshold):
        """The same scores re-judged at another threshold, without re-running the check."""
        return Report(self.dataset, threshold, [Result(r.id, r.group, r.length, r.same_answer, r.score, r.score >= threshold)
                                                for r in self.results])

    def best_threshold(self, max_wrong):
        """(threshold, hit rate) with the most hits while wrong answers stay <= max_wrong,
        or (None, 0.0). Picked on this data, so optimistic: confirm on held-out traffic."""
        best = (None, 0.0)
        for t in sorted({r.score for r in self.results}):
            rep = self.at_threshold(t)
            if rep.wrong_rate <= max_wrong and rep.hit_rate > best[1]:
                best = (t, rep.hit_rate)
        return best

    def to_dict(self):
        return {"dataset": self.dataset, "threshold": self.threshold, "n": len(self.results),
                "hit_rate": self.hit_rate, "wrong_rate": self.wrong_rate, "by_group": self.by_group()}

    def __str__(self):
        hits = [g for g in self.by_group() if any(r.group == g and r.same_answer for r in self.results)]
        traps = [g for g in self.by_group() if g not in hits]
        groups = self.by_group()
        lines = [f"fow-cache: {self.dataset}, {len(self.results)} pairs, threshold {self.threshold}", "",
                 f"  should-hit served         {self.hit_rate:6.1%}"]
        lines += [f"    {g:<23}{groups[g]:6.1%}" for g in hits]
        lines += [f"  traps given wrong answer  {self.wrong_rate:6.1%}"]
        lines += [f"    {g:<23}{groups[g]:6.1%}" for g in traps]
        return "\n".join(lines)


AMBIGUOUS = ("different", "same", "skip")


def evaluate(check, dataset="questions", threshold=0.5, workers=1, ambiguous="different"):
    """Score `check` on a bundled dataset.

    check: for "questions", check(cached_question, new_question); for "conversations",
    check(cached_messages, new_messages) with lists of {role, content} dicts. Return True
    to serve the cached answer, or a similarity/probability score compared to `threshold`.
    workers > 1 runs checks in parallel threads (useful for API-backed checks).

    ambiguous: how to score pairs whose answer equivalence depends on the application.
    Each has an `ambiguous` reason: "complementary" (two sides of one question: "which
    deductions are lawful?" vs "which are illegal?") or "context_dependent" (same answer
    only if the business works a certain way: "my child's school report" vs "their
    end-of-year report"). "different" (default, strict) counts them as traps, "same" as
    should-hit, "skip" leaves them out. They're reported as their own groups either way.
    """
    if ambiguous not in AMBIGUOUS:
        raise ValueError(f"ambiguous must be one of {AMBIGUOUS}")
    items = {"questions": load_questions, "conversations": load_conversations}[dataset]()
    if ambiguous == "skip":
        items = [i for i in items if not i.get("ambiguous")]

    def run(item):
        s = check(item["a"], item["b"])
        return float(s) if not isinstance(s, bool) else (1.0 if s else 0.0)

    if workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            scores = list(ex.map(run, items))
    else:
        scores = [run(i) for i in items]
    def label(i):
        return ambiguous == "same" if i.get("ambiguous") else bool(i["same_answer"])

    results = [Result(i["id"], i.get("ambiguous") or i.get("category") or i["subtype"],
                      length_bucket(i) if dataset == "conversations" else "", label(i), s, s >= threshold)
               for i, s in zip(items, scores)]
    return Report(dataset, threshold, results)
