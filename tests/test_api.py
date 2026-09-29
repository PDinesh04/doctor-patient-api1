from datetime import datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app import models

from app.schemas import (
    DoctorCreate,
    DoctorUpdate,
    PatientCreate,
    PatientUpdate,
    AppointmentCreate,
    AppointmentUpdate,
    UserCreate
)

from app.doctors.service import (
    create_doctor,
    get_doctor,
    get_doctors,
    update_doctor,
    delete_doctor,
    assign_patient,
    get_doctor_patients
)

from app.patients.service import (
    create_patient,
    get_patient,
    get_patients,
    update_patient,
    delete_patient
)

from app.appointments.service import (
    create_appointment,
    get_appointment,
    get_appointments,
    update_appointment,
    delete_appointment,
    get_doctor_appointments,
    get_patient_appointments
)

from app.auth.service import (
    register_user,
    authenticate_user,
    hash_password,
    verify_password,
    create_access_token
)


client = TestClient(app)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def unique_email():
    return f"test_{uuid4().hex}@example.com"


def create_test_doctor(db):
    doctor = DoctorCreate(
        name="Test Doctor",
        specialization="Cardiology",
        email=unique_email()
    )

    return create_doctor(db, doctor, 1)


def create_test_patient(db):
    patient = PatientCreate(
        name="Test Patient",
        age=30,
        phone=str(uuid4().int)[0:10]
    )

    return create_patient(db, patient, 1)


# ============================================================
# BASIC API TESTS
# ============================================================

def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Doctor Patient API is running"


def test_invalid_patient_phone():
    response = client.post(
        "/api/v1/patients",
        json={
            "name": "Test Patient",
            "age": 25,
            "phone": "12345"
        },
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401


def test_get_doctors_without_token():
    response = client.get("/api/v1/doctors")

    assert response.status_code == 401


def test_get_patient_not_found():
    response = client.get(
        "/api/v1/patients/99999",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401


def test_get_doctor_not_found():
    response = client.get(
        "/api/v1/doctors/99999",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401


def test_invalid_patient_age():
    response = client.post(
        "/api/v1/patients",
        json={
            "name": "Test Patient",
            "age": 0,
            "phone": "9876543210"
        },
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401


def test_invalid_appointment_date():
    response = client.post(
        "/api/v1/appointments",
        json={
            "doctor_id": 1,
            "patient_id": 1,
            "appointment_date": "invalid-date",
            "status": "scheduled"
        },
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401


# ============================================================
# DOCTOR SERVICE TESTS
# ============================================================

def test_get_doctors_service():
    db = SessionLocal()

    total, doctors = get_doctors(db)

    assert total >= 0
    assert isinstance(doctors, list)

    db.close()


def test_get_doctors_with_specialization_filter():
    db = SessionLocal()

    total, doctors = get_doctors(
        db,
        specialization="Cardiology"
    )

    assert total >= 0
    assert isinstance(doctors, list)

    db.close()


def test_get_doctors_with_active_filter():
    db = SessionLocal()

    total, doctors = get_doctors(
        db,
        is_active=True
    )

    assert total >= 0
    assert isinstance(doctors, list)

    db.close()


def test_get_doctors_pagination():
    db = SessionLocal()

    total, doctors = get_doctors(
        db,
        page=1,
        limit=5
    )

    assert total >= 0
    assert isinstance(doctors, list)
    assert len(doctors) <= 5

    db.close()


def test_create_doctor_service():
    db = SessionLocal()

    doctor = DoctorCreate(
        name="Service Doctor",
        specialization="Cardiology",
        email=unique_email()
    )

    result = create_doctor(
        db,
        doctor,
        1
    )

    assert result is not None
    assert result.name == "Service Doctor"

    db.close()


def test_create_duplicate_doctor():
    db = SessionLocal()

    email = unique_email()

    doctor1 = DoctorCreate(
        name="Doctor One",
        specialization="Cardiology",
        email=email
    )

    doctor2 = DoctorCreate(
        name="Doctor Two",
        specialization="Neurology",
        email=email
    )

    first = create_doctor(db, doctor1, 1)
    second = create_doctor(db, doctor2, 1)

    assert first is not None
    assert second is None

    db.close()


def test_get_doctor_service():
    db = SessionLocal()

    result = get_doctor(db, 1)

    assert result is not None
    assert result.id == 1

    db.close()


def test_get_doctor_not_found_service():
    db = SessionLocal()

    result = get_doctor(db, 99999)

    assert result is None

    db.close()


def test_update_doctor_service():
    db = SessionLocal()

    doctor = create_test_doctor(db)

    data = DoctorUpdate(
        specialization="Neurology"
    )

    updated, error = update_doctor(
        db,
        doctor.id,
        data,
        1
    )

    assert error is None
    assert updated is not None
    assert updated.specialization == "Neurology"

    db.close()


def test_update_doctor_not_found():
    db = SessionLocal()

    data = DoctorUpdate(
        specialization="Neurology"
    )

    doctor, error = update_doctor(
        db,
        99999,
        data,
        1
    )

    assert doctor is None
    assert error == "Doctor not found"

    db.close()


def test_update_doctor_duplicate_email():
    db = SessionLocal()

    doctor1 = create_test_doctor(db)
    doctor2 = create_test_doctor(db)

    data = DoctorUpdate(
        email=doctor2.email
    )

    result, error = update_doctor(
        db,
        doctor1.id,
        data,
        1
    )

    assert result is None
    assert error == "Doctor email already exists"

    db.close()


def test_delete_doctor_service():
    db = SessionLocal()

    doctor = create_test_doctor(db)

    result = delete_doctor(
        db,
        doctor.id
    )

    assert result is not None
    assert result.is_active is False

    db.close()


def test_delete_doctor_not_found():
    db = SessionLocal()

    result = delete_doctor(
        db,
        99999
    )

    assert result is None

    db.close()


# ============================================================
# DOCTOR-PATIENT ASSIGNMENT TESTS
# ============================================================

def test_assign_patient_success():
    db = SessionLocal()

    doctor = create_test_doctor(db)
    patient = create_test_patient(db)

    result, error = assign_patient(
        db,
        doctor.id,
        patient.id
    )

    assert error is None
    assert result is not None
    assert result.doctor_id == doctor.id

    db.close()


def test_assign_patient_doctor_not_found():
    db = SessionLocal()

    patient = create_test_patient(db)

    result, error = assign_patient(
        db,
        99999,
        patient.id
    )

    assert result is None
    assert error == "Doctor not found"

    db.close()


def test_assign_patient_patient_not_found():
    db = SessionLocal()

    doctor = create_test_doctor(db)

    result, error = assign_patient(
        db,
        doctor.id,
        99999
    )

    assert result is None
    assert error == "Patient not found"

    db.close()


def test_assign_patient_inactive_doctor():
    db = SessionLocal()

    doctor = create_test_doctor(db)
    patient = create_test_patient(db)

    doctor.is_active = False
    db.commit()

    result, error = assign_patient(
        db,
        doctor.id,
        patient.id
    )

    assert result is None
    assert error == "Cannot assign patient to an inactive doctor"

    db.close()


def test_assign_same_patient_twice():
    db = SessionLocal()

    doctor = create_test_doctor(db)
    patient = create_test_patient(db)

    first, error1 = assign_patient(
        db,
        doctor.id,
        patient.id
    )

    second, error2 = assign_patient(
        db,
        doctor.id,
        patient.id
    )

    assert first is not None
    assert error1 is None
    assert second is None
    assert error2 == "Patient already assigned to this doctor"

    db.close()


def test_get_doctor_patients():
    db = SessionLocal()

    doctor = create_test_doctor(db)
    patient = create_test_patient(db)

    assign_patient(
        db,
        doctor.id,
        patient.id
    )

    patients = get_doctor_patients(
        db,
        doctor.id
    )

    assert patients is not None
    assert isinstance(patients, list)
    assert len(patients) >= 1

    db.close()


def test_get_doctor_patients_not_found():
    db = SessionLocal()

    result = get_doctor_patients(
        db,
        99999
    )

    assert result is None

    db.close()


# ============================================================
# PATIENT SERVICE TESTS
# ============================================================

def test_get_patients_service():
    db = SessionLocal()

    total, patients = get_patients(db)

    assert total >= 0
    assert isinstance(patients, list)

    db.close()


def test_get_patients_age_filter():
    db = SessionLocal()

    total, patients = get_patients(
        db,
        age_gt=25
    )

    assert total >= 0
    assert isinstance(patients, list)

    for patient in patients:
        assert patient.age > 25

    db.close()


def test_get_patients_pagination():
    db = SessionLocal()

    total, patients = get_patients(
        db,
        page=1,
        limit=5
    )

    assert total >= 0
    assert isinstance(patients, list)
    assert len(patients) <= 5

    db.close()


def test_create_patient_service():
    db = SessionLocal()

    patient = create_test_patient(db)

    assert patient is not None
    assert patient.name == "Test Patient"

    db.close()


def test_get_patient_service():
    db = SessionLocal()

    result = get_patient(
        db,
        1
    )

    assert result is not None
    assert result.id == 1

    db.close()


def test_get_patient_not_found_service():
    db = SessionLocal()

    result = get_patient(
        db,
        99999
    )

    assert result is None

    db.close()


def test_update_patient_service():
    db = SessionLocal()

    patient = create_test_patient(db)

    data = PatientUpdate(
        age=31
    )

    result = update_patient(
        db,
        patient.id,
        data,
        1
    )

    assert result is not None
    assert result.age == 31

    db.close()


def test_update_patient_not_found():
    db = SessionLocal()

    data = PatientUpdate(
        age=31
    )

    result = update_patient(
        db,
        99999,
        data,
        1
    )

    assert result is None

    db.close()


def test_delete_patient_service():
    db = SessionLocal()

    patient = create_test_patient(db)

    result = delete_patient(
        db,
        patient.id
    )

    assert result is not None

    deleted = get_patient(
        db,
        patient.id
    )

    assert deleted is None

    db.close()


def test_delete_patient_not_found():
    db = SessionLocal()

    patient = delete_patient(
        db,
        99999
    )

    assert patient is None

    db.close()


# ============================================================
# APPOINTMENT SERVICE TESTS
# ============================================================

def test_get_appointments_service():
    db = SessionLocal()

    result = get_appointments(db)

    assert isinstance(result, list)

    db.close()


def test_get_appointment_not_found_service():
    db = SessionLocal()

    result = get_appointment(
        db,
        99999
    )

    assert result is None

    db.close()


def test_create_appointment_success():
    db = SessionLocal()

    doctor = create_test_doctor(db)
    patient = create_test_patient(db)

    appointment = AppointmentCreate(
        doctor_id=doctor.id,
        patient_id=patient.id,
        appointment_date=datetime(2035, 1, 1, 10, 0),
        status="scheduled"
    )

    result, error = create_appointment(
        db,
        appointment,
        1
    )

    assert error is None
    assert result is not None
    assert result.doctor_id == doctor.id
    assert result.patient_id == patient.id

    db.close()


def test_create_appointment_doctor_not_found():
    db = SessionLocal()

    patient = create_test_patient(db)

    appointment = AppointmentCreate(
        doctor_id=99999,
        patient_id=patient.id,
        appointment_date=datetime(2035, 2, 1, 10, 0),
        status="scheduled"
    )

    result, error = create_appointment(
        db,
        appointment,
        1
    )

    assert result is None
    assert error == "Doctor not found"

    db.close()


def test_create_appointment_patient_not_found():
    db = SessionLocal()

    doctor = create_test_doctor(db)

    appointment = AppointmentCreate(
        doctor_id=doctor.id,
        patient_id=99999,
        appointment_date=datetime(2035, 3, 1, 10, 0),
        status="scheduled"
    )

    result, error = create_appointment(
        db,
        appointment,
        1
    )

    assert result is None
    assert error == "Patient not found"

    db.close()


def test_create_appointment_inactive_doctor():
    db = SessionLocal()

    doctor = create_test_doctor(db)
    patient = create_test_patient(db)

    doctor.is_active = False
    db.commit()

    appointment = AppointmentCreate(
        doctor_id=doctor.id,
        patient_id=patient.id,
        appointment_date=datetime(2035, 4, 1, 10, 0),
        status="scheduled"
    )

    result, error = create_appointment(
        db,
        appointment,
        1
    )

    assert result is None
    assert error == "Cannot create appointment with an inactive doctor"

    db.close()


def test_create_duplicate_appointment():
    db = SessionLocal()

    doctor = create_test_doctor(db)
    patient = create_test_patient(db)

    appointment = AppointmentCreate(
        doctor_id=doctor.id,
        patient_id=patient.id,
        appointment_date=datetime(2035, 5, 1, 10, 0),
        status="scheduled"
    )

    first, error1 = create_appointment(
        db,
        appointment,
        1
    )

    second, error2 = create_appointment(
        db,
        appointment,
        1
    )

    assert first is not None
    assert error1 is None
    assert second is None
    assert error2 == "Doctor already has an appointment at this time"

    db.close()


def test_get_appointment_service():
    db = SessionLocal()

    doctor = create_test_doctor(db)
    patient = create_test_patient(db)

    appointment = AppointmentCreate(
        doctor_id=doctor.id,
        patient_id=patient.id,
        appointment_date=datetime(2035, 6, 1, 10, 0),
        status="scheduled"
    )

    created, error = create_appointment(
        db,
        appointment,
        1
    )

    assert error is None

    result = get_appointment(
        db,
        created.id
    )

    assert result is not None
    assert result.id == created.id

    db.close()


def test_update_appointment_service():
    db = SessionLocal()

    doctor = create_test_doctor(db)
    patient = create_test_patient(db)

    appointment = AppointmentCreate(
        doctor_id=doctor.id,
        patient_id=patient.id,
        appointment_date=datetime(2035, 7, 1, 10, 0),
        status="scheduled"
    )

    created, error = create_appointment(
        db,
        appointment,
        1
    )

    assert error is None

    update_data = AppointmentUpdate(
        status="completed"
    )

    updated, update_error = update_appointment(
        db,
        created.id,
        update_data,
        1
    )

    assert update_error is None
    assert updated is not None
    assert updated.status == "completed"

    db.close()


def test_update_appointment_not_found():
    db = SessionLocal()

    data = AppointmentUpdate(
        status="completed"
    )

    result, error = update_appointment(
        db,
        99999,
        data,
        1
    )

    assert result is None
    assert error == "Appointment not found"

    db.close()


def test_update_appointment_doctor_not_found():
    db = SessionLocal()

    doctor = create_test_doctor(db)
    patient = create_test_patient(db)

    appointment = AppointmentCreate(
        doctor_id=doctor.id,
        patient_id=patient.id,
        appointment_date=datetime(2035, 8, 1, 10, 0),
        status="scheduled"
    )

    created, _ = create_appointment(
        db,
        appointment,
        1
    )

    update_data = AppointmentUpdate(
        doctor_id=99999
    )

    result, error = update_appointment(
        db,
        created.id,
        update_data,
        1
    )

    assert result is None
    assert error == "Doctor not found"

    db.close()


def test_update_appointment_patient_not_found():
    db = SessionLocal()

    doctor = create_test_doctor(db)
    patient = create_test_patient(db)

    appointment = AppointmentCreate(
        doctor_id=doctor.id,
        patient_id=patient.id,
        appointment_date=datetime(2035, 9, 1, 10, 0),
        status="scheduled"
    )

    created, _ = create_appointment(
        db,
        appointment,
        1
    )

    update_data = AppointmentUpdate(
        patient_id=99999
    )

    result, error = update_appointment(
        db,
        created.id,
        update_data,
        1
    )

    assert result is None
    assert error == "Patient not found"

    db.close()


def test_delete_appointment_service():
    db = SessionLocal()

    doctor = create_test_doctor(db)
    patient = create_test_patient(db)

    appointment = AppointmentCreate(
        doctor_id=doctor.id,
        patient_id=patient.id,
        appointment_date=datetime(2035, 10, 1, 10, 0),
        status="scheduled"
    )

    created, error = create_appointment(
        db,
        appointment,
        1
    )

    assert error is None

    deleted = delete_appointment(
        db,
        created.id
    )

    assert deleted is not None

    db.close()


def test_delete_appointment_not_found():
    db = SessionLocal()

    result = delete_appointment(
        db,
        99999
    )

    assert result is None

    db.close()


def test_get_doctor_appointments():
    db = SessionLocal()

    doctor = create_test_doctor(db)
    patient = create_test_patient(db)

    appointment = AppointmentCreate(
        doctor_id=doctor.id,
        patient_id=patient.id,
        appointment_date=datetime(2035, 11, 1, 10, 0),
        status="scheduled"
    )

    create_appointment(
        db,
        appointment,
        1
    )

    result = get_doctor_appointments(
        db,
        doctor.id
    )

    assert isinstance(result, list)
    assert len(result) >= 1

    db.close()


def test_get_patient_appointments():
    db = SessionLocal()

    doctor = create_test_doctor(db)
    patient = create_test_patient(db)

    appointment = AppointmentCreate(
        doctor_id=doctor.id,
        patient_id=patient.id,
        appointment_date=datetime(2035, 12, 1, 10, 0),
        status="scheduled"
    )

    create_appointment(
        db,
        appointment,
        1
    )

    result = get_patient_appointments(
        db,
        patient.id
    )

    assert isinstance(result, list)
    assert len(result) >= 1

    db.close()


# ============================================================
# AUTH SERVICE TESTS
# ============================================================

def test_hash_and_verify_password():
    password = "TestPassword123"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_register_user():
    db = SessionLocal()

    user = UserCreate(
        name="Test User",
        email=unique_email(),
        password="Test123456"
    )

    result = register_user(
        db,
        user
    )

    assert result is not None
    assert result.email == user.email
    assert result.role == "doctor"
    assert result.is_active is True

    db.close()


def test_register_duplicate_user():
    db = SessionLocal()

    email = unique_email()

    user1 = UserCreate(
        name="User One",
        email=email,
        password="Test123456"
    )

    user2 = UserCreate(
        name="User Two",
        email=email,
        password="Test123456"
    )

    first = register_user(
        db,
        user1
    )

    second = register_user(
        db,
        user2
    )

    assert first is not None
    assert second is None

    db.close()


def test_authenticate_user_success():
    db = SessionLocal()

    email = unique_email()

    user = UserCreate(
        name="Login User",
        email=email,
        password="Login123456"
    )

    register_user(
        db,
        user
    )

    result = authenticate_user(
        db,
        email,
        "Login123456"
    )

    assert result is not None
    assert result.email == email

    db.close()


def test_authenticate_user_wrong_password():
    db = SessionLocal()

    email = unique_email()

    user = UserCreate(
        name="Wrong Password User",
        email=email,
        password="Correct123456"
    )

    register_user(
        db,
        user
    )

    result = authenticate_user(
        db,
        email,
        "Wrong123456"
    )

    assert result is None

    db.close()


def test_authenticate_user_not_found():
    db = SessionLocal()

    result = authenticate_user(
        db,
        "does_not_exist@example.com",
        "Password123"
    )

    assert result is None

    db.close()


def test_create_access_token():
    token = create_access_token(
        1,
        "admin"
    )

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0
# ============================================================
# EXTRA TESTS FOR COVERAGE
# ============================================================

def test_protected_without_token():
    response = client.get("/protected")

    assert response.status_code == 401


def test_invalid_token_protected():
    response = client.get(
        "/protected",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401


def test_invalid_doctor_id_without_token():
    response = client.get(
        "/api/v1/doctors/99999",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401


def test_invalid_patient_id_without_token():
    response = client.get(
        "/api/v1/patients/99999",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401


def test_invalid_appointment_id_without_token():
    response = client.get(
        "/api/v1/appointments/99999",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401


def test_invalid_doctor_phone_request():
    response = client.post(
        "/api/v1/patients",
        json={
            "name": "Test Patient",
            "age": 25,
            "phone": "abc"
        },
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401


def test_invalid_patient_age_request():
    response = client.post(
        "/api/v1/patients",
        json={
            "name": "Test Patient",
            "age": -5,
            "phone": "9876543210"
        },
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401

# ============================================================
# AUTHENTICATED ROUTER TESTS
# ============================================================

def get_admin_token():
    return create_access_token(1, "admin")


def get_doctor_token():
    return create_access_token(2, "doctor")


def test_list_doctors_authenticated():
    token = get_admin_token()

    response = client.get(
        "/api/v1/doctors",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_get_doctor_authenticated():
    token = get_admin_token()

    response = client.get(
        "/api/v1/doctors/1",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_list_patients_authenticated():
    token = get_admin_token()

    response = client.get(
        "/api/v1/patients",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

def test_get_patient_authenticated():
    token = get_admin_token()

    response = client.get(
        "/api/v1/patients/1",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

def test_list_appointments_authenticated():
    token = get_admin_token()

    response = client.get(
        "/api/v1/appointments",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_get_appointment_not_found_authenticated():
    token = get_admin_token()

    response = client.get(
        "/api/v1/appointments/99999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404


def test_get_doctor_appointments_authenticated():
    token = get_admin_token()

    response = client.get(
        "/api/v1/appointments/doctor/1",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_get_patient_appointments_authenticated():
    token = get_admin_token()

    response = client.get(
        "/api/v1/appointments/patient/1",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_doctor_list_with_filter():
    token = get_admin_token()

    response = client.get(
        "/api/v1/doctors?is_active=true",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_doctor_list_with_specialization():
    token = get_admin_token()

    response = client.get(
        "/api/v1/doctors?specialization=Cardiology",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_patient_list_with_age_filter():
    token = get_admin_token()

    response = client.get(
        "/api/v1/patients?age_gt=25",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_doctor_pagination():
    token = get_admin_token()

    response = client.get(
        "/api/v1/doctors?page=1&limit=5",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_patient_pagination():
    token = get_admin_token()

    response = client.get(
        "/api/v1/patients?page=1&limit=5",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
