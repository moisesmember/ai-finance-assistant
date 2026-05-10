from datetime import date

from app.domain.entities.account import Account, AccountType
from app.domain.entities.transaction import Transaction, TransactionCategory, TransactionType


class InMemoryAccountRepository:
    def __init__(self) -> None:
        self.accounts: list[Account] = []

    async def get_by_id(self, account_id: str) -> Account | None:
        return next((account for account in self.accounts if account.id == account_id), None)

    async def get_by_identity(
        self,
        *,
        name: str,
        institution: str,
        account_type: AccountType,
    ) -> Account | None:
        return next(
            (
                account
                for account in self.accounts
                if account.name == name
                and account.institution == institution
                and account.type == account_type
            ),
            None,
        )

    async def add(self, account: Account) -> Account:
        self.accounts.append(account)
        return account

    async def list_all(self) -> list[Account]:
        return list(self.accounts)


class InMemoryTransactionRepository:
    def __init__(self) -> None:
        self.transactions: list[Transaction] = []

    async def add_many(self, transactions: list[Transaction]) -> list[Transaction]:
        self.transactions.extend(transactions)
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
        result = list(self.transactions)
        if user_id:
            result = [transaction for transaction in result if transaction.user_id == user_id]
        if start_date:
            result = [transaction for transaction in result if transaction.date >= start_date]
        if end_date:
            result = [transaction for transaction in result if transaction.date <= end_date]
        if category:
            result = [transaction for transaction in result if transaction.category == category]
        if account_id:
            result = [transaction for transaction in result if transaction.account_id == account_id]
        if transaction_type:
            result = [
                transaction
                for transaction in result
                if transaction.transaction_type == transaction_type
            ]
        return result
