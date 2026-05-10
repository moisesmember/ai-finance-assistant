from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.import_transactions import ImportTransactionsUseCase
from app.application.use_cases.list_transactions import (
    ListTransactionsQuery,
    ListTransactionsUseCase,
)
from app.core.config import get_settings
from app.domain.entities.transaction import TransactionCategory, TransactionType
from app.domain.services.transaction_classifier import KeywordTransactionClassifier
from app.infrastructure.api.dependencies import get_session
from app.infrastructure.api.schemas import ImportTransactionsResponse, TransactionResponse
from app.infrastructure.repositories.sqlalchemy_account_repository import SQLAlchemyAccountRepository
from app.infrastructure.repositories.sqlalchemy_transaction_repository import (
    SQLAlchemyTransactionRepository,
)


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/import", response_model=ImportTransactionsResponse)
async def import_transactions(
    file: UploadFile = File(...),
    user_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> ImportTransactionsResponse:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie um arquivo CSV.",
        )

    use_case = ImportTransactionsUseCase(
        account_repository=SQLAlchemyAccountRepository(session),
        transaction_repository=SQLAlchemyTransactionRepository(session),
        classifier=KeywordTransactionClassifier(),
    )
    try:
        result = await use_case.execute(
            csv_content=await file.read(),
            source_file=file.filename,
            user_id=user_id or get_settings().default_user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ImportTransactionsResponse(
        imported_count=result.imported_count,
        created_accounts_count=result.created_accounts_count,
        source_file=result.source_file,
    )


@router.get("", response_model=list[TransactionResponse])
async def list_transactions(
    start_date: date | None = None,
    end_date: date | None = None,
    category: TransactionCategory | None = None,
    account_id: str | None = None,
    transaction_type: TransactionType | None = None,
    user_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[TransactionResponse]:
    use_case = ListTransactionsUseCase(SQLAlchemyTransactionRepository(session))
    transactions = await use_case.execute(
        ListTransactionsQuery(
            user_id=user_id or get_settings().default_user_id,
            start_date=start_date,
            end_date=end_date,
            category=category,
            account_id=account_id,
            transaction_type=transaction_type,
        )
    )
    return [TransactionResponse.from_entity(transaction) for transaction in transactions]
