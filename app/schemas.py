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
from datetime import datetime
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