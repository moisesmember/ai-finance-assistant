from decimal import Decimal

import pytest

from app.application.use_cases.import_transactions import ImportTransactionsUseCase
from app.domain.entities.account import AccountType
from app.domain.entities.transaction import TransactionCategory, TransactionType
from app.domain.services.transaction_classifier import KeywordTransactionClassifier
from tests.fakes import InMemoryAccountRepository, InMemoryTransactionRepository


@pytest.mark.asyncio
async def test_import_transactions_creates_accounts_and_classifies_rows() -> None:
    csv_content = (
        "date,description,amount,account_name,institution,account_type\n"
        "2026-05-01,Salario Empresa,5000.00,Santander Conta,Santander,checking_account\n"
        "2026-05-02,Ifood Restaurante,-75.50,Nubank Cartao,Nubank,credit_card\n"
        "2026-05-03,Uber Trip,-31.20,Nubank Cartao,Nubank,credit_card\n"
    ).encode()
    account_repository = InMemoryAccountRepository()
    transaction_repository = InMemoryTransactionRepository()
    use_case = ImportTransactionsUseCase(
        account_repository=account_repository,
        transaction_repository=transaction_repository,
        classifier=KeywordTransactionClassifier(),
    )

    result = await use_case.execute(
        csv_content=csv_content,
        source_file="sample.csv",
        user_id="user-1",
    )

    assert result.imported_count == 3
    assert result.created_accounts_count == 2
    assert len(account_repository.accounts) == 2
    assert account_repository.accounts[1].type == AccountType.CREDIT_CARD
    assert transaction_repository.transactions[0].transaction_type == TransactionType.CREDIT
    assert transaction_repository.transactions[1].amount == Decimal("75.50")
    assert transaction_repository.transactions[1].category == TransactionCategory.FOOD
    assert transaction_repository.transactions[2].category == TransactionCategory.TRANSPORT


@pytest.mark.asyncio
async def test_import_transactions_rejects_missing_columns() -> None:
    use_case = ImportTransactionsUseCase(
        account_repository=InMemoryAccountRepository(),
        transaction_repository=InMemoryTransactionRepository(),
        classifier=KeywordTransactionClassifier(),
    )

    with pytest.raises(ValueError, match="CSV sem colunas obrigatorias"):
        await use_case.execute(
            csv_content=b"date,description,amount\n2026-05-01,Teste,-10",
            source_file="bad.csv",
            user_id="user-1",
        )
