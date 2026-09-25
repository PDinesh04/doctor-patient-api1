from sqlalchemy.orm import Session

from app import models
from app.schemas import PatientCreate


def create_patient(db: Session, patient: PatientCreate):
    new_patient = models.Patient(
        name=patient.name,
        age=patient.age,
        phone=patient.phone
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


def get_patients(db: Session):
    return db.query(models.Patient).all()


def get_patient(db: Session, patient_id: int):
    return (
        db.query(models.Patient)
        .filter(models.Patient.id == patient_id)
        .first()
    )