import anthropic
from fastapi import HTTPException, status

from app.services.ai.base import AIProvider


class AnthropicProvider(AIProvider):
    name = "anthropic"

    def __init__(self, api_key: str, model: str):
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def generate(self, system: str, prompt: str) -> str:
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=2048,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
        except anthropic.APIError as exc:
            # Surface a clean, actionable error instead of a raw 500 — the
            # most common causes here are an exhausted credit balance or an
            # invalid API key, both of which the user can act on directly.
            message = getattr(exc, "message", None) or str(exc)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Le service IA (Anthropic) a renvoyé une erreur : {message}",
            ) from exc
        return "".join(block.text for block in response.content if block.type == "text").strip()
