import re
import unicodedata
from typing import Protocol

from app.domain.entities.transaction import TransactionCategory


class TransactionClassifier(Protocol):
    def classify(self, description_normalized: str) -> TransactionCategory:
        raise NotImplementedError


class KeywordTransactionClassifier:
    def __init__(self) -> None:
        self._rules: dict[TransactionCategory, tuple[str, ...]] = {
            TransactionCategory.FOOD: ("ifood", "restaurante", "lanche", "padaria", "cafe"),
            TransactionCategory.TRANSPORT: ("uber", "99", "taxi", "posto", "combustivel"),
            TransactionCategory.HOUSING: ("aluguel", "condominio", "energia", "agua", "internet"),
            TransactionCategory.HEALTH: ("farmacia", "hospital", "clinica", "medico", "plano de saude"),
            TransactionCategory.EDUCATION: ("faculdade", "curso", "escola", "livro", "udemy"),
            TransactionCategory.GROCERIES: ("supermercado", "mercado", "hortifruti", "atacadao"),
            TransactionCategory.SUBSCRIPTIONS: ("netflix", "spotify", "prime", "amazon prime", "disney"),
            TransactionCategory.LEISURE: ("cinema", "bar", "show", "viagem", "hotel"),
            TransactionCategory.TRANSFER: ("pix", "ted", "doc", "transferencia", "resgate"),
        }

    def classify(self, description_normalized: str) -> TransactionCategory:
        for category, keywords in self._rules.items():
            if any(keyword in description_normalized for keyword in keywords):
                return category
        return TransactionCategory.OTHER


def normalize_description(description: str) -> str:
    normalized = unicodedata.normalize("NFKD", description.strip().lower())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = re.sub(r"[^a-z0-9\s]", " ", ascii_text)
    return re.sub(r"\s+", " ", ascii_text).strip()
