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


def get_doctors(
    db: Session,
    specialization: str | None = None,
    is_active: bool | None = None,
    page: int = 1,
    limit: int = 10
):
    query = db.query(models.Doctor)

    if specialization:
        query = query.filter(
            models.Doctor.specialization.ilike(
                f"%{specialization}%"
            )
        )

    if is_active is not None:
        query = query.filter(
            models.Doctor.is_active == is_active
        )

    total = query.count()

    offset = (page - 1) * limit

    doctors = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return total, doctors

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
        return None, "Doctor not found"

    update_data = doctor_data.model_dump(exclude_unset=True)

    if "email" in update_data:
        existing_doctor = (
            db.query(models.Doctor)
            .filter(
                models.Doctor.email == update_data["email"],
                models.Doctor.id != doctor_id
            )
            .first()
        )

        if existing_doctor:
            return None, "Doctor email already exists"

    for key, value in update_data.items():
        setattr(doctor, key, value)

    db.commit()
    db.refresh(doctor)

    return doctor, None


def delete_doctor(db: Session, doctor_id: int):
    doctor = get_doctor(db, doctor_id)

    if not doctor:
        return None

    doctor.is_active = False

    db.commit()
    db.refresh(doctor)

    return doctor
def assign_patient(db: Session, doctor_id: int, patient_id: int):
    doctor = get_doctor(db, doctor_id)

    if not doctor:
        return None, "Doctor not found"

    if not doctor.is_active:
        return None, "Cannot assign patient to an inactive doctor"

    patient = (
        db.query(models.Patient)
        .filter(models.Patient.id == patient_id)
        .first()
    )

    if not patient:
        return None, "Patient not found"

    if patient.doctor_id == doctor_id:
        return None, "Patient already assigned to this doctor"

    doctor.patients.append(patient)

    db.commit()
    db.refresh(patient)

    return patient, None


def get_doctor_patients(
    db: Session,
    doctor_id: int
):
    doctor = get_doctor(db, doctor_id)

    if not doctor:
        return None

    return doctor.patients