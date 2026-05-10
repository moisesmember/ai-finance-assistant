from datetime import date
from decimal import Decimal

from app.domain.entities.account import AccountType
from app.domain.entities.transaction import Transaction, TransactionCategory, TransactionType
from app.domain.services.insight_generator import BasicInsightGenerator


def test_basic_insight_generator_returns_monthly_summary() -> None:
    checking_id = "checking"
    card_id = "card"
    transactions = [
        Transaction(
            account_id=checking_id,
            user_id="user-1",
            date=date(2026, 5, 3),
            description_original="Salario",
            description_normalized="salario",
            amount=Decimal("5000.00"),
            transaction_type=TransactionType.CREDIT,
            category=TransactionCategory.OTHER,
        ),
        Transaction(
            account_id=card_id,
            user_id="user-1",
            date=date(2026, 5, 4),
            description_original="Ifood",
            description_normalized="ifood",
            amount=Decimal("100.00"),
            transaction_type=TransactionType.DEBIT,
            category=TransactionCategory.FOOD,
        ),
        Transaction(
            account_id=card_id,
            user_id="user-1",
            date=date(2026, 5, 5),
            description_original="Restaurante",
            description_normalized="restaurante",
            amount=Decimal("200.00"),
            transaction_type=TransactionType.DEBIT,
            category=TransactionCategory.FOOD,
        ),
        Transaction(
            account_id=checking_id,
            user_id="user-1",
            date=date(2026, 4, 10),
            description_original="Mercado",
            description_normalized="mercado",
            amount=Decimal("120.00"),
            transaction_type=TransactionType.DEBIT,
            category=TransactionCategory.GROCERIES,
        ),
    ]

    summary = BasicInsightGenerator().generate_summary(
        transactions=transactions,
        month_start=date(2026, 5, 1),
        account_names_by_id={checking_id: "Santander Conta", card_id: "Nubank Cartao"},
        account_types_by_id={
            checking_id: AccountType.CHECKING_ACCOUNT,
            card_id: AccountType.CREDIT_CARD,
        },
    )

    assert summary.month == "2026-05"
    assert summary.total_income == Decimal("5000.00")
    assert summary.total_expenses == Decimal("300.00")
    assert summary.consolidated_balance == Decimal("4700.00")
    assert summary.largest_expense_category == "Alimentação"
    assert summary.previous_month_expense_delta == Decimal("180.00")
    assert summary.credit_card_usage_percentage == Decimal("100.00")
    assert summary.expenses_by_account == {"Nubank Cartao": Decimal("300.00")}
    assert summary.insights[0].message == "Alimentação representa 100.00% das despesas do mes."
