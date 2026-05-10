from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal


@dataclass(slots=True)
class Insight:
    message: str
    metric: str
    value: Decimal | int | float | str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
