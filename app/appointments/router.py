from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse

from app.appointments.service import (
    create_appointment,
    get_appointments,
    get_appointment,
    update_appointment,
    delete_appointment,
    get_doctor_appointments,
    get_patient_appointments,
)

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


@router.post("", response_model=AppointmentResponse)
def create_appointment_api(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    new_appointment, error = create_appointment(
        db,
        appointment,
        current_user.id
    )

    if error:
        if error in ["Doctor not found", "Patient not found"]:
            raise HTTPException(
                status_code=404,
                detail=error
            )

        raise HTTPException(
            status_code=400,
            detail=error
        )

    return new_appointment


@router.get("", response_model=list[AppointmentResponse])
def list_appointments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_appointments(db)


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment_api(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    appointment = get_appointment(
        db,
        appointment_id
    )

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment_api(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    appointment, error = update_appointment(
        db,
        appointment_id,
        appointment_data,
        current_user.id
    )

    if error:
        if error in [
            "Appointment not found",
            "Doctor not found",
            "Patient not found"
        ]:
            raise HTTPException(
                status_code=404,
                detail=error
            )

        raise HTTPException(
            status_code=400,
            detail=error
        )

    return appointment


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def patch_appointment_api(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    appointment, error = update_appointment(
        db,
        appointment_id,
        appointment_data,
        current_user.id
    )

    if error:
        if error in [
            "Appointment not found",
            "Doctor not found",
            "Patient not found"
        ]:
            raise HTTPException(
                status_code=404,
                detail=error
            )

        raise HTTPException(
            status_code=400,
            detail=error
        )

    return appointment


@router.delete("/{appointment_id}")
def delete_appointment_api(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    appointment = delete_appointment(
        db,
        appointment_id
    )

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return {
        "message": "Appointment deleted successfully"
    }


@router.get(
    "/doctor/{doctor_id}",
    response_model=list[AppointmentResponse]
)
def doctor_appointments_api(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_doctor_appointments(
        db,
        doctor_id
    )


@router.get(
    "/patient/{patient_id}",
    response_model=list[AppointmentResponse]
)
def patient_appointments_api(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_patient_appointments(
        db,
        patient_id
    )