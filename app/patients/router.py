from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientPaginatedResponse
)
from app.patients.service import (
    create_patient,
    get_patients,
    get_patient,
    update_patient,
    delete_patient
)
from app.dependencies import get_current_user, require_admin


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post("", response_model=PatientResponse)
def create_patient_api(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    return create_patient(db, patient)


@router.get("", response_model=PatientPaginatedResponse)
def list_patients(
    age_gt: int | None = Query(default=None, gt=0),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    total, patients = get_patients(
        db,
        age_gt=age_gt,
        page=page,
        limit=limit
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": patients
    }


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient_api(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    patient = get_patient(db, patient_id)

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    if current_user.role == "admin":
        return patient

    if current_user.role == "doctor":
        if not current_user.doctor:
            raise HTTPException(
                status_code=403,
                detail="Doctor profile not linked"
            )

        if patient.doctor_id != current_user.doctor.id:
            raise HTTPException(
                status_code=403,
                detail="You can only view your assigned patients"
            )

        return patient

    raise HTTPException(
        status_code=403,
        detail="Access denied"
    )


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient_api(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    patient = update_patient(
        db,
        patient_id,
        patient_data
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient


@router.patch("/{patient_id}", response_model=PatientResponse)
def patch_patient_api(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    patient = update_patient(
        db,
        patient_id,
        patient_data
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient


@router.delete("/{patient_id}", response_model=PatientResponse)
def delete_patient_api(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    patient = delete_patient(db, patient_id)

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient