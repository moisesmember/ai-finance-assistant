from app.domain.entities.transaction import TransactionCategory
from app.domain.services.transaction_classifier import (
    KeywordTransactionClassifier,
    normalize_description,
)


def test_keyword_classifier_maps_known_descriptions() -> None:
    classifier = KeywordTransactionClassifier()

    assert classifier.classify(normalize_description("IFood Restaurante")) == TransactionCategory.FOOD
    assert classifier.classify(normalize_description("Uber Trip")) == TransactionCategory.TRANSPORT
    assert classifier.classify(normalize_description("Spotify Premium")) == TransactionCategory.SUBSCRIPTIONS
    assert classifier.classify(normalize_description("Supermercado Central")) == TransactionCategory.GROCERIES


def test_keyword_classifier_falls_back_to_other() -> None:
    classifier = KeywordTransactionClassifier()

    assert classifier.classify(normalize_description("Compra desconhecida")) == TransactionCategory.OTHER
