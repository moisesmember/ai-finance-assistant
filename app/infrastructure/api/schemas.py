from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.domain.entities.account import Account, AccountType
from app.domain.entities.transaction import Transaction, TransactionCategory, TransactionType
from app.domain.services.insight_generator import FinancialSummary


class AccountCreateRequest(BaseModel):
    name: str
    institution: str
    type: AccountType


class AccountResponse(BaseModel):
    id: str
    name: str
    institution: str
    type: AccountType
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_entity(cls, account: Account) -> "AccountResponse":
        return cls.model_validate(account)


class TransactionResponse(BaseModel):
    id: str
    account_id: str
    user_id: str
    date: date
    description_original: str
    description_normalized: str
    amount: Decimal
    transaction_type: TransactionType
    category: TransactionCategory
    source_file: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_entity(cls, transaction: Transaction) -> "TransactionResponse":
        return cls.model_validate(transaction)


class ImportTransactionsResponse(BaseModel):
    imported_count: int
    created_accounts_count: int
    source_file: str | None


class InsightResponse(BaseModel):
    message: str
    metric: str
    value: Decimal | int | float | str


class SummaryResponse(BaseModel):
    month: str
    total_income: Decimal
    total_expenses: Decimal
    consolidated_balance: Decimal
    largest_expense_category: str | None
    previous_month_expense_delta: Decimal
    top_expenses: list[TransactionResponse]
    expenses_by_account: dict[str, Decimal]
    credit_card_usage_percentage: Decimal
    insights: list[InsightResponse]

    @classmethod
    def from_summary(cls, summary: FinancialSummary) -> "SummaryResponse":
        return cls(
            month=summary.month,
            total_income=summary.total_income,
            total_expenses=summary.total_expenses,
            consolidated_balance=summary.consolidated_balance,
            largest_expense_category=summary.largest_expense_category,
            previous_month_expense_delta=summary.previous_month_expense_delta,
            top_expenses=[
                TransactionResponse.from_entity(transaction)
                for transaction in summary.top_expenses
            ],
            expenses_by_account=summary.expenses_by_account,
            credit_card_usage_percentage=summary.credit_card_usage_percentage,
            insights=[
                InsightResponse(
                    message=insight.message,
                    metric=insight.metric,
                    value=insight.value,
                )
                for insight in summary.insights
            ],
        )


class FinancialExplanationResponse(BaseModel):
    month: str
    explanation: str
