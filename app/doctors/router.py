from fastapi import APIRouter, Depends, HTTPException
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas import (
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
    DoctorPaginatedResponse,
    PatientResponse
)

from app.doctors.service import (
    create_doctor,
    get_doctors,
    get_doctor,
    update_doctor,
    delete_doctor,
    assign_patient,
    get_doctor_patients
)

from app.dependencies import (
    get_current_user,
    require_admin
)


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


# -------------------------
# CREATE DOCTOR
# -------------------------

@router.post(
    "",
    response_model=DoctorResponse
)
def create_doctor_api(
    doctor: DoctorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    new_doctor = create_doctor(db, doctor)

    if new_doctor is None:
        raise HTTPException(
            status_code=400,
            detail="Doctor email already exists"
        )

    return new_doctor


# -------------------------
# GET ALL DOCTORS
# -------------------------
@router.get("", response_model=DoctorPaginatedResponse)
def list_doctors(
    specialization: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    total, doctors = get_doctors(
        db,
        specialization=specialization,
        is_active=is_active,
        page=page,
        limit=limit
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": doctors
    }

# -------------------------
# GET ONE DOCTOR
# -------------------------

@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def get_doctor_api(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    doctor = get_doctor(db, doctor_id)

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return doctor


# -------------------------
# UPDATE DOCTOR
# -------------------------

@router.put(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def update_doctor_api(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    doctor = update_doctor(
        db,
        doctor_id,
        doctor_data
    )

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return doctor
@router.patch("/{doctor_id}", response_model=DoctorResponse)
def patch_doctor_api(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    doctor = update_doctor(
        db,
        doctor_id,
        doctor_data
    )

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return doctor


# -------------------------
# DELETE DOCTOR
# SOFT DELETE
# -------------------------

@router.delete(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def delete_doctor_api(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    doctor = delete_doctor(db, doctor_id)

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return doctor


# -------------------------
# ASSIGN PATIENT TO DOCTOR
# -------------------------

@router.post(
    "/{doctor_id}/patients/{patient_id}",
    response_model=PatientResponse
)
def assign_patient_api(
    doctor_id: int,
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    patient, error = assign_patient(
        db,
        doctor_id,
        patient_id
    )

    if error:
        if error == "Doctor not found":
            raise HTTPException(status_code=404, detail=error)
        if error == "Patient not found":
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(
            status_code=400,
            detail=error
        )

    return patient


# -------------------------
# GET DOCTOR'S PATIENTS
# -------------------------

@router.get("", response_model=list[DoctorResponse])
def list_doctors(
    specialization: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_doctors(
        db,
        specialization=specialization,
        is_active=is_active
    )