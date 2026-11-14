"""Стан агента під час одного запуску."""

from dataclasses import dataclass, field


@dataclass
class AgentState:
    """Зберігає мету, спостереження та підсумок виконання."""

    goal: str
    observations: list[str] = field(default_factory=list)
    trace: list[dict] = field(default_factory=list)
    step: int = 0
    final_answer: str = ""
    stop_reason: str = ""
