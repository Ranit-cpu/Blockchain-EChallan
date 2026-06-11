import uuid
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin
from app.core.enums import ChallanStatus, PaymentStatus, PaymentMethod, BlockchainTxStatus


class Violation(Base, TimestampMixin):
    __tablename__ = "violations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    fine_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    points_deducted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    challans: Mapped[list["Challan"]] = relationship("Challan", back_populates="violation")


class Challan(Base, TimestampMixin):
    __tablename__ = "challans"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    challan_number: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    vehicle_id: Mapped[str] = mapped_column(ForeignKey("vehicles.id"), nullable=False, index=True)
    officer_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    violation_id: Mapped[int] = mapped_column(ForeignKey("violations.id"), nullable=False)
    challan_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        Enum(ChallanStatus, name="challan_status_enum"),
        default=ChallanStatus.PENDING,
        nullable=False,
        index=True,
    )
    fine_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    location: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(11, 8), nullable=True)
    violation_datetime: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_disputed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dispute_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="challans")  # type: ignore[name-defined]
    officer: Mapped["User"] = relationship("User", back_populates="challans", foreign_keys=[officer_id])  # type: ignore[name-defined]
    violation: Mapped["Violation"] = relationship("Violation", back_populates="challans")
    evidence_files: Mapped[list["EvidenceFile"]] = relationship("EvidenceFile", back_populates="challan")
    blockchain_transactions: Mapped[list["BlockchainTransaction"]] = relationship(
        "BlockchainTransaction", back_populates="challan"
    )
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="challan")


class EvidenceFile(Base, TimestampMixin):
    __tablename__ = "evidence_files"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    challan_id: Mapped[str] = mapped_column(ForeignKey("challans.id"), nullable=False, index=True)
    ipfs_cid: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    ipfs_url: Mapped[str] = mapped_column(String(500), nullable=False)
    uploaded_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    challan: Mapped["Challan"] = relationship("Challan", back_populates="evidence_files")


class BlockchainTransaction(Base, TimestampMixin):
    __tablename__ = "blockchain_transactions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    challan_id: Mapped[str] = mapped_column(ForeignKey("challans.id"), nullable=False, index=True)
    tx_hash: Mapped[str] = mapped_column(String(66), unique=True, nullable=False, index=True)
    block_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    contract_address: Mapped[str] = mapped_column(String(42), nullable=False)
    challan_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(BlockchainTxStatus, name="blockchain_tx_status_enum"),
        default=BlockchainTxStatus.PENDING,
        nullable=False,
    )
    gas_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed_at: Mapped[str | None] = mapped_column(String(50), nullable=True)

    challan: Mapped["Challan"] = relationship("Challan", back_populates="blockchain_transactions")


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    challan_id: Mapped[str] = mapped_column(ForeignKey("challans.id"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(
        Enum(PaymentMethod, name="payment_method_enum"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum(PaymentStatus, name="payment_status_enum"),
        default=PaymentStatus.PENDING,
        nullable=False,
    )
    transaction_reference: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    payment_gateway: Mapped[str | None] = mapped_column(String(100), nullable=True)
    paid_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    paid_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    challan: Mapped["Challan"] = relationship("Challan", back_populates="payments")