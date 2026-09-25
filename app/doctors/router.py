from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas import (
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
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

@router.get(
    "",
    response_model=list[DoctorResponse]
)
def list_doctors(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_doctors(db)


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
        raise HTTPException(
            status_code=400,
            detail=error
        )

    return patient


# -------------------------
# GET DOCTOR'S PATIENTS
# -------------------------

@router.get(
    "/{doctor_id}/patients",
    response_model=list[PatientResponse]
)
def doctor_patients_api(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Admin can view any doctor's patients
    if current_user.role == "admin":
        patients = get_doctor_patients(
            db,
            doctor_id
        )

        if patients is None:
            raise HTTPException(
                status_code=404,
                detail="Doctor not found"
            )

        return patients

    # Doctor can only view their own patients
    if current_user.role == "doctor":

        if not current_user.doctor:
            raise HTTPException(
                status_code=403,
                detail="Doctor profile not linked"
            )

        if current_user.doctor.id != doctor_id:
            raise HTTPException(
                status_code=403,
                detail="You can only view your own patients"
            )

        return get_doctor_patients(
            db,
            doctor_id
        )

    raise HTTPException(
        status_code=403,
        detail="Access denied"
    )