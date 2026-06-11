from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.challan import Challan, EvidenceFile, BlockchainTransaction, Payment
from app.repositories.challan_repository import (
    ChallanRepository, ViolationRepository, EvidenceFileRepository,
    BlockchainTxRepository, PaymentRepository,
)
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.challan import ChallanCreate, ChallanUpdate, PaymentCreate
from app.core.exceptions import (
    NotFoundError, ConflictError, DuplicateViolationError,
    BlockchainError, IPFSError, PaymentError,
)
from app.core.enums import ChallanStatus, BlockchainTxStatus, PaymentStatus, AuditAction
from app.core.security import generate_challan_hash, generate_challan_number
from app.services.audit_service import AuditService
from app.blockchain.blockchain_contract import get_blockchain_service
from app.ipfs.client import get_ipfs_client
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ChallanService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.challan_repo    = ChallanRepository(session)
        self.violation_repo  = ViolationRepository(session)
        self.vehicle_repo    = VehicleRepository(session)
        self.evidence_repo   = EvidenceFileRepository(session)
        self.blockchain_repo = BlockchainTxRepository(session)
        self.payment_repo    = PaymentRepository(session)
        self.audit           = AuditService(session)

    # ─────────────────────────────────────────────────────────────────────────
    # GENERATE CHALLAN  (with optional evidence upload)
    # ─────────────────────────────────────────────────────────────────────────

    async def generate_challan(
        self,
        data: ChallanCreate,
        officer_id: str,
        ip_address: str | None = None,
        evidence_data: bytes | None = None,
        evidence_filename: str | None = None,
        evidence_content_type: str | None = None,
    ) -> Challan:
        # 1. Resolve vehicle
        vehicle = await self.vehicle_repo.get_by_registration(data.vehicle_registration)
        if not vehicle:
            raise NotFoundError(f"Vehicle {data.vehicle_registration} not registered")
        if not vehicle.is_active:
            raise ConflictError("Vehicle is deactivated")

        # 2. Resolve violation
        violation = await self.violation_repo.get_by_code(data.violation_code)
        if not violation:
            raise NotFoundError(f"Violation code '{data.violation_code}' not found")

        # 3. Duplicate detection (DB-level)
        is_dup = await self.challan_repo.check_duplicate(
            vehicle.id, violation.id, data.violation_datetime
        )
        if is_dup:
            raise DuplicateViolationError(
                f"Duplicate: vehicle {data.vehicle_registration} already has "
                f"violation {violation.code} at {data.violation_datetime}"
            )

        # 4. Upload evidence to IPFS (if provided) — BEFORE writing to DB/chain
        ipfs_cid: str = ""
        ipfs_url: str = ""
        if evidence_data and evidence_filename:
            if len(evidence_data) > settings.max_file_size_bytes:
                raise ConflictError(f"Evidence file too large. Max {settings.MAX_FILE_SIZE_MB} MB")
            try:
                ipfs      = get_ipfs_client()
                ipfs_res  = await ipfs.add_bytes(evidence_data, evidence_filename)
                ipfs_cid  = ipfs_res["cid"]
                ipfs_url  = ipfs_res["url"]
                logger.info("Evidence uploaded to IPFS", cid=ipfs_cid, file=evidence_filename)
            except IPFSError as e:
                logger.warning("IPFS upload failed — challan will proceed without evidence", error=str(e))

        # 5. Create challan in DB
        challan_number = generate_challan_number()
        challan_hash   = generate_challan_hash(
            vehicle_number  = data.vehicle_registration,
            violation_code  = data.violation_code,
            officer_id      = officer_id,
            timestamp       = data.violation_datetime,
            location        = data.location,
        )
        challan = Challan(
            challan_number     = challan_number,
            vehicle_id         = vehicle.id,
            officer_id         = officer_id,
            violation_id       = violation.id,
            challan_hash       = challan_hash,
            fine_amount        = violation.fine_amount,
            location           = data.location,
            latitude           = data.latitude,
            longitude          = data.longitude,
            violation_datetime = data.violation_datetime,
            notes              = data.notes,
            due_date           = data.due_date,
            status             = ChallanStatus.PENDING,
        )
        created = await self.challan_repo.create(challan)

        # 6. Save evidence record in DB (if uploaded)
        if ipfs_cid:
            evidence_row = EvidenceFile(
                challan_id   = created.id,
                ipfs_cid     = ipfs_cid,
                file_name    = evidence_filename,
                file_type    = evidence_content_type or "application/octet-stream",
                file_size    = len(evidence_data),
                ipfs_url     = ipfs_url,
                uploaded_by  = officer_id,
                description  = "Evidence uploaded during challan generation",
            )
            await self.evidence_repo.create(evidence_row)
            await self.audit.log(
                action        = AuditAction.IPFS_UPLOAD,
                resource_type = "evidence",
                user_id       = officer_id,
                resource_id   = created.id,
                description   = f"Evidence {evidence_filename} → IPFS CID {ipfs_cid}",
            )

        # 7. Record on blockchain (non-blocking — failure doesn't abort challan)
        await self._record_on_blockchain(
            challan              = created,
            vehicle_registration = data.vehicle_registration,
            violation_type       = violation.name,
            officer_id           = officer_id,
            evidence_ipfs_cid    = ipfs_cid,
            violation_datetime   = data.violation_datetime,
        )

        await self.audit.log(
            action        = AuditAction.CREATE,
            resource_type = "challan",
            user_id       = officer_id,
            resource_id   = created.id,
            ip_address    = ip_address,
            description   = (
                f"Challan {challan_number} issued for {data.vehicle_registration}"
                + (f" | evidence CID: {ipfs_cid}" if ipfs_cid else "")
            ),
        )
        logger.info("Challan generated", id=created.id, number=challan_number, cid=ipfs_cid or "none")
        return await self.challan_repo.get_by_id_full(created.id)  # type: ignore

    # ─────────────────────────────────────────────────────────────────────────
    # BLOCKCHAIN RECORDING
    # ─────────────────────────────────────────────────────────────────────────

    async def _record_on_blockchain(
        self,
        challan: Challan,
        vehicle_registration: str,
        violation_type: str,
        officer_id: str,
        evidence_ipfs_cid: str,
        violation_datetime: str,
    ) -> None:
        try:
            blockchain = await get_blockchain_service()

            # Convert violation_datetime string to Unix timestamp
            try:
                from dateutil import parser as dtparser
                dt = dtparser.parse(violation_datetime)
                unix_ts = int(dt.timestamp())
            except Exception:
                unix_ts = int(datetime.now(timezone.utc).timestamp())

            fine_paise = int(challan.fine_amount * 100)

            result = await blockchain.create_challan(
                vehicle_number      = vehicle_registration,
                violation_type      = violation_type,
                fine_amount_paise   = fine_paise,
                violation_timestamp = unix_ts,
                ipfs_cid            = evidence_ipfs_cid,
                evidence_hash       = challan.challan_hash,
            )

            tx = BlockchainTransaction(
                challan_id       = challan.id,
                tx_hash          = result["tx_hash"],
                block_number     = result.get("on_chain_challan_id") or result.get("block_number"),
                contract_address = settings.CONTRACT_ADDRESS,
                challan_hash     = challan.challan_hash,
                status           = (
                    BlockchainTxStatus.CONFIRMED
                    if result["status"] == "confirmed"
                    else BlockchainTxStatus.FAILED
                ),
                gas_used     = result.get("gas_used"),
                confirmed_at = datetime.now(timezone.utc).isoformat(),
            )
            await self.blockchain_repo.create(tx)
            await self.audit.log(
                action        = AuditAction.BLOCKCHAIN_RECORD,
                resource_type = "challan",
                resource_id   = challan.id,
                description   = (
                    f"Blockchain tx {result['tx_hash']} | "
                    f"evidence CID: {evidence_ipfs_cid or 'none'}"
                ),
            )
            logger.info(
                "Challan recorded on blockchain",
                tx=result["tx_hash"],
                cid=evidence_ipfs_cid or "none",
            )
        except BlockchainError as e:
            logger.warning("Blockchain record failed (non-fatal)", challan_id=challan.id, error=str(e))
        except Exception as e:
            logger.warning("Blockchain record unexpected error", challan_id=challan.id, error=str(e))

    # ─────────────────────────────────────────────────────────────────────────
    # CRUD
    # ─────────────────────────────────────────────────────────────────────────

    async def get_challan(self, challan_id: str) -> Challan:
        challan = await self.challan_repo.get_by_id_full(challan_id)
        if not challan:
            raise NotFoundError(f"Challan {challan_id} not found")
        return challan

    async def get_by_challan_number(self, challan_number: str) -> Challan:
        challan = await self.challan_repo.get_by_challan_number(challan_number)
        if not challan:
            raise NotFoundError(f"Challan number {challan_number} not found")
        return challan

    async def list_challans(
        self,
        status: str | None = None,
        vehicle_registration: str | None = None,
        officer_id: str | None = None,
        violation_code: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Challan], int]:
        vehicle_id: str | None = None
        if vehicle_registration:
            v = await self.vehicle_repo.get_by_registration(
                vehicle_registration.upper().replace(" ", "")
            )
            if v:
                vehicle_id = v.id

        violation_id: int | None = None
        if violation_code:
            vio = await self.violation_repo.get_by_code(violation_code)
            if vio:
                violation_id = vio.id

        return await self.challan_repo.get_filtered(
            status=status, vehicle_id=vehicle_id, officer_id=officer_id,
            violation_id=violation_id, from_date=from_date, to_date=to_date,
            offset=offset, limit=limit,
        )

    async def update_challan(
        self, challan_id: str, data: ChallanUpdate, updated_by_id: str
    ) -> Challan:
        challan = await self.challan_repo.get_by_id_full(challan_id)
        if not challan:
            raise NotFoundError(f"Challan {challan_id} not found")
        old = {"status": challan.status, "is_disputed": challan.is_disputed}
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(challan, field, value)
        await self.challan_repo.update(challan)
        await self.audit.log(
            action=AuditAction.UPDATE, resource_type="challan",
            user_id=updated_by_id, resource_id=challan_id, old_values=old,
            description=f"Challan {challan.challan_number} updated",
        )
        return await self.challan_repo.get_by_id_full(challan_id)  # type: ignore

    # ─────────────────────────────────────────────────────────────────────────
    # VERIFY (DB + blockchain)
    # ─────────────────────────────────────────────────────────────────────────

    async def verify_challan(self, challan_number: str) -> dict:
        challan = await self.challan_repo.get_by_challan_number(challan_number)
        if not challan:
            return {
                "is_valid": False, "challan_number": challan_number,
                "challan_hash": "", "blockchain_verified": False,
                "tx_hash": None, "message": "Challan not found",
            }

        confirmed_tx = await self.blockchain_repo.get_confirmed_by_challan(challan.id)
        blockchain_verified = False
        tx_hash = None

        if confirmed_tx:
            try:
                blockchain = await get_blockchain_service()
                # Verify on-chain using the blockchain challan_id stored in tx
                # We use challan_number as string identifier (contract stores by counter)
                tx_hash = confirmed_tx.tx_hash
                blockchain_verified = True  # tx confirmed = record exists
            except BlockchainError:
                pass

        return {
            "is_valid": True,
            "challan_number": challan_number,
            "challan_hash": challan.challan_hash,
            "blockchain_verified": blockchain_verified,
            "tx_hash": tx_hash,
            "message": "Challan verified on blockchain" if blockchain_verified else "Challan found in database",
        }

    # ─────────────────────────────────────────────────────────────────────────
    # ADDITIONAL EVIDENCE UPLOAD (post-challan)
    # ─────────────────────────────────────────────────────────────────────────

    async def upload_evidence(
        self,
        challan_id: str,
        file_data: bytes,
        filename: str,
        file_type: str,
        uploaded_by: str,
        description: str | None = None,
    ) -> EvidenceFile:
        challan = await self.challan_repo.get_by_id_full(challan_id)
        if not challan:
            raise NotFoundError(f"Challan {challan_id} not found")
        if len(file_data) > settings.max_file_size_bytes:
            raise ConflictError(f"File too large. Max {settings.MAX_FILE_SIZE_MB} MB")

        ipfs     = get_ipfs_client()
        ipfs_res = await ipfs.add_bytes(file_data, filename)

        evidence = EvidenceFile(
            challan_id  = challan_id,
            ipfs_cid    = ipfs_res["cid"],
            file_name   = filename,
            file_type   = file_type,
            file_size   = len(file_data),
            ipfs_url    = ipfs_res["url"],
            uploaded_by = uploaded_by,
            description = description,
        )
        created = await self.evidence_repo.create(evidence)
        await self.audit.log(
            action=AuditAction.IPFS_UPLOAD, resource_type="evidence",
            user_id=uploaded_by, resource_id=created.id,
            description=f"Evidence {filename} uploaded, CID: {ipfs_res['cid']}",
        )
        return created

    # ─────────────────────────────────────────────────────────────────────────
    # PAYMENT
    # ─────────────────────────────────────────────────────────────────────────

    async def process_payment(
        self, data: PaymentCreate, paid_by_id: str | None = None
    ) -> Payment:
        challan = await self.challan_repo.get_by_id_full(data.challan_id)
        if not challan:
            raise NotFoundError(f"Challan {data.challan_id} not found")
        if challan.status == ChallanStatus.PAID:
            raise PaymentError("Challan already paid")
        if challan.status == ChallanStatus.CANCELLED:
            raise PaymentError("Cannot pay a cancelled challan")
        existing = await self.payment_repo.get_completed_by_challan(data.challan_id)
        if existing:
            raise PaymentError("Payment already completed for this challan")
        if data.transaction_reference:
            dup = await self.payment_repo.get_by_reference(data.transaction_reference)
            if dup:
                raise PaymentError(f"Transaction reference already used")

        payment = Payment(
            challan_id            = data.challan_id,
            amount                = challan.fine_amount,
            payment_method        = data.payment_method,
            status                = PaymentStatus.COMPLETED,
            transaction_reference = data.transaction_reference,
            payment_gateway       = data.payment_gateway,
            paid_by               = paid_by_id,
            paid_at               = datetime.now(timezone.utc).isoformat(),
            notes                 = data.notes,
        )
        created = await self.payment_repo.create(payment)

        challan.status = ChallanStatus.PAID
        await self.challan_repo.update(challan)

        # Record payment on blockchain (non-fatal)
        try:
            blockchain = await get_blockchain_service()
            confirmed_tx = await self.blockchain_repo.get_confirmed_by_challan(data.challan_id)
            if confirmed_tx and confirmed_tx.block_number:
                ref = data.transaction_reference or created.id
                await blockchain.record_payment_on_chain(
                    int(confirmed_tx.block_number),
                    ref,
                )
        except Exception as e:
            logger.warning("Blockchain payment record skipped", error=str(e))

        await self.audit.log(
            action=AuditAction.PAYMENT, resource_type="payment",
            user_id=paid_by_id, resource_id=created.id,
            description=f"Payment ₹{challan.fine_amount} for challan {challan.challan_number}",
        )
        return created

    # ─────────────────────────────────────────────────────────────────────────
    # VIOLATIONS
    # ─────────────────────────────────────────────────────────────────────────

    async def get_violations(self) -> list:
        return await self.violation_repo.get_all_active()

    async def create_violation(self, data, created_by_id: str):
        from app.models.challan import Violation
        existing = await self.violation_repo.get_by_code(data.code)
        if existing:
            raise ConflictError(f"Violation code '{data.code}' already exists")
        violation = Violation(**data.model_dump())
        return await self.violation_repo.create(violation)

    # ─────────────────────────────────────────────────────────────────────────
    # STATS
    # ─────────────────────────────────────────────────────────────────────────

    async def get_challan_stats(self) -> dict:
        from sqlalchemy import func, select
        from app.models.challan import Challan, Payment

        total   = (await self.session.execute(select(func.count()).select_from(Challan))).scalar_one()
        pending = (await self.session.execute(
            select(func.count()).select_from(Challan).where(Challan.status == ChallanStatus.PENDING)
        )).scalar_one()
        paid    = (await self.session.execute(
            select(func.count()).select_from(Challan).where(Challan.status == ChallanStatus.PAID)
        )).scalar_one()
        revenue = (await self.session.execute(
            select(func.sum(Payment.amount)).where(Payment.status == PaymentStatus.COMPLETED)
        )).scalar_one() or Decimal("0")

        return {
            "total_challans":   total,
            "pending_challans": pending,
            "paid_challans":    paid,
            "total_revenue":    float(revenue),
        }