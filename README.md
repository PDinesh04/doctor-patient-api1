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

## Project Structure

```text
app/
├── auth/
│   ├── router.py
│   └── service.py
├── doctors/
│   ├── router.py
│   └── service.py
├── patients/
│   ├── router.py
│   └── service.py
├── database.py
├── dependencies.py
├── main.py
├── models.py
└── schemas.py