from fastapi import HTTPException, status

from app.core.config import settings
from app.services.ai.base import AIProvider
from app.services.ai.local_provider import LocalProvider


def get_ai_provider() -> AIProvider:
    provider = settings.AI_PROVIDER

    if provider == "anthropic":
        from app.services.ai.anthropic_provider import AnthropicProvider

        if not settings.AI_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI_PROVIDER=anthropic mais AI_API_KEY n'est pas configurée.",
            )
        return AnthropicProvider(api_key=settings.AI_API_KEY, model=settings.AI_MODEL)

    if provider == "openai":
        from app.services.ai.openai_provider import OpenAIProvider

        if not settings.AI_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI_PROVIDER=openai mais AI_API_KEY n'est pas configurée.",
            )
        return OpenAIProvider(api_key=settings.AI_API_KEY, model=settings.AI_MODEL)

    if provider == "local":
        return LocalProvider()

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Module AI Writer non configuré (AI_PROVIDER=none). "
        "Définissez AI_PROVIDER=anthropic, openai ou local dans la configuration.",
    )
