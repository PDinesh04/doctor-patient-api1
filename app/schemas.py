from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool

    model_config = {"from_attributes": True}
class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
class DoctorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    specialization: str = Field(min_length=2, max_length=100)
    email: EmailStr


class DoctorUpdate(BaseModel):
    name: str | None = None
    specialization: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None


class DoctorResponse(BaseModel):
    id: int
    name: str
    specialization: str
    email: EmailStr
    is_active: bool

    model_config = {"from_attributes": True}
class PatientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(gt=0)
    phone: str = Field(pattern=r"^\d{10}$")
class PatientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    age: int | None = Field(default=None, gt=0)
    phone: str | None = Field(
        default=None,
        pattern=r"^\d{10}$"
    )


class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    phone: str

    model_config = {"from_attributes": True}
class DoctorPaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: list[DoctorResponse]


class PatientPaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: list[PatientResponse]



from datetime import datetime, date
from typing import Literal
class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_id: int
    appointment_date: datetime
    status: Literal["scheduled", "completed", "cancelled"] = "scheduled"


class AppointmentUpdate(BaseModel):
    doctor_id: int | None = None
    patient_id: int | None = None
    appointment_date: datetime | None = None
    status: Literal["scheduled", "completed", "cancelled"] | None = None


class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    appointment_date: datetime
    status: str

    model_config = {"from_attributes": True}
# ---------------------------------------------------------
# BILLING SCHEMAS
# ---------------------------------------------------------

from typing import Literal


class BillingCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: int | None = None

    consultation_fee: float = Field(
        ge=0
    )

    additional_charges: float = Field(
        default=0,
        ge=0
    )

    payment_status: Literal[
        "pending",
        "paid",
        "cancelled"
    ] = "pending"

    payment_mode: Literal[
        "cash",
        "card",
        "upi"
    ]


class BillingUpdate(BaseModel):
    consultation_fee: float | None = Field(
        default=None,
        ge=0
    )

    additional_charges: float | None = Field(
        default=None,
        ge=0
    )

    payment_status: Literal[
        "pending",
        "paid",
        "cancelled"
    ] | None = None

    payment_mode: Literal[
        "cash",
        "card",
        "upi"
    ] | None = None


class BillingResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_id: int | None

    consultation_fee: float
    additional_charges: float
    total_amount: float

    payment_status: str
    payment_mode: str

    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class BillingPaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: list[BillingResponse]


# ---------------------------------------------------------
# REVENUE REPORT SCHEMA
# ---------------------------------------------------------

class RevenueReportItem(BaseModel):
    doctor_id: int
    date: date
    revenue: float


class RevenueReportResponse(BaseModel):
    items: list[RevenueReportItem]