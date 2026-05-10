from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4


class AccountType(StrEnum):
    CHECKING_ACCOUNT = "checking_account"
    SAVINGS_ACCOUNT = "savings_account"
    CREDIT_CARD = "credit_card"


@dataclass(slots=True)
class Account:
    name: str
    institution: str
    type: AccountType
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
