from sqlalchemy.orm import Session

from app import models
from app.schemas import DoctorCreate, DoctorUpdate


def create_doctor(db: Session, doctor: DoctorCreate):
    existing_doctor = (
        db.query(models.Doctor)
        .filter(models.Doctor.email == doctor.email)
        .first()
    )

    if existing_doctor:
        return None

    new_doctor = models.Doctor(
        name=doctor.name,
        specialization=doctor.specialization,
        email=doctor.email,
        is_active=True
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return new_doctor


def get_doctors(db: Session):
    return db.query(models.Doctor).all()


def get_doctor(db: Session, doctor_id: int):
    return (
        db.query(models.Doctor)
        .filter(models.Doctor.id == doctor_id)
        .first()
    )


def update_doctor(
    db: Session,
    doctor_id: int,
    doctor_data: DoctorUpdate
):
    doctor = get_doctor(db, doctor_id)

    if not doctor:
        return None

    update_data = doctor_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(doctor, key, value)

    db.commit()
    db.refresh(doctor)

    return doctor


def delete_doctor(db: Session, doctor_id: int):
    doctor = get_doctor(db, doctor_id)

    if not doctor:
        return None

    doctor.is_active = False

    db.commit()
    db.refresh(doctor)

    return doctor
def assign_patient(
    db: Session,
    doctor_id: int,
    patient_id: int
):
    doctor = get_doctor(db, doctor_id)

    if not doctor:
        return None, "Doctor not found"

    patient = (
        db.query(models.Patient)
        .filter(models.Patient.id == patient_id)
        .first()
    )

    if not patient:
        return None, "Patient not found"

    if patient in doctor.patients:
        return None, "Patient already assigned"

    doctor.patients.append(patient)

    db.commit()

    return patient, None


def get_doctor_patients(
    db: Session,
    doctor_id: int
):
    doctor = get_doctor(db, doctor_id)

    if not doctor:
        return None

    return doctor.patients