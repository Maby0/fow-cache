import pytest

from fow_cache import costs
from fow_cache.cli import main


def test_batched_guard_is_cheaper_than_per_turn_facts():
    s = costs.Scenario()
    assert costs.guard_cost(s) < costs.guard_cost(s, "facts every turn")
    assert 0 < costs.break_even(s) < costs.break_even(s, "facts every turn")


def test_prompt_caching_raises_break_even():
    cached, uncached = costs.Scenario(prompt_caching=True), costs.Scenario(prompt_caching=False)
    assert costs.break_even(cached) > costs.break_even(uncached)


def test_cli_max_wrong_fails_ci(monkeypatch, capsys):
    import fow_cache.cli as cli
    monkeypatch.setattr(cli, "_load_callable", lambda spec: (lambda a, b: True))
    with pytest.raises(SystemExit) as e:
        main(["eval", "--check", "x:y", "--max-wrong", "0.05"])
    assert e.value.code == 1
    assert "FAIL" in capsys.readouterr().err


def test_cli_costs_prints_break_even(capsys):
    main(["costs", "--model", "haiku-4.5"])
    assert "break-even hit rate" in capsys.readouterr().out
