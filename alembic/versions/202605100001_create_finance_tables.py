"""create finance tables

Revision ID: 202605100001
Revises:
Create Date: 2026-05-10 00:00:01.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "202605100001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("institution", sa.String(length=120), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "checking_account",
                "savings_account",
                "credit_card",
                name="accounttype",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "institution", "type", name="uq_accounts_identity"),
    )
    op.create_table(
        "transactions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("account_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=80), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("description_original", sa.String(length=300), nullable=False),
        sa.Column("description_normalized", sa.String(length=300), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "transaction_type",
            sa.Enum("debit", "credit", name="transactiontype", native_enum=False),
            nullable=False,
        ),
        sa.Column(
            "category",
            sa.Enum(
                "Alimentação",
                "Transporte",
                "Moradia",
                "Saúde",
                "Educação",
                "Mercado",
                "Assinaturas",
                "Lazer",
                "Transferência",
                "Outros",
                name="transactioncategory",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("source_file", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transactions_account_id"), "transactions", ["account_id"], unique=False)
    op.create_index(op.f("ix_transactions_date"), "transactions", ["date"], unique=False)
    op.create_index(
        op.f("ix_transactions_description_normalized"),
        "transactions",
        ["description_normalized"],
        unique=False,
    )
    op.create_index(op.f("ix_transactions_user_id"), "transactions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_transactions_user_id"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_description_normalized"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_date"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_account_id"), table_name="transactions")
    op.drop_table("transactions")
    op.drop_table("accounts")
