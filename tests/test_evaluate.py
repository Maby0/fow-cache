from fow_cache import evaluate, load_conversations, load_questions


def test_datasets_load_with_balanced_labels():
    qs, convs = load_questions(), load_conversations()
    assert len(qs) == 600 and sum(q["same_answer"] for q in qs) == 300
    assert len(convs) == 240 and sum(c["same_answer"] for c in convs) == 120
    assert all(c["a"][-1]["role"] == "user" and c["b"][-1]["role"] == "user" for c in convs)


def test_always_serve_gets_every_trap_wrong():
    rep = evaluate(lambda a, b: True)
    assert rep.hit_rate == 1.0 and rep.wrong_rate == 1.0
    assert not rep.passes(0.05)


def test_exact_match_is_safe_but_misses_paraphrases():
    rep = evaluate(lambda a, b: a.strip().lower() == b.strip().lower())
    assert rep.wrong_rate == 0.0
    assert rep.hit_rate < 0.2


def test_scores_threshold_and_best_threshold():
    labels = {q["a"] + q["b"]: q["same_answer"] for q in load_questions()}
    rep = evaluate(lambda a, b: 0.9 if labels[a + b] else 0.4, threshold=0.5, ambiguous="skip")
    assert (rep.hit_rate, rep.wrong_rate) == (1.0, 0.0)
    assert rep.at_threshold(0.3).wrong_rate == 1.0
    assert rep.best_threshold(0.0) == (0.9, 1.0)


def test_conversation_last_message_check_fails_every_trap():
    rep = evaluate(lambda a, b: a[-1]["content"].lower().strip(" ?!.") == b[-1]["content"].lower().strip(" ?!."),
                   dataset="conversations")
    assert rep.wrong_rate > 0.9
    assert set(rep.by_group()) >= {"context_swap", "detail_swap", "intent_flip"}


def test_ambiguous_setting():
    strict = evaluate(lambda a, b: True)
    lenient = evaluate(lambda a, b: True, ambiguous="same")
    skipped = evaluate(lambda a, b: True, ambiguous="skip")
    n = sum(1 for q in load_questions() if q.get("ambiguous"))
    assert n >= 4 and {"complementary", "context_dependent"} <= set(strict.by_group())
    # strict: every ambiguous pair is a trap; lenient: every one is a hit
    assert sum(r.same_answer for r in lenient.results) == sum(r.same_answer for r in strict.results) + n
    assert sum(r.same_answer for r in strict.results) + n == sum(r.same_answer for r in skipped.results) + n
    assert len(skipped.results) == 600 - n
