"""Локальні перевірки довідника, валідатора та циклу."""

import pytest

from agent.environment import lookup_pattern
from agent.errors import DecisionError
from agent.loop import MAX_STEPS, run_agent
from agent.validator import validate_decision


def test_existing_pattern():
    assert lookup_pattern(" FACTORY-METHOD ").startswith("Factory Method")


def test_missing_pattern():
    assert lookup_pattern("unknown").startswith("NOT_FOUND")


def test_unknown_action():
    with pytest.raises(DecisionError, match="Невідома дія"):
        validate_decision({"action": "unknown"})


def test_lookup_then_finish():
    def decide(goal, observations, step, max_steps):
        if step == 1:
            return {
                "action": "lookup_pattern",
                "arguments": {"name": "Observer"},
                "decision_summary": "Шукаємо опис Observer.",
            }
        assert observations[0].startswith("Observer")
        return {
            "action": "finish",
            "arguments": {"answer": observations[0]},
            "decision_summary": "Повертаємо знайдений опис.",
        }

    state = run_agent("Поясни Observer", decide)
    assert state.stop_reason == "finish"
    assert state.step == len(state.trace) == 2
    assert state.final_answer == lookup_pattern("Observer")


def test_invalid_actions_become_observations_and_stop_at_limit():
    def decide(goal, observations, step, max_steps):
        if step > 1:
            assert observations[-1].startswith("ERROR: Невідома дія")
        return {"action": "unknown"}

    state = run_agent("Поясни Observer", decide)
    assert state.stop_reason == "max_steps"
    assert state.step == len(state.trace) == len(state.observations) == MAX_STEPS
