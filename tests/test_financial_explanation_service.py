from datetime import date
from decimal import Decimal

from app.domain.entities.insight import Insight
from app.domain.entities.transaction import Transaction, TransactionCategory, TransactionType
from app.domain.services.financial_explanation_service import FinancialExplanationService
from app.domain.services.insight_generator import FinancialSummary


class CapturingLLMProvider:
    def __init__(self) -> None:
        self.prompt: str | None = None

    def generate_response(self, prompt: str) -> str:
        self.prompt = prompt
        return "explicacao gerada"


def test_financial_explanation_service_uses_structured_aggregates() -> None:
    provider = CapturingLLMProvider()
    service = FinancialExplanationService(provider)

    explanation = service.generate_explanation(_summary())

    assert explanation == "explicacao gerada"
    assert provider.prompt is not None
    assert "Total de receitas: 5000.00" in provider.prompt
    assert "Total de despesas: 1800.00" in provider.prompt
    assert "Variacao das despesas vs. mes anterior: 250.00" in provider.prompt
    assert "monthly_expense_delta" in provider.prompt


def test_financial_explanation_prompt_does_not_expose_raw_transactions() -> None:
    provider = CapturingLLMProvider()
    service = FinancialExplanationService(provider)

    service.generate_explanation(_summary())

    assert provider.prompt is not None
    assert "Compra sensivel no cartao" not in provider.prompt
    assert "compra sensivel no cartao" not in provider.prompt
    assert "Banco Principal" not in provider.prompt
    assert "Conta 1: 1800.00" in provider.prompt


def _summary() -> FinancialSummary:
    return FinancialSummary(
        month="2026-05",
        total_income=Decimal("5000.00"),
        total_expenses=Decimal("1800.00"),
        consolidated_balance=Decimal("3200.00"),
        largest_expense_category="Moradia",
        previous_month_expense_delta=Decimal("250.00"),
        top_expenses=[
            Transaction(
                account_id="account-1",
                user_id="user-1",
                date=date(2026, 5, 5),
                description_original="Compra sensivel no cartao",
                description_normalized="compra sensivel no cartao",
                amount=Decimal("1800.00"),
                transaction_type=TransactionType.DEBIT,
                category=TransactionCategory.HOUSING,
            )
        ],
        expenses_by_account={"Banco Principal": Decimal("1800.00")},
        credit_card_usage_percentage=Decimal("0.00"),
        insights=[
            Insight(
                message="As despesas cresceram em relacao ao mes anterior.",
                metric="monthly_expense_delta",
                value=Decimal("250.00"),
            )
        ],
    )
