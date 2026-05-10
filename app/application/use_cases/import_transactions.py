from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from io import BytesIO
from typing import Any

import pandas as pd

from app.domain.entities.account import Account, AccountType
from app.domain.entities.transaction import Transaction, TransactionType
from app.domain.repositories.account_repository import AccountRepository
from app.domain.repositories.transaction_repository import TransactionRepository
from app.domain.services.transaction_classifier import TransactionClassifier, normalize_description


REQUIRED_COLUMNS = {
    "date",
    "description",
    "amount",
    "account_name",
    "institution",
    "account_type",
}


@dataclass(slots=True)
class ImportTransactionsResult:
    imported_count: int
    created_accounts_count: int
    source_file: str | None


class ImportTransactionsUseCase:
    def __init__(
        self,
        *,
        account_repository: AccountRepository,
        transaction_repository: TransactionRepository,
        classifier: TransactionClassifier,
    ) -> None:
        self._account_repository = account_repository
        self._transaction_repository = transaction_repository
        self._classifier = classifier

    async def execute(
        self,
        *,
        csv_content: bytes,
        source_file: str | None,
        user_id: str,
    ) -> ImportTransactionsResult:
        frame = pd.read_csv(BytesIO(csv_content))
        frame.columns = [str(column).strip() for column in frame.columns]
        self._validate_columns(frame)

        account_cache: dict[tuple[str, str, AccountType], Account] = {}
        transactions: list[Transaction] = []
        created_accounts = 0

        for _, row in frame.iterrows():
            account_type = parse_account_type(row["account_type"])
            account_key = (
                str(row["account_name"]).strip(),
                str(row["institution"]).strip(),
                account_type,
            )
            account = account_cache.get(account_key)
            if account is None:
                account = await self._account_repository.get_by_identity(
                    name=account_key[0],
                    institution=account_key[1],
                    account_type=account_key[2],
                )
                if account is None:
                    account = await self._account_repository.add(
                        Account(
                            name=account_key[0],
                            institution=account_key[1],
                            type=account_key[2],
                        )
                    )
                    created_accounts += 1
                account_cache[account_key] = account

            raw_amount = parse_decimal(row["amount"])
            transaction_type = (
                TransactionType.DEBIT if raw_amount < Decimal("0") else TransactionType.CREDIT
            )
            description_original = str(row["description"]).strip()
            description_normalized = normalize_description(description_original)
            category = self._classifier.classify(description_normalized)

            transactions.append(
                Transaction(
                    account_id=account.id,
                    user_id=user_id,
                    date=parse_date(row["date"]),
                    description_original=description_original,
                    description_normalized=description_normalized,
                    amount=abs(raw_amount),
                    transaction_type=transaction_type,
                    category=category,
                    source_file=source_file,
                )
            )

        await self._transaction_repository.add_many(transactions)
        return ImportTransactionsResult(
            imported_count=len(transactions),
            created_accounts_count=created_accounts,
            source_file=source_file,
        )

    def _validate_columns(self, frame: pd.DataFrame) -> None:
        missing_columns = REQUIRED_COLUMNS.difference(frame.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"CSV sem colunas obrigatorias: {missing}")


def parse_decimal(value: Any) -> Decimal:
    normalized = str(value).strip().replace("R$", "").replace(" ", "")
    if "," in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    try:
        return Decimal(normalized)
    except InvalidOperation as exc:
        raise ValueError(f"Valor monetario invalido: {value}") from exc


def parse_account_type(value: Any) -> AccountType:
    try:
        return AccountType(str(value).strip())
    except ValueError as exc:
        accepted = ", ".join(account_type.value for account_type in AccountType)
        raise ValueError(f"Tipo de conta invalido: {value}. Use um de: {accepted}") from exc


def parse_date(value: Any) -> date:
    parsed = pd.to_datetime(value, dayfirst=False, errors="coerce")
    if pd.isna(parsed):
        raise ValueError(f"Data invalida: {value}")
    return parsed.date()
