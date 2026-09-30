from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(String, default="doctor", nullable=False)
    is_active = Column(Boolean, default=True)

    doctor = relationship(
        "Doctor",
        back_populates="user",
        uselist=False
    )


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC)
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )

    created_by = Column(
        Integer,
        nullable=True
    )

    updated_by = Column(
        Integer,
        nullable=True
    )

    patients = relationship(
        "Patient",
        back_populates="doctor"
    )

    appointments = relationship(
        "Appointment",
        back_populates="doctor"
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        unique=True
    )

    user = relationship(
        "User",
        back_populates="doctor"
    )


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    phone = Column(String, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC)
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )
    created_by = Column(
        Integer,
        nullable=True
    )

    updated_by = Column(
        Integer,
        nullable=True
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=True
    )

    doctor = relationship(
        "Doctor",
        back_populates="patients"
    )

    appointments = relationship(
        "Appointment",
        back_populates="patient"
    )


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=False,
        index=True
    )

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False,
        index=True
    )

    appointment_date = Column(
        DateTime,
        nullable=False,
        index=True
    )

    status = Column(
        String,
        nullable=False,
        default="scheduled"
    )
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC)
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )

    created_by = Column(
        Integer,
        nullable=True
    )

    updated_by = Column(
        Integer,
        nullable=True
    )
    doctor = relationship(
        "Doctor",
        back_populates="appointments"
    )

    patient = relationship(
        "Patient",
        back_populates="appointments"
    )
class Billing(Base):
    __tablename__ = "billings"

    __table_args__ = (
        CheckConstraint(
            "consultation_fee >= 0",
            name="check_consultation_fee_positive"
        ),
        CheckConstraint(
            "additional_charges >= 0",
            name="check_additional_charges_positive"
        ),
        CheckConstraint(
            "total_amount >= 0",
            name="check_total_amount_positive"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=False
    )

    appointment_id = Column(
        Integer,
        ForeignKey("appointments.id"),
        nullable=True
    )

    consultation_fee = Column(
        Float,
        nullable=False
    )

    additional_charges = Column(
        Float,
        nullable=False,
        default=0
    )

    total_amount = Column(
        Float,
        nullable=False
    )

    payment_status = Column(
        String,
        nullable=False,
        default="pending"
    )

    payment_mode = Column(
        String,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )

    created_by = Column(
        Integer,
        nullable=True
    )

    updated_by = Column(
        Integer,
        nullable=True
    )

    patient = relationship(
        "Patient",
        backref="billings"
    )

    doctor = relationship(
        "Doctor",
        backref="billings"
    )

    appointment = relationship(
        "Appointment",
        backref="billing"
    )