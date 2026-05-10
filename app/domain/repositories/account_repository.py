from typing import Protocol

from app.domain.entities.account import Account, AccountType


class AccountRepository(Protocol):
    async def get_by_id(self, account_id: str) -> Account | None:
        raise NotImplementedError

    async def get_by_identity(
        self,
        *,
        name: str,
        institution: str,
        account_type: AccountType,
    ) -> Account | None:
        raise NotImplementedError

    async def add(self, account: Account) -> Account:
        raise NotImplementedError

    async def list_all(self) -> list[Account]:
        raise NotImplementedError
