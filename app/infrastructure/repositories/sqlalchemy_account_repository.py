from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.account import Account, AccountType
from app.infrastructure.database.models import AccountModel


class SQLAlchemyAccountRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, account_id: str) -> Account | None:
        model = await self._session.get(AccountModel, account_id)
        return account_from_model(model) if model else None

    async def get_by_identity(
        self,
        *,
        name: str,
        institution: str,
        account_type: AccountType,
    ) -> Account | None:
        result = await self._session.execute(
            select(AccountModel).where(
                AccountModel.name == name,
                AccountModel.institution == institution,
                AccountModel.type == account_type,
            )
        )
        model = result.scalar_one_or_none()
        return account_from_model(model) if model else None

    async def add(self, account: Account) -> Account:
        model = AccountModel(
            id=account.id,
            name=account.name,
            institution=account.institution,
            type=account.type,
            created_at=account.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return account

    async def list_all(self) -> list[Account]:
        result = await self._session.execute(select(AccountModel).order_by(AccountModel.name))
        return [account_from_model(model) for model in result.scalars().all()]


def account_from_model(model: AccountModel) -> Account:
    return Account(
        id=model.id,
        name=model.name,
        institution=model.institution,
        type=model.type,
        created_at=model.created_at,
    )
