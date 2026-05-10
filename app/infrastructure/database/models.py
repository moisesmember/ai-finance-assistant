from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.account import AccountType
from app.domain.entities.transaction import TransactionCategory, TransactionType
from app.infrastructure.database.base import Base


def enum_values(enum_class: type) -> list[str]:
    return [item.value for item in enum_class]


class AccountModel(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("name", "institution", "type", name="uq_accounts_identity"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    institution: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[AccountType] = mapped_column(
        Enum(AccountType, values_callable=enum_values, native_enum=False),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    transactions: Mapped[list["TransactionModel"]] = relationship(back_populates="account")


class TransactionModel(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    account_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    description_original: Mapped[str] = mapped_column(String(300), nullable=False)
    description_normalized: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, values_callable=enum_values, native_enum=False),
        nullable=False,
    )
    category: Mapped[TransactionCategory] = mapped_column(
        Enum(TransactionCategory, values_callable=enum_values, native_enum=False),
        nullable=False,
    )
    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    account: Mapped[AccountModel] = relationship(back_populates="transactions")
