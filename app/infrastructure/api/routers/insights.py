from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.generate_insights import GenerateInsightsQuery, GenerateInsightsUseCase
from app.core.config import get_settings
from app.domain.services.financial_explanation_service import FinancialExplanationService
from app.domain.services.insight_generator import BasicInsightGenerator
from app.domain.services.llm_provider import LLMProvider
from app.infrastructure.api.dependencies import get_llm_provider, get_session
from app.infrastructure.api.schemas import FinancialExplanationResponse, SummaryResponse
from app.infrastructure.repositories.sqlalchemy_account_repository import SQLAlchemyAccountRepository
from app.infrastructure.repositories.sqlalchemy_transaction_repository import (
    SQLAlchemyTransactionRepository,
)


router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/summary", response_model=SummaryResponse)
async def summary(
    month: date | None = Query(default=None),
    user_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> SummaryResponse:
    use_case = GenerateInsightsUseCase(
        account_repository=SQLAlchemyAccountRepository(session),
        transaction_repository=SQLAlchemyTransactionRepository(session),
        insight_generator=BasicInsightGenerator(),
    )
    result = await use_case.execute(
        GenerateInsightsQuery(
            user_id=user_id or get_settings().default_user_id,
            month=month or date.today().replace(day=1),
        )
    )
    return SummaryResponse.from_summary(result)


@router.get("/explanation", response_model=FinancialExplanationResponse)
async def explanation(
    month: date | None = Query(default=None),
    user_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    llm_provider: LLMProvider = Depends(get_llm_provider),
) -> FinancialExplanationResponse:
    insights_use_case = GenerateInsightsUseCase(
        account_repository=SQLAlchemyAccountRepository(session),
        transaction_repository=SQLAlchemyTransactionRepository(session),
        insight_generator=BasicInsightGenerator(),
    )
    summary_result = await insights_use_case.execute(
        GenerateInsightsQuery(
            user_id=user_id or get_settings().default_user_id,
            month=month or date.today().replace(day=1),
        )
    )
    explanation_service = FinancialExplanationService(llm_provider=llm_provider)

    return FinancialExplanationResponse(
        month=summary_result.month,
        explanation=explanation_service.generate_explanation(summary_result),
    )
