from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Abstraction over the underlying text-generation backend.

    Every concrete provider (Anthropic, local template fallback, …) takes
    a system prompt and a user prompt and returns plain generated text —
    document assembly and versioning live in DocumentService, not here.
    """

    name: str

    @abstractmethod
    def generate(self, system: str, prompt: str) -> str:
        raise NotImplementedError
