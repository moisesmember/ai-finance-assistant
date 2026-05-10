from dataclasses import dataclass
from typing import Any

from app.infrastructure.llm.langchain_provider import (
    LangChainLLMProvider,
    extract_langchain_text,
)


class EchoRunnable:
    def __init__(self) -> None:
        self.received_input: Any = None

    def invoke(self, input: Any) -> dict[str, str]:
        self.received_input = input
        return {"content": "resposta da chain"}


@dataclass(slots=True)
class MessageResponse:
    content: str


def test_langchain_provider_adapts_prompt_to_runnable_input_key() -> None:
    runnable = EchoRunnable()
    provider = LangChainLLMProvider(runnable, input_key="prompt")

    response = provider.generate_response("prompt estruturado")

    assert response == "resposta da chain"
    assert runnable.received_input == {"prompt": "prompt estruturado"}


def test_extract_langchain_text_supports_common_response_shapes() -> None:
    assert extract_langchain_text("texto direto") == "texto direto"
    assert extract_langchain_text({"answer": "texto em dict"}) == "texto em dict"
    assert extract_langchain_text(MessageResponse(content="texto em mensagem")) == (
        "texto em mensagem"
    )
