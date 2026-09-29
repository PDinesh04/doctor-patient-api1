from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app import models
from app.schemas import AppointmentCreate, AppointmentUpdate


def create_appointment(
    db: Session,
    appointment: AppointmentCreate,
    user_id: int
):
    # Check doctor
    doctor = (
        db.query(models.Doctor)
        .filter(models.Doctor.id == appointment.doctor_id)
        .first()
    )

    if not doctor:
        return None, "Doctor not found"

    # Check doctor active
    if not doctor.is_active:
        return None, "Cannot create appointment with an inactive doctor"

    # Check patient
    patient = (
        db.query(models.Patient)
        .filter(models.Patient.id == appointment.patient_id)
        .first()
    )

    if not patient:
        return None, "Patient not found"

    # Check overlapping appointment
    existing_appointment = (
        db.query(models.Appointment)
        .filter(
            models.Appointment.doctor_id == appointment.doctor_id,
            models.Appointment.appointment_date
            == appointment.appointment_date,
            models.Appointment.status == "scheduled"
        )
        .first()
    )

    if existing_appointment:
        return None, "Doctor already has an appointment at this time"

    new_appointment = models.Appointment(
        doctor_id=appointment.doctor_id,
        patient_id=appointment.patient_id,
        appointment_date=appointment.appointment_date,
        status=appointment.status,
        created_by=user_id,
        updated_by=user_id
    )

    try:
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)

    except IntegrityError:
        db.rollback()
        return None, "Database constraint error while creating appointment"

    return new_appointment, None




def get_appointments(db: Session):
    return (
        db.query(models.Appointment)
        .order_by(models.Appointment.appointment_date)
        .all()
    )


def get_appointment(db: Session, appointment_id: int):
    return (
        db.query(models.Appointment)
        .filter(models.Appointment.id == appointment_id)
        .first()
    )


def update_appointment(
    db: Session,
    appointment_id: int,
    appointment_data: AppointmentUpdate,
        user_id: int
):
    appointment = get_appointment(db, appointment_id)

    if not appointment:
        return None, "Appointment not found"

    update_data = appointment_data.model_dump(exclude_unset=True)

    doctor_id = update_data.get(
        "doctor_id",
        appointment.doctor_id
    )

    patient_id = update_data.get(
        "patient_id",
        appointment.patient_id
    )

    appointment_date = update_data.get(
        "appointment_date",
        appointment.appointment_date
    )

    # Check doctor
    doctor = (
        db.query(models.Doctor)
        .filter(models.Doctor.id == doctor_id)
        .first()
    )

    if not doctor:
        return None, "Doctor not found"

    if not doctor.is_active:
        return None, "Cannot use an inactive doctor"

    # Check patient
    patient = (
        db.query(models.Patient)
        .filter(models.Patient.id == patient_id)
        .first()
    )

    if not patient:
        return None, "Patient not found"

    # Check overlapping appointment
    existing = (
        db.query(models.Appointment)
        .filter(
            models.Appointment.doctor_id == doctor_id,
            models.Appointment.appointment_date == appointment_date,
            models.Appointment.status == "scheduled",
            models.Appointment.id != appointment_id
        )
        .first()
    )

    if existing:
        return None, "Doctor already has an appointment at this time"

    for key, value in update_data.items():
        setattr(appointment, key, value)
    appointment.updated_by = user_id

    try:
        db.commit()
        db.refresh(appointment)

    except IntegrityError:
        db.rollback()
        return None, "Database constraint error while updating appointment"

    return appointment, None

def delete_appointment(
    db: Session,
    appointment_id: int
):
    appointment = get_appointment(db, appointment_id)

    if not appointment:
        return None

    db.delete(appointment)
    db.commit()

    return appointment


def get_doctor_appointments(
    db: Session,
    doctor_id: int
):
    return (
        db.query(models.Appointment)
        .filter(models.Appointment.doctor_id == doctor_id)
        .order_by(models.Appointment.appointment_date)
        .all()
    )

def get_patient_appointments(
    db: Session,
    patient_id: int
):
    return (
        db.query(models.Appointment)
        .filter(models.Appointment.patient_id == patient_id)
        .order_by(models.Appointment.appointment_date)
        .all()
    )
