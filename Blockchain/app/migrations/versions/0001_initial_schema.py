"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("badge_number", sa.String(50), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_login_at", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("badge_number"),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "vehicle_owners",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("license_number", sa.String(50), nullable=False),
        sa.Column("license_expiry", sa.String(20), nullable=True),
        sa.Column("id_proof_type", sa.String(50), nullable=True),
        sa.Column("id_proof_number", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("license_number"),
    )
    op.create_index("ix_vehicle_owners_license_number", "vehicle_owners", ["license_number"])

    op.create_table(
        "vehicles",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("registration_number", sa.String(20), nullable=False),
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("vehicle_type", sa.Enum("two_wheeler", "three_wheeler", "four_wheeler", "heavy_vehicle", "bus", "truck", name="vehicle_type_enum"), nullable=False),
        sa.Column("make", sa.String(100), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(50), nullable=False),
        sa.Column("engine_number", sa.String(100), nullable=False),
        sa.Column("chassis_number", sa.String(100), nullable=False),
        sa.Column("fuel_type", sa.String(30), nullable=False),
        sa.Column("insurance_valid_till", sa.String(20), nullable=True),
        sa.Column("puc_valid_till", sa.String(20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["vehicle_owners.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("registration_number"),
        sa.UniqueConstraint("engine_number"),
        sa.UniqueConstraint("chassis_number"),
    )
    op.create_index("ix_vehicles_registration_number", "vehicles", ["registration_number"])

    op.create_table(
        "violations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("fine_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("points_deducted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_violations_code", "violations", ["code"])

    op.create_table(
        "challans",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("challan_number", sa.String(30), nullable=False),
        sa.Column("vehicle_id", sa.String(36), nullable=False),
        sa.Column("officer_id", sa.String(36), nullable=False),
        sa.Column("violation_id", sa.Integer(), nullable=False),
        sa.Column("challan_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.Enum("pending", "paid", "disputed", "cancelled", "overdue", name="challan_status_enum"), nullable=False, server_default="pending"),
        sa.Column("fine_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("location", sa.String(500), nullable=False),
        sa.Column("latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column("violation_datetime", sa.String(50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("due_date", sa.String(20), nullable=True),
        sa.Column("is_disputed", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("dispute_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.ForeignKeyConstraint(["officer_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["violation_id"], ["violations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("challan_number"),
        sa.UniqueConstraint("challan_hash"),
    )
    op.create_index("ix_challans_challan_number", "challans", ["challan_number"])
    op.create_index("ix_challans_vehicle_id", "challans", ["vehicle_id"])
    op.create_index("ix_challans_status", "challans", ["status"])

    op.create_table(
        "evidence_files",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("challan_id", sa.String(36), nullable=False),
        sa.Column("ipfs_cid", sa.String(100), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(50), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("ipfs_url", sa.String(500), nullable=False),
        sa.Column("uploaded_by", sa.String(36), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["challan_id"], ["challans.id"]),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ipfs_cid"),
    )

    op.create_table(
        "blockchain_transactions",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("challan_id", sa.String(36), nullable=False),
        sa.Column("tx_hash", sa.String(66), nullable=False),
        sa.Column("block_number", sa.Integer(), nullable=True),
        sa.Column("contract_address", sa.String(42), nullable=False),
        sa.Column("challan_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.Enum("pending", "confirmed", "failed", name="blockchain_tx_status_enum"), nullable=False, server_default="pending"),
        sa.Column("gas_used", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("confirmed_at", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["challan_id"], ["challans.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tx_hash"),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("challan_id", sa.String(36), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_method", sa.Enum("online", "bank_transfer", "cash", "upi", name="payment_method_enum"), nullable=False),
        sa.Column("status", sa.Enum("pending", "completed", "failed", "refunded", name="payment_status_enum"), nullable=False, server_default="pending"),
        sa.Column("transaction_reference", sa.String(255), nullable=True),
        sa.Column("payment_gateway", sa.String(100), nullable=True),
        sa.Column("paid_by", sa.String(36), nullable=True),
        sa.Column("paid_at", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["challan_id"], ["challans.id"]),
        sa.ForeignKeyConstraint(["paid_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_reference"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("action", sa.Enum("create", "update", "delete", "login", "logout", "payment", "blockchain_record", "ipfs_upload", name="audit_action_enum"), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(36), nullable=True),
        sa.Column("old_values", sa.Text(), nullable=True),
        sa.Column("new_values", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_resource_type", "audit_logs", ["resource_type"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("payments")
    op.drop_table("blockchain_transactions")
    op.drop_table("evidence_files")
    op.drop_table("challans")
    op.drop_table("violations")
    op.drop_table("vehicles")
    op.drop_table("vehicle_owners")
    op.drop_table("users")
    op.drop_table("roles")
    for enum in ["vehicle_type_enum", "challan_status_enum", "payment_method_enum",
                 "payment_status_enum", "blockchain_tx_status_enum", "audit_action_enum"]:
        sa.Enum(name=enum).drop(op.get_bind(), checkfirst=True)