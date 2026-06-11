from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    OFFICER = "officer"
    OWNER = "owner"


class ChallanStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(StrEnum):
    ONLINE = "online"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    UPI = "upi"


class BlockchainTxStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"


class VehicleType(StrEnum):
    TWO_WHEELER = "two_wheeler"
    THREE_WHEELER = "three_wheeler"
    FOUR_WHEELER = "four_wheeler"
    HEAVY_VEHICLE = "heavy_vehicle"
    BUS = "bus"
    TRUCK = "truck"


class AuditAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    PAYMENT = "payment"
    BLOCKCHAIN_RECORD = "blockchain_record"
    IPFS_UPLOAD = "ipfs_upload"