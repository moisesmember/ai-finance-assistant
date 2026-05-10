from typing import Protocol


class LLMProvider(Protocol):
    def generate_response(self, prompt: str) -> str:
        raise NotImplementedError
