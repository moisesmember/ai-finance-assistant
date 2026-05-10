from app.domain.services.financial_explanation_prompt import build_financial_explanation_prompt
from app.domain.services.insight_generator import FinancialSummary
from app.domain.services.llm_provider import LLMProvider


class FinancialExplanationService:
    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm_provider = llm_provider

    def generate_explanation(self, summary: FinancialSummary) -> str:
        prompt = build_financial_explanation_prompt(summary)
        return self._llm_provider.generate_response(prompt)
