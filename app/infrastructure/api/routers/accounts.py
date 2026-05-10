from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.account import Account
from app.infrastructure.api.dependencies import get_session
from app.infrastructure.api.schemas import AccountCreateRequest, AccountResponse
from app.infrastructure.repositories.sqlalchemy_account_repository import SQLAlchemyAccountRepository


router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountResponse])
async def list_accounts(session: AsyncSession = Depends(get_session)) -> list[AccountResponse]:
    repository = SQLAlchemyAccountRepository(session)
    accounts = await repository.list_all()
    return [AccountResponse.from_entity(account) for account in accounts]


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> AccountResponse:
    repository = SQLAlchemyAccountRepository(session)
    existing = await repository.get_by_identity(
        name=payload.name,
        institution=payload.institution,
        account_type=payload.type,
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conta ja existe para nome, instituicao e tipo informados.",
        )

    account = await repository.add(
        Account(name=payload.name, institution=payload.institution, type=payload.type)
    )
    return AccountResponse.from_entity(account)
