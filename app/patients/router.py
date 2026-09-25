from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import PatientCreate, PatientResponse
from app.patients.service import create_patient, get_patients, get_patient
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientResponse)
def create_patient_api(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    return create_patient(db, patient)


@router.get("", response_model=list[PatientResponse])
def list_patients(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    return get_patients(db)


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

    # Admin can view any patient
    if current_user.role == "admin":
        return patient

    # Doctor can view only their assigned patients
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