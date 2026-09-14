from app.services.ai.base import AIProvider


class LocalProvider(AIProvider):
    """Deterministic, network-free stand-in for a real AI provider.

    Used when AI_PROVIDER=local (explicit offline mode) and by the test
    suite, so automated tests never depend on a live API key. It does not
    pretend to write like an LLM — it clearly labels its output as a
    local draft and simply reflects back the assembled prompt, so the
    user always knows this is not real AI-generated prose.
    """

    name = "local"

    def generate(self, system: str, prompt: str) -> str:
        return (
            "[Brouillon généré en local, sans IA externe — configurez "
            "AI_PROVIDER=anthropic dans .env pour une génération par IA réelle]\n\n"
            f"{prompt.strip()}"
        )
