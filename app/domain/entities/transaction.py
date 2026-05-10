from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import StrEnum
from uuid import uuid4


class TransactionType(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"


class TransactionCategory(StrEnum):
    FOOD = "Alimentação"
    TRANSPORT = "Transporte"
    HOUSING = "Moradia"
    HEALTH = "Saúde"
    EDUCATION = "Educação"
    GROCERIES = "Mercado"
    SUBSCRIPTIONS = "Assinaturas"
    LEISURE = "Lazer"
    TRANSFER = "Transferência"
    OTHER = "Outros"


@dataclass(slots=True)
class Transaction:
    account_id: str
    user_id: str
    date: date
    description_original: str
    description_normalized: str
    amount: Decimal
    transaction_type: TransactionType
    category: TransactionCategory
    source_file: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
