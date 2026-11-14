"""Диспетчер дій і цикл агента."""

from collections.abc import Callable

from .environment import lookup_pattern
from .errors import DecisionError
from .state import AgentState
from .validator import validate_decision

MAX_STEPS = 6


def execute_action(decision: dict, state: AgentState) -> str | None:
    """Виконує дозволену дію та повертає спостереження."""
    validate_decision(decision)
    arguments = decision["arguments"]
    if decision["action"] == "lookup_pattern":
        return lookup_pattern(arguments["name"])

    state.final_answer = arguments["answer"]
    state.stop_reason = "finish"
    return None


def run_agent(
    goal: str,
    decide: Callable[[str, list[str], int, int], dict],
    max_steps: int = MAX_STEPS,
) -> AgentState:
    """Виконує кроки до фінальної відповіді або вичерпання ліміту."""
    state = AgentState(goal=goal)
    for step in range(1, max_steps + 1):
        state.step = step
        decision = None
        try:
            decision = decide(goal, state.observations.copy(), step, max_steps)
            observation = execute_action(decision, state)
        except DecisionError as error:
            observation = f"ERROR: {error}"

        if observation is not None:
            state.observations.append(observation)
        state.trace.append(
            {"step": step, "decision": decision, "observation": observation}
        )
        if state.stop_reason == "finish":
            return state

    state.stop_reason = "max_steps"
    state.final_answer = "Досягнуто ліміту кроків без фінальної відповіді."
    return state
