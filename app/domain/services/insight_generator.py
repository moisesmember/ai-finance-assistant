from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Protocol

from app.domain.entities.account import AccountType
from app.domain.entities.insight import Insight
from app.domain.entities.transaction import Transaction, TransactionType


@dataclass(slots=True)
class FinancialSummary:
    month: str
    total_income: Decimal
    total_expenses: Decimal
    consolidated_balance: Decimal
    largest_expense_category: str | None
    previous_month_expense_delta: Decimal
    top_expenses: list[Transaction]
    expenses_by_account: dict[str, Decimal]
    credit_card_usage_percentage: Decimal
    insights: list[Insight]


class InsightGenerator(Protocol):
    def generate_summary(
        self,
        *,
        transactions: list[Transaction],
        month_start: date,
        account_names_by_id: dict[str, str],
        account_types_by_id: dict[str, AccountType],
    ) -> FinancialSummary:
        raise NotImplementedError


class BasicInsightGenerator:
    def generate_summary(
        self,
        *,
        transactions: list[Transaction],
        month_start: date,
        account_names_by_id: dict[str, str],
        account_types_by_id: dict[str, AccountType],
    ) -> FinancialSummary:
        month_transactions = [
            transaction
            for transaction in transactions
            if transaction.date.year == month_start.year and transaction.date.month == month_start.month
        ]
        previous_month = _previous_month(month_start)
        previous_month_transactions = [
            transaction
            for transaction in transactions
            if transaction.date.year == previous_month.year
            and transaction.date.month == previous_month.month
        ]

        total_income = sum_amount(month_transactions, TransactionType.CREDIT)
        total_expenses = sum_amount(month_transactions, TransactionType.DEBIT)
        previous_expenses = sum_amount(previous_month_transactions, TransactionType.DEBIT)
        consolidated_balance = total_income - total_expenses
        previous_delta = total_expenses - previous_expenses

        expenses_by_category: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        expenses_by_account: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        credit_card_expenses = Decimal("0")

        debit_transactions = [
            transaction
            for transaction in month_transactions
            if transaction.transaction_type == TransactionType.DEBIT
        ]

        for transaction in debit_transactions:
            expenses_by_category[str(transaction.category)] += transaction.amount
            account_name = account_names_by_id.get(transaction.account_id, transaction.account_id)
            expenses_by_account[account_name] += transaction.amount
            if account_types_by_id.get(transaction.account_id) == AccountType.CREDIT_CARD:
                credit_card_expenses += transaction.amount

        largest_category = None
        if expenses_by_category:
            largest_category = max(expenses_by_category, key=lambda category: expenses_by_category[category])

        top_expenses = sorted(debit_transactions, key=lambda transaction: transaction.amount, reverse=True)[:5]
        card_usage_percentage = percentage(credit_card_expenses, total_expenses)

        insights = self._build_insights(
            total_expenses=total_expenses,
            largest_category=largest_category,
            expenses_by_category=expenses_by_category,
            previous_delta=previous_delta,
            credit_card_usage_percentage=card_usage_percentage,
        )

        return FinancialSummary(
            month=month_start.strftime("%Y-%m"),
            total_income=total_income,
            total_expenses=total_expenses,
            consolidated_balance=consolidated_balance,
            largest_expense_category=largest_category,
            previous_month_expense_delta=previous_delta,
            top_expenses=top_expenses,
            expenses_by_account=dict(expenses_by_account),
            credit_card_usage_percentage=card_usage_percentage,
            insights=insights,
        )

    def _build_insights(
        self,
        *,
        total_expenses: Decimal,
        largest_category: str | None,
        expenses_by_category: dict[str, Decimal],
        previous_delta: Decimal,
        credit_card_usage_percentage: Decimal,
    ) -> list[Insight]:
        insights: list[Insight] = []
        if largest_category and total_expenses > 0:
            category_percentage = percentage(expenses_by_category[largest_category], total_expenses)
            insights.append(
                Insight(
                    message=(
                        f"{largest_category} representa {category_percentage}% "
                        "das despesas do mes."
                    ),
                    metric="largest_category_percentage",
                    value=category_percentage,
                )
            )

        if previous_delta > 0:
            insights.append(
                Insight(
                    message="As despesas cresceram em relacao ao mes anterior.",
                    metric="monthly_expense_delta",
                    value=previous_delta,
                )
            )
        elif previous_delta < 0:
            insights.append(
                Insight(
                    message="As despesas reduziram em relacao ao mes anterior.",
                    metric="monthly_expense_delta",
                    value=previous_delta,
                )
            )

        insights.append(
            Insight(
                message=f"Cartoes representam {credit_card_usage_percentage}% das despesas do mes.",
                metric="credit_card_usage_percentage",
                value=credit_card_usage_percentage,
            )
        )
        return insights


def sum_amount(transactions: list[Transaction], transaction_type: TransactionType) -> Decimal:
    return sum(
        (transaction.amount for transaction in transactions if transaction.transaction_type == transaction_type),
        Decimal("0"),
    )


def percentage(value: Decimal, total: Decimal) -> Decimal:
    if total == 0:
        return Decimal("0")
    return ((value / total) * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _previous_month(month_start: date) -> date:
    if month_start.month == 1:
        return date(month_start.year - 1, 12, 1)
    return date(month_start.year, month_start.month - 1, 1)
