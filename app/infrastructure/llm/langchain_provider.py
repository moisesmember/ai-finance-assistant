from typing import Any, Protocol

from app.domain.services.llm_provider import LLMProvider


class LangChainRunnable(Protocol):
    def invoke(self, input: Any) -> Any:
        raise NotImplementedError


class LangChainLLMProvider(LLMProvider):
    def __init__(
        self,
        runnable: LangChainRunnable,
        *,
        input_key: str | None = None,
    ) -> None:
        self._runnable = runnable
        self._input_key = input_key

    def generate_response(self, prompt: str) -> str:
        chain_input: str | dict[str, str] = prompt
        if self._input_key:
            chain_input = {self._input_key: prompt}

        response = self._runnable.invoke(chain_input)
        return extract_langchain_text(response)


def extract_langchain_text(response: Any) -> str:
    if isinstance(response, str):
        return response

    if isinstance(response, dict):
        return _extract_text_from_dict(response)

    content = getattr(response, "content", None)
    if content is not None:
        return _stringify_content(content)

    text = getattr(response, "text", None)
    if text is not None:
        return str(text)

    return str(response)


def _extract_text_from_dict(response: dict[str, Any]) -> str:
    for key in ("content", "text", "answer", "output", "result"):
        value = response.get(key)
        if value is not None:
            return _stringify_content(value)
    return str(response)


def _stringify_content(content: Any) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "\n".join(_stringify_content(item) for item in content)

    if isinstance(content, dict):
        text = content.get("text")
        if text is not None:
            return str(text)

    return str(content)
