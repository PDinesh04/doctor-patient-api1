from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.billing import service
from app.schemas import (
    BillingCreate,
    BillingUpdate,
    BillingResponse,
    BillingPaginatedResponse,
    RevenueReportResponse

)


router = APIRouter(
    prefix="/billings",
    tags=["Billing"]
)


def get_current_doctor(db: Session, current_user):
    return (
        db.query(models.Doctor)
        .filter(models.Doctor.user_id == current_user.id)
        .first()
    )


@router.post(
    "",
    response_model=BillingResponse,
    dependencies=[Depends(require_admin)]
)
def create_billing(
    billing: BillingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_billing, error = service.create_billing(
        db,
        billing,
        current_user.id
    )

    if error:
        raise HTTPException(
            status_code=400,
            detail=error
        )

    return new_billing


@router.get(
    "",
    response_model=BillingPaginatedResponse
)
def get_all_billings(
    payment_status: str | None = None,
    doctor_id: int | None = None,
    patient_id: int | None = None,
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role == "admin":
        pass

    elif current_user.role == "doctor":
        doctor = get_current_doctor(db, current_user)

        if not doctor:
            raise HTTPException(
                status_code=403,
                detail="Doctor profile not found"
            )

        doctor_id = doctor.id

    else:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    start_datetime = None
    end_datetime = None

    if from_date:
        start_datetime = datetime.combine(
            from_date,
            time.min
        )

    if to_date:
        end_datetime = datetime.combine(
            to_date,
            time.max
        )

    total, billings = service.get_billings(
        db=db,
        payment_status=payment_status,
        doctor_id=doctor_id,
        patient_id=patient_id,
        from_date=start_datetime,
        to_date=end_datetime,
        page=page,
        limit=limit
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": billings
    }


@router.get(
    "/{billing_id}",
    response_model=BillingResponse
)
def get_billing(
    billing_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    billing = service.get_billing(
        db,
        billing_id
    )

    if not billing:
        raise HTTPException(
            status_code=404,
            detail="Billing not found"
        )

    if current_user.role == "admin":
        return billing

    if current_user.role == "doctor":
        doctor = get_current_doctor(
            db,
            current_user
        )

        if not doctor or billing.doctor_id != doctor.id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to view this billing"
            )

        return billing

    raise HTTPException(
        status_code=403,
        detail="Access denied"
    )


@router.get(
    "/patients/{patient_id}",
    response_model=BillingPaginatedResponse
)
def get_patient_billings(
    patient_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    patient = (
        db.query(models.Patient)
        .filter(models.Patient.id == patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    doctor_id = None

    if current_user.role == "doctor":
        doctor = get_current_doctor(
            db,
            current_user
        )

        if not doctor:
            raise HTTPException(
                status_code=403,
                detail="Doctor profile not found"
            )

        if patient.doctor_id != doctor.id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to view this patient's billings"
            )

        doctor_id = doctor.id

    elif current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    total, billings = service.get_billings(
        db=db,
        patient_id=patient_id,
        doctor_id=doctor_id,
        page=page,
        limit=limit
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": billings
    }


@router.get(
    "/doctors/{doctor_id}",
    response_model=BillingPaginatedResponse
)
def get_doctor_billings(
    doctor_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    doctor = (
        db.query(models.Doctor)
        .filter(models.Doctor.id == doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    if current_user.role == "doctor":
        current_doctor = get_current_doctor(
            db,
            current_user
        )

        if not current_doctor or current_doctor.id != doctor_id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to view this doctor's billings"
            )

    elif current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    total, billings = service.get_billings(
        db=db,
        doctor_id=doctor_id,
        page=page,
        limit=limit
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": billings
    }


@router.put(
    "/{billing_id}",
    response_model=BillingResponse,
    dependencies=[Depends(require_admin)]
)
def update_billing(
    billing_id: int,
    billing_data: BillingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    billing, error = service.update_billing(
        db,
        billing_id,
        billing_data,
        current_user.id
    )

    if error:
        raise HTTPException(
            status_code=400,
            detail=error
        )

    return billing


@router.patch(
    "/{billing_id}",
    response_model=BillingResponse,
    dependencies=[Depends(require_admin)]
)
def patch_billing(
    billing_id: int,
    billing_data: BillingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    billing, error = service.update_billing(
        db,
        billing_id,
        billing_data,
        current_user.id
    )

    if error:
        raise HTTPException(
            status_code=400,
            detail=error
        )

    return billing


@router.delete(
    "/{billing_id}",
    response_model=BillingResponse,
    dependencies=[Depends(require_admin)]
)
def delete_billing(
    billing_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    billing = service.delete_billing(
        db,
        billing_id,
        current_user.id
    )

    if not billing:
        raise HTTPException(
            status_code=404,
            detail="Billing not found"
        )

    return billing
# ---------------------------------------------------------
# REVENUE REPORT
# ---------------------------------------------------------

@router.get(
    "/reports/revenue",
    response_model=RevenueReportResponse
)
def revenue_report(
    doctor_id: int | None = None,
    from_date: date | None = Query(
        None,
        alias="from"
    ),
    to_date: date | None = Query(
        None,
        alias="to"
    ),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    results = service.get_revenue_report(
        db=db,
        doctor_id=doctor_id,
        from_date=from_date,
        to_date=to_date
    )

    return {
        "items": [
            {
                "doctor_id": row.doctor_id,
                "date": row.date,
                "revenue": float(row.revenue or 0)
            }
            for row in results
        ]
    }