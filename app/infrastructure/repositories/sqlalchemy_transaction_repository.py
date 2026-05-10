from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.transaction import Transaction, TransactionCategory, TransactionType
from app.infrastructure.database.models import TransactionModel


class SQLAlchemyTransactionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_many(self, transactions: list[Transaction]) -> list[Transaction]:
        self._session.add_all([transaction_to_model(transaction) for transaction in transactions])
        await self._session.flush()
        return transactions

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
        statement = select(TransactionModel).order_by(TransactionModel.date.desc())
        if user_id:
            statement = statement.where(TransactionModel.user_id == user_id)
        if start_date:
            statement = statement.where(TransactionModel.date >= start_date)
        if end_date:
            statement = statement.where(TransactionModel.date <= end_date)
        if category:
            statement = statement.where(TransactionModel.category == category)
        if account_id:
            statement = statement.where(TransactionModel.account_id == account_id)
        if transaction_type:
            statement = statement.where(TransactionModel.transaction_type == transaction_type)

        result = await self._session.execute(statement)
        return [transaction_from_model(model) for model in result.scalars().all()]


def transaction_to_model(transaction: Transaction) -> TransactionModel:
    return TransactionModel(
        id=transaction.id,
        account_id=transaction.account_id,
        user_id=transaction.user_id,
        date=transaction.date,
        description_original=transaction.description_original,
        description_normalized=transaction.description_normalized,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        category=transaction.category,
        source_file=transaction.source_file,
        created_at=transaction.created_at,
    )


def transaction_from_model(model: TransactionModel) -> Transaction:
    return Transaction(
        id=model.id,
        account_id=model.account_id,
        user_id=model.user_id,
        date=model.date,
        description_original=model.description_original,
        description_normalized=model.description_normalized,
        amount=model.amount,
        transaction_type=model.transaction_type,
        category=model.category,
        source_file=model.source_file,
        created_at=model.created_at,
    )
