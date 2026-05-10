from typing import Protocol

from app.domain.entities.transaction import Transaction


class TransactionEmbeddingService(Protocol):
    async def embed_description(self, description: str) -> list[float]:
        raise NotImplementedError


class SupervisedTransactionClassifier(Protocol):
    async def predict_category(self, transaction: Transaction) -> str:
        raise NotImplementedError


class ExplainabilityService(Protocol):
    async def explain_transaction_prediction(self, transaction: Transaction) -> dict[str, float]:
        raise NotImplementedError


class LLMFinancialAdvisor(Protocol):
    async def summarize_context(self, transactions: list[Transaction]) -> str:
        raise NotImplementedError


class TemporalAnalysisService(Protocol):
    async def detect_trends(self, transactions: list[Transaction]) -> dict[str, float | str]:
        raise NotImplementedError
