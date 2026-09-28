from sqlalchemy.orm import Session

from app import models
from app.schemas import PatientCreate, PatientUpdate

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



def get_patients(
    db: Session,
    age_gt: int | None = None,
    page: int = 1,
    limit: int = 10
):
    query = db.query(models.Patient)

    if age_gt is not None:
        query = query.filter(
            models.Patient.age > age_gt
        )

    total = query.count()

    offset = (page - 1) * limit

    patients = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return total, patients
def get_patient(db: Session, patient_id: int):
    return (
        db.query(models.Patient)
        .filter(models.Patient.id == patient_id)
        .first()
    )


def update_patient(
    db: Session,
    patient_id: int,
    patient_data: PatientUpdate
):
    patient = get_patient(db, patient_id)

    if not patient:
        return None

    update_data = patient_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)

    return patient


def delete_patient(db: Session, patient_id: int):
    patient = get_patient(db, patient_id)

    if not patient:
        return None

    db.delete(patient)
    db.commit()

    return patient