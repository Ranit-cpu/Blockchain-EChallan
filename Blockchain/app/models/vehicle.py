import uuid
from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin
from app.core.enums import VehicleType


class VehicleOwner(Base, TimestampMixin):
    __tablename__ = "vehicle_owners"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True, index=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    license_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    license_expiry: Mapped[str | None] = mapped_column(String(20), nullable=True)
    id_proof_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    id_proof_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    vehicles: Mapped[list["Vehicle"]] = relationship("Vehicle", back_populates="owner")


class Vehicle(Base, TimestampMixin):
    __tablename__ = "vehicles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    registration_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    owner_id: Mapped[str] = mapped_column(ForeignKey("vehicle_owners.id"), nullable=False)
    vehicle_type: Mapped[str] = mapped_column(
        Enum(VehicleType, name="vehicle_type_enum"), nullable=False
    )
    make: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    engine_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    chassis_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    fuel_type: Mapped[str] = mapped_column(String(30), nullable=False)
    insurance_valid_till: Mapped[str | None] = mapped_column(String(20), nullable=True)
    puc_valid_till: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    owner: Mapped["VehicleOwner"] = relationship("VehicleOwner", back_populates="vehicles")
    challans: Mapped[list["Challan"]] = relationship("Challan", back_populates="vehicle")  # type: ignore[name-defined]