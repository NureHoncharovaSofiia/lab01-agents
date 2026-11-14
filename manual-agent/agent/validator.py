"""Перевірка рішення перед виконанням дії."""

from .errors import DecisionError

ALLOWED_ACTIONS = {"lookup_pattern": "name", "finish": "answer"}


def validate_decision(decision: object) -> None:
    """Перевіряє дію, аргументи та коротке пояснення."""
    if not isinstance(decision, dict):
        raise DecisionError("Рішення має бути JSON-об'єктом.")

    action = decision.get("action")
    if not isinstance(action, str) or action not in ALLOWED_ACTIONS:
        raise DecisionError(f"Невідома дія: {action!r}.")

    expected = ALLOWED_ACTIONS[action]
    arguments = decision.get("arguments")
    if not isinstance(arguments, dict) or set(arguments) != {expected}:
        raise DecisionError(f"Дія {action!r} потребує лише аргумент {expected!r}.")

    value = arguments[expected]
    if not isinstance(value, str) or not value.strip():
        raise DecisionError(f"Аргумент {expected!r} має бути непорожнім рядком.")

    summary = decision.get("decision_summary")
    if not isinstance(summary, str) or not summary.strip():
        raise DecisionError("decision_summary має бути непорожнім рядком.")
