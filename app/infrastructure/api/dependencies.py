from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.services.insight_generator import BasicInsightGenerator
from app.domain.services.llm_provider import LLMProvider
from app.domain.services.transaction_classifier import KeywordTransactionClassifier
from app.infrastructure.database.session import get_session
from app.infrastructure.llm.fake_llm_provider import FakeLLMProvider
from app.infrastructure.repositories.sqlalchemy_account_repository import (
    SQLAlchemyAccountRepository,
)
from app.infrastructure.repositories.sqlalchemy_transaction_repository import (
    SQLAlchemyTransactionRepository,
)


def get_llm_provider() -> LLMProvider:
    return FakeLLMProvider()


__all__ = [
    "AsyncSession",
    "BasicInsightGenerator",
    "FakeLLMProvider",
    "KeywordTransactionClassifier",
    "LLMProvider",
    "SQLAlchemyAccountRepository",
    "SQLAlchemyTransactionRepository",
    "get_llm_provider",
    "get_session",
]
