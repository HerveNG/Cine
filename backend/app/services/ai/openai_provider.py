import openai
from fastapi import HTTPException, status

from app.services.ai.base import AIProvider


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self, api_key: str, model: str):
        self._client = openai.OpenAI(api_key=api_key)
        self._model = model

    def generate(self, system: str, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                max_completion_tokens=2048,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            )
        except openai.APIError as exc:
            # Same rationale as AnthropicProvider: surface a clean, actionable
            # error (exhausted quota, invalid key…) instead of a raw 500.
            message = getattr(exc, "message", None) or str(exc)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Le service IA (OpenAI) a renvoyé une erreur : {message}",
            ) from exc

        content = response.choices[0].message.content
        return (content or "").strip()
