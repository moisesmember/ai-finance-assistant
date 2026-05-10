from datetime import date
from typing import Protocol

from app.domain.entities.transaction import Transaction, TransactionCategory, TransactionType


class TransactionRepository(Protocol):
    async def add_many(self, transactions: list[Transaction]) -> list[Transaction]:
        raise NotImplementedError

    async def list(
        self,
        *,
        user_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        category: TransactionCategory | None = None,
        account_id: str | None = None,
        transaction_type: TransactionType | None = None,
    ) -> list[Transaction]:
        raise NotImplementedError
