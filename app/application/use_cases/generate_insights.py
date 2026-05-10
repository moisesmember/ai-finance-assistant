from dataclasses import dataclass
from datetime import date

from app.domain.repositories.account_repository import AccountRepository
from app.domain.repositories.transaction_repository import TransactionRepository
from app.domain.services.insight_generator import FinancialSummary, InsightGenerator


@dataclass(slots=True)
class GenerateInsightsQuery:
    user_id: str
    month: date


class GenerateInsightsUseCase:
    def __init__(
        self,
        *,
        account_repository: AccountRepository,
        transaction_repository: TransactionRepository,
        insight_generator: InsightGenerator,
    ) -> None:
        self._account_repository = account_repository
        self._transaction_repository = transaction_repository
        self._insight_generator = insight_generator

    async def execute(self, query: GenerateInsightsQuery) -> FinancialSummary:
        transactions = await self._transaction_repository.list(user_id=query.user_id)
        accounts = await self._account_repository.list_all()
        names_by_id = {account.id: account.name for account in accounts}
        types_by_id = {account.id: account.type for account in accounts}
        month_start = date(query.month.year, query.month.month, 1)

        return self._insight_generator.generate_summary(
            transactions=transactions,
            month_start=month_start,
            account_names_by_id=names_by_id,
            account_types_by_id=types_by_id,
        )
