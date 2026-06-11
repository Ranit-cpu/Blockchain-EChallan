from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.schemas.challan import (
    ChallanUpdate, ChallanResponse, ChallanVerifyResponse,
    PaymentCreate, PaymentResponse, ViolationCreate, ViolationResponse,
)
from app.schemas.common import APIResponse, PaginatedResponse, MessageResponse
from app.services.challan_service import ChallanService
from app.middleware.auth import get_current_user, get_admin_user, get_officer_or_admin
from app.core.enums import ChallanStatus
from app.models.user import User

router = APIRouter(prefix="/challans", tags=["Challans"])


# ── Violations ────────────────────────────────────────────────────────────────

@router.post("/violations", response_model=APIResponse[ViolationResponse], status_code=201)
async def create_violation(
    data: ViolationCreate,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_admin_user),
) -> APIResponse[ViolationResponse]:
    service = ChallanService(db)
    v = await service.create_violation(data, created_by_id=admin.id)
    return APIResponse(message="Violation created", data=ViolationResponse.model_validate(v))


@router.get("/violations", response_model=APIResponse[list[ViolationResponse]])
async def list_violations(
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> APIResponse[list[ViolationResponse]]:
    service = ChallanService(db)
    violations = await service.get_violations()
    return APIResponse(data=[ViolationResponse.model_validate(v) for v in violations])


# ── Generate challan (multipart: fields + optional evidence file) ─────────────

@router.post("", response_model=APIResponse[ChallanResponse], status_code=201)
async def generate_challan(
    request: Request,
    # --- required fields ---
    vehicle_registration: Annotated[str, Form()],
    violation_code:       Annotated[str, Form()],
    location:             Annotated[str, Form()],
    violation_datetime:   Annotated[str, Form()],
    # --- optional fields ---
    latitude:   Annotated[float | None, Form()] = None,
    longitude:  Annotated[float | None, Form()] = None,
    notes:      Annotated[str | None,   Form()] = None,
    due_date:   Annotated[str | None,   Form()] = None,
    # --- optional evidence file ---
    evidence:   UploadFile | None = File(default=None),
    db:         AsyncSession = Depends(get_db_session),
    officer:    User = Depends(get_officer_or_admin),
) -> APIResponse[ChallanResponse]:
    """
    Issue a challan.
    Send as **multipart/form-data** — include `evidence` file (image/video) to
    have it uploaded to IPFS and the CID recorded on the blockchain automatically.
    """
    ip = request.client.host if request.client else None

    # Read evidence bytes if provided
    evidence_data: bytes | None = None
    evidence_filename: str | None = None
    evidence_content_type: str | None = None
    if evidence and evidence.filename:
        evidence_data         = await evidence.read()
        evidence_filename     = evidence.filename
        evidence_content_type = evidence.content_type or "application/octet-stream"

    # Build schema object for validation
    from app.schemas.challan import ChallanCreate
    challan_data = ChallanCreate(
        vehicle_registration = vehicle_registration,
        violation_code       = violation_code,
        location             = location,
        violation_datetime   = violation_datetime,
        latitude             = latitude,
        longitude            = longitude,
        notes                = notes,
        due_date             = due_date,
    )

    service = ChallanService(db)
    challan = await service.generate_challan(
        data                   = challan_data,
        officer_id             = officer.id,
        ip_address             = ip,
        evidence_data          = evidence_data,
        evidence_filename      = evidence_filename,
        evidence_content_type  = evidence_content_type,
    )
    return APIResponse(
        message = (
            "Challan issued with evidence on IPFS"
            if evidence_data else "Challan issued"
        ),
        data = ChallanResponse.model_validate(challan),
    )


# ── List / filter ─────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedResponse[ChallanResponse])
async def list_challans(
    status:               ChallanStatus | None = Query(default=None),
    vehicle_registration: str | None           = Query(default=None),
    officer_id:           str | None           = Query(default=None),
    violation_code:       str | None           = Query(default=None),
    from_date:            str | None           = Query(default=None),
    to_date:              str | None           = Query(default=None),
    page:                 int                  = Query(default=1, ge=1),
    page_size:            int                  = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[ChallanResponse]:
    service = ChallanService(db)
    offset = (page - 1) * page_size
    eff_officer_id = officer_id
    if current_user.role.name == "officer":
        eff_officer_id = current_user.id
    challans, total = await service.list_challans(
        status               = status.value if status else None,
        vehicle_registration = vehicle_registration,
        officer_id           = eff_officer_id,
        violation_code       = violation_code,
        from_date            = from_date,
        to_date              = to_date,
        offset               = offset,
        limit                = page_size,
    )
    return PaginatedResponse.create(
        items     = [ChallanResponse.model_validate(c) for c in challans],
        total     = total,
        page      = page,
        page_size = page_size,
    )


@router.get("/stats", response_model=APIResponse[dict])
async def get_stats(
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_admin_user),
) -> APIResponse[dict]:
    service = ChallanService(db)
    return APIResponse(data=await service.get_challan_stats())


@router.get("/verify/{challan_number}", response_model=APIResponse[ChallanVerifyResponse])
async def verify_challan(
    challan_number: str,
    db: AsyncSession = Depends(get_db_session),
) -> APIResponse[ChallanVerifyResponse]:
    """Public endpoint — no authentication required."""
    service = ChallanService(db)
    result  = await service.verify_challan(challan_number)
    return APIResponse(data=ChallanVerifyResponse(**result))


@router.get("/number/{challan_number}", response_model=APIResponse[ChallanResponse])
async def get_by_number(
    challan_number: str,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> APIResponse[ChallanResponse]:
    service = ChallanService(db)
    challan = await service.get_by_challan_number(challan_number)
    return APIResponse(data=ChallanResponse.model_validate(challan))


@router.get("/{challan_id}", response_model=APIResponse[ChallanResponse])
async def get_challan(
    challan_id: str,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> APIResponse[ChallanResponse]:
    service = ChallanService(db)
    challan = await service.get_challan(challan_id)
    return APIResponse(data=ChallanResponse.model_validate(challan))


@router.patch("/{challan_id}", response_model=APIResponse[ChallanResponse])
async def update_challan(
    challan_id: str,
    data: ChallanUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_officer_or_admin),
) -> APIResponse[ChallanResponse]:
    service = ChallanService(db)
    challan = await service.update_challan(challan_id, data, updated_by_id=current_user.id)
    return APIResponse(message="Challan updated", data=ChallanResponse.model_validate(challan))


# ── Additional evidence upload (after challan created) ───────────────────────

@router.post("/{challan_id}/evidence", response_model=APIResponse[dict], status_code=201)
async def upload_evidence(
    challan_id:  str,
    file:        UploadFile = File(...),
    description: str | None = Form(default=None),
    db:          AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_officer_or_admin),
) -> APIResponse[dict]:
    file_data = await file.read()
    service   = ChallanService(db)
    evidence  = await service.upload_evidence(
        challan_id  = challan_id,
        file_data   = file_data,
        filename    = file.filename or "evidence",
        file_type   = file.content_type or "application/octet-stream",
        uploaded_by = current_user.id,
        description = description,
    )
    return APIResponse(
        message = "Evidence uploaded to IPFS",
        data    = {"id": evidence.id, "cid": evidence.ipfs_cid, "url": evidence.ipfs_url},
    )


# ── Payments ──────────────────────────────────────────────────────────────────

@router.post("/payments", response_model=APIResponse[PaymentResponse], status_code=201)
async def process_payment(
    data: PaymentCreate,
    db:   AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> APIResponse[PaymentResponse]:
    service = ChallanService(db)
    payment = await service.process_payment(data, paid_by_id=current_user.id)
    return APIResponse(message="Payment processed", data=PaymentResponse.model_validate(payment))