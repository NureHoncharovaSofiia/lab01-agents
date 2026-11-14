"""Базова лінія для експерименту."""

from google import genai


def one_shot_answer(client: genai.Client, model: str, goal: str) -> str:
    """Повертає відповідь на запит за один виклик моделі."""
    response = client.models.generate_content(
        model=model,
        contents=f"Дай коротку відповідь українською.\n\n{goal}",
    )
    return response.text or ""
