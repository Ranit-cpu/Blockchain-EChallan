import hashlib
import secrets
import uuid
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_session_id() -> str:
    return secrets.token_urlsafe(32)


def generate_challan_hash(
    vehicle_number: str,
    violation_code: str,
    officer_id: str,
    timestamp: str,
    location: str,
) -> str:
    data = f"{vehicle_number}:{violation_code}:{officer_id}:{timestamp}:{location}"
    return hashlib.sha256(data.encode()).hexdigest()


def generate_transaction_id() -> str:
    return str(uuid.uuid4()).replace("-", "").upper()


def generate_challan_number() -> str:
    prefix = "CH"
    unique = secrets.token_hex(6).upper()
    return f"{prefix}{unique}"