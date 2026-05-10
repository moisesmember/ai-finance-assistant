from dataclasses import dataclass
from datetime import date

from app.domain.entities.transaction import Transaction, TransactionCategory, TransactionType
from app.domain.repositories.transaction_repository import TransactionRepository


@dataclass(slots=True)
class ListTransactionsQuery:
    user_id: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    category: TransactionCategory | None = None
    account_id: str | None = None
    transaction_type: TransactionType | None = None


class ListTransactionsUseCase:
    def __init__(self, transaction_repository: TransactionRepository) -> None:
        self._transaction_repository = transaction_repository

    async def execute(self, query: ListTransactionsQuery) -> list[Transaction]:
        return await self._transaction_repository.list(
            user_id=query.user_id,
            start_date=query.start_date,
            end_date=query.end_date,
            category=query.category,
            account_id=query.account_id,
            transaction_type=query.transaction_type,
        )
