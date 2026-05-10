from app.infrastructure.llm.langchain_provider import LangChainLLMProvider, LangChainRunnable


def create_langchain_provider_from_runnable(
    runnable: LangChainRunnable,
    *,
    input_key: str | None = None,
) -> LangChainLLMProvider:
    return LangChainLLMProvider(runnable, input_key=input_key)


def create_prompt_template_chain_provider(
    *,
    chat_model: object,
    system_message: str,
    human_template: str = "{prompt}",
) -> LangChainLLMProvider:
    try:
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
    except ImportError as exc:
        raise RuntimeError(
            "Dependencias do LangChain nao instaladas. "
            "Instale langchain-core para usar este provider."
        ) from exc

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("human", human_template),
        ]
    )
    runnable = prompt_template | chat_model | StrOutputParser()
    return LangChainLLMProvider(runnable, input_key="prompt")
