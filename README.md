# Doctor-Patient Management API

A REST API built using FastAPI for managing doctors, patients, authentication, and doctor-patient assignments.

## Tech Stack

- Python 3.9+
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- JWT Authentication
- Uvicorn
- Passlib
- Pytest
- Docker

## Features

- User registration and login
- JWT-based authentication
- Role-based access control
- Admin and Doctor roles
- Doctor CRUD operations
- Patient CRUD operations
- Soft delete for doctors
- Doctor-patient assignment
- One-to-many Doctor → Patient relationship
- Doctor specialization filtering
- Active/inactive doctor filtering
- Patient age filtering
- Pagination
- Email validation
- Unique doctor email validation
- Patient phone validation
- Request logging
- CORS configuration
- API versioning using `/api/v1/`
- SQLite database with SQLAlchemy
- Automated API tests using Pytest
- Docker support
- Swagger/OpenAPI documentation

## Project Structure

```text
pythonProject5/
├── app/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── service.py
│   │
│   ├── doctors/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── service.py
│   │
│   ├── patients/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── service.py
│   │
│   ├── routes/
│   │   └── __init__.py
│   │
│   ├── __init__.py
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── admin.py
│   ├── link_doctor.py
│   └── migrate_db.py
│
├── tests/
│   └── test_api.py
│
├── .env
├── .gitignore
├── Dockerfile
├── pytest.ini
├── requirements.txt
├── README.md
└── doctor_patient.db
```

## Installation

Clone the repository:

```bash
git clone https://github.com/PDinesh04/doctor-patient-api1.git
cd doctor-patient-api1
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=sqlite:///./doctor_patient.db
SECRET_KEY=my-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Run the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## Swagger Documentation

Open:

```text
http://127.0.0.1:8000/docs
```

Swagger provides an interactive interface for testing all API endpoints.

## API Versioning

The API uses versioning:

```text
/api/v1/
```

Examples:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login

GET /api/v1/doctors
POST /api/v1/doctors

GET /api/v1/patients
POST /api/v1/patients
```

## Authentication

### Register

```http
POST /api/v1/auth/register
```

Example:

```json
{
    "name": "John Doctor",
    "email": "john@example.com",
    "password": "password123"
}
```

### Login

```http
POST /api/v1/auth/login
```

Example:

```json
{
    "email": "john@example.com",
    "password": "password123"
}
```

The login endpoint returns a JWT access token.

Use the token in protected endpoints:

```text
Authorization: Bearer <access_token>
```

## Roles

### Admin

Admin users can:

- Create doctors
- Update doctors
- Delete/deactivate doctors
- Create patients
- Update patients
- Delete patients
- Assign patients to doctors
- View doctors and patients

### Doctor

Doctors can:

- View doctors
- View their assigned patients
- Access protected endpoints using JWT authentication

Doctors cannot manage patient records or assign patients.

## Doctor APIs

### Create Doctor

```http
POST /api/v1/doctors
```

Example:

```json
{
    "name": "Dr. Gowtham",
    "specialization": "Cardiology",
    "email": "gowtham@example.com"
}
```

### Get Doctors

```http
GET /api/v1/doctors
```

Supports filtering and pagination.

Example:

```text
GET /api/v1/doctors?specialization=cardiology
```

```text
GET /api/v1/doctors?is_active=true
```

```text
GET /api/v1/doctors?page=1&limit=10
```

### Get Doctor by ID

```http
GET /api/v1/doctors/{doctor_id}
```

### Update Doctor

```http
PUT /api/v1/doctors/{doctor_id}
```

### Partial Update Doctor

```http
PATCH /api/v1/doctors/{doctor_id}
```

### Delete Doctor

```http
DELETE /api/v1/doctors/{doctor_id}
```

Doctor deletion is implemented as a soft delete by setting:

```text
is_active = false
```

## Patient APIs

### Create Patient

```http
POST /api/v1/patients
```

Example:

```json
{
    "name": "Mohith",
    "age": 24,
    "phone": "9876543201"
}
```

### Get Patients

```http
GET /api/v1/patients
```

Supports filtering and pagination.

Example:

```text
GET /api/v1/patients?age_gt=30
```

```text
GET /api/v1/patients?page=1&limit=10
```

### Get Patient by ID

```http
GET /api/v1/patients/{patient_id}
```

### Update Patient

```http
PUT /api/v1/patients/{patient_id}
```

### Partial Update Patient

```http
PATCH /api/v1/patients/{patient_id}
```

### Delete Patient

```http
DELETE /api/v1/patients/{patient_id}
```

## Doctor-Patient Assignment

Patients are connected to doctors using a one-to-many relationship.

```text
Doctor
   |
   ├── Patient 1
   ├── Patient 2
   └── Patient 3
```

### Assign Patient

```http
POST /api/v1/doctors/{doctor_id}/patients/{patient_id}
```

The API validates:

- Doctor exists
- Patient exists
- Doctor is active
- Patient is not already assigned to the same doctor

### Get Doctor's Patients

```http
GET /api/v1/doctors/{doctor_id}/patients
```

A doctor can only view their own assigned patients.

## Validation

### Doctor Email

Doctor email must:

- Be a valid email address
- Be unique

### Patient Age

Patient age must be greater than `0`.

### Patient Phone

Phone number must contain exactly 10 digits.

Example:

```text
9876543201
```

Invalid:

```text
12345
```

## Pagination

Doctor and patient list APIs support pagination.

Example:

```text
GET /api/v1/doctors?page=1&limit=10
```

Example response:

```json
{
    "total": 25,
    "page": 1,
    "limit": 10,
    "data": []
}
```

## Error Handling

The API returns appropriate HTTP status codes.

Examples:

```text
200 OK
201 Created
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
422 Validation Error
```

## Database

The project uses:

- SQLite
- SQLAlchemy ORM

Database file:

```text
doctor_patient.db
```

The database tables include:

```text
users
doctors
patients
```

## Logging

Application logging is configured using Python's `logging` module.

Example:

```text
INFO - Doctor Patient API root endpoint accessed
```

## CORS

CORS is configured to allow requests from the frontend development server:

```text
http://localhost:3000
```

## Testing

Run the automated tests using:

```bash
pytest
```

Current tests verify:

- Root endpoint
- Authentication protection

Example result:

```text
2 passed
```

## Docker

Build the Docker image:

```bash
docker build -t doctor-patient-api .
```

Run the container:

```bash
docker run -p 8000:8000 doctor-patient-api
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Security

- Passwords are hashed before storing
- JWT tokens are used for authentication
- Protected endpoints require authentication
- Role-based authorization is implemented
- `.env` is excluded from Git
- Database files are excluded from Git

## API Documentation

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

ReDoc documentation:

```text
http://127.0.0.1:8000/redoc
```

## License

This project was created as a FastAPI Doctor-Patient Management API assignment.