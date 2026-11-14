"""Запуск агента або базової лінії з термінала."""

import argparse
import json
import os
from dataclasses import asdict
from functools import partial
from pathlib import Path
from time import perf_counter

from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

from agent.loop import run_agent
from agent.reasoning import get_decision
from baseline import one_shot_answer


def main() -> None:
    """Читає параметри запуску, викликає модель та виводить результат."""
    load_dotenv(Path(__file__).with_name(".env"))

    parser = argparse.ArgumentParser(description="Довідник патернів GoF")
    parser.add_argument("goal", help="Запит користувача")
    parser.add_argument("--mode", choices=("agent", "oneshot"), default="agent")
    parser.add_argument("--model", default=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"))
    parser.add_argument("--trace", type=Path, default=Path("traces/manual.json"))
    args = parser.parse_args()

    key = os.getenv("GEMINI_API_KEY")
    if not key:
        parser.exit(1, "Додай GEMINI_API_KEY у файл manual-agent/.env.\n")

    start = perf_counter()
    try:
        with genai.Client(
            api_key=key,
            http_options={"timeout": 60000, "retry_options": {"attempts": 1}},
        ) as client:
            if args.mode == "oneshot":
                print(one_shot_answer(client, args.model, args.goal) or "Порожня відповідь.")
                print("Викликів LLM: 1. Дій: 0.")
                print(f"Час: {perf_counter() - start:.2f} с")
                return

            state = run_agent(args.goal, partial(get_decision, client, args.model))
    except APIError as error:
        parser.exit(1, f"Помилка Gemini API: {error.code} {error.status}\n")
    except TimeoutError:
        parser.exit(1, "Перевищено час очікування відповіді Gemini.\n")

    result = asdict(state)
    result["model"] = args.model
    result["llm_calls"] = state.step
    result["elapsed_seconds"] = round(perf_counter() - start, 3)

    args.trace.parent.mkdir(parents=True, exist_ok=True)
    args.trace.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(state.final_answer)
    print(f"Кроків: {state.step}. Викликів LLM: {result['llm_calls']}.")
    print(f"Причина завершення: {state.stop_reason}")
    print(f"Час: {result['elapsed_seconds']:.2f} с")
    print(f"Трасу збережено: {args.trace}")


if __name__ == "__main__":
    main()
