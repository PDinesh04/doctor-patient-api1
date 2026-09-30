from datetime import datetime, date, time

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from app import models
from app.schemas import BillingCreate, BillingUpdate


def calculate_total(
    consultation_fee: float,
    additional_charges: float
) -> float:
    return consultation_fee + additional_charges


def create_billing(
    db: Session,
    billing: BillingCreate,
    user_id: int
):
    patient = (
        db.query(models.Patient)
        .filter(models.Patient.id == billing.patient_id)
        .first()
    )

    if not patient:
        return None, "Patient not found"

    doctor = (
        db.query(models.Doctor)
        .filter(models.Doctor.id == billing.doctor_id)
        .first()
    )

    if not doctor:
        return None, "Doctor not found"

    if not doctor.is_active:
        return None, "Cannot create billing for an inactive doctor"

    appointment = None

    if billing.appointment_id is not None:
        appointment = (
            db.query(models.Appointment)
            .filter(
                models.Appointment.id == billing.appointment_id
            )
            .first()
        )

        if not appointment:
            return None, "Appointment not found"

        if appointment.doctor_id != billing.doctor_id:
            return None, "Appointment does not belong to this doctor"

        if appointment.patient_id != billing.patient_id:
            return None, "Appointment does not belong to this patient"

        if appointment.status == "cancelled":
            return None, "Cannot create billing for a cancelled appointment"

        existing_billing = (
            db.query(models.Billing)
            .filter(
                models.Billing.appointment_id == billing.appointment_id,
                models.Billing.is_active == True
            )
            .first()
        )

        if existing_billing:
            return None, "Billing already exists for this appointment"

    total_amount = calculate_total(
        billing.consultation_fee,
        billing.additional_charges
    )

    new_billing = models.Billing(
        patient_id=billing.patient_id,
        doctor_id=billing.doctor_id,
        appointment_id=billing.appointment_id,
        consultation_fee=billing.consultation_fee,
        additional_charges=billing.additional_charges,
        total_amount=total_amount,
        payment_status=billing.payment_status,
        payment_mode=billing.payment_mode,
        is_active=True,
        created_by=user_id,
        updated_by=user_id
    )

    try:
        db.add(new_billing)

        if appointment and appointment.status == "scheduled":
            appointment.status = "completed"

        db.commit()
        db.refresh(new_billing)

    except IntegrityError:
        db.rollback()
        return None, "Database constraint error while creating billing"

    return new_billing, None


def get_billing(
    db: Session,
    billing_id: int
):
    return (
        db.query(models.Billing)
        .filter(
            models.Billing.id == billing_id,
            models.Billing.is_active == True
        )
        .first()
    )


def get_billings(
    db: Session,
    payment_status: str | None = None,
    doctor_id: int | None = None,
    patient_id: int | None = None,
    from_date=None,
    to_date=None,
    page: int = 1,
    limit: int = 10
):
    query = db.query(models.Billing).filter(
        models.Billing.is_active == True
    )

    if payment_status:
        query = query.filter(
            models.Billing.payment_status == payment_status
        )

    if doctor_id is not None:
        query = query.filter(
            models.Billing.doctor_id == doctor_id
        )

    if patient_id is not None:
        query = query.filter(
            models.Billing.patient_id == patient_id
        )

    if from_date is not None:
        query = query.filter(
            models.Billing.created_at >= from_date
        )

    if to_date is not None:
        query = query.filter(
            models.Billing.created_at <= to_date
        )

    total = query.count()

    offset = (page - 1) * limit

    billings = (
        query
        .order_by(models.Billing.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return total, billings


def get_patient_billings(
    db: Session,
    patient_id: int,
    page: int = 1,
    limit: int = 10
):
    return get_billings(
        db=db,
        patient_id=patient_id,
        page=page,
        limit=limit
    )


def get_doctor_billings(
    db: Session,
    doctor_id: int,
    page: int = 1,
    limit: int = 10
):
    return get_billings(
        db=db,
        doctor_id=doctor_id,
        page=page,
        limit=limit
    )


def update_billing(
    db: Session,
    billing_id: int,
    billing_data: BillingUpdate,
    user_id: int
):
    billing = get_billing(db, billing_id)

    if not billing:
        return None, "Billing not found"

    update_data = billing_data.model_dump(
        exclude_unset=True
    )

    consultation_fee = update_data.get(
        "consultation_fee",
        billing.consultation_fee
    )

    additional_charges = update_data.get(
        "additional_charges",
        billing.additional_charges
    )

    update_data["total_amount"] = calculate_total(
        consultation_fee,
        additional_charges
    )

    for key, value in update_data.items():
        setattr(billing, key, value)

    billing.updated_by = user_id

    try:
        db.commit()
        db.refresh(billing)

    except IntegrityError:
        db.rollback()
        return None, "Database constraint error while updating billing"

    return billing, None


def delete_billing(
    db: Session,
    billing_id: int,
    user_id: int
):
    billing = get_billing(db, billing_id)

    if not billing:
        return None

    billing.is_active = False
    billing.updated_by = user_id

    db.commit()
    db.refresh(billing)

    return billing


# ---------------------------------------------------------
# REVENUE REPORT
# ---------------------------------------------------------

def get_revenue_report(
    db: Session,
    doctor_id: int | None = None,
    from_date: date | None = None,
    to_date: date | None = None
):
    query = db.query(
        models.Billing.doctor_id,
        func.date(models.Billing.created_at).label("date"),
        func.sum(models.Billing.total_amount).label("revenue")
    ).filter(
        models.Billing.is_active == True,
        models.Billing.payment_status == "paid"
    )

    if doctor_id is not None:
        query = query.filter(
            models.Billing.doctor_id == doctor_id
        )

    if from_date is not None:
        start_datetime = datetime.combine(
            from_date,
            time.min
        )

        query = query.filter(
            models.Billing.created_at >= start_datetime
        )

    if to_date is not None:
        end_datetime = datetime.combine(
            to_date,
            time.max
        )

        query = query.filter(
            models.Billing.created_at <= end_datetime
        )

    results = (
        query
        .group_by(
            models.Billing.doctor_id,
            func.date(models.Billing.created_at)
        )
        .order_by(
            func.date(models.Billing.created_at)
        )
        .all()
    )

    return results