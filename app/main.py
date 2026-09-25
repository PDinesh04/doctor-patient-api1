from fastapi import FastAPI, Depends

from app.database import engine
from app.database import Base
from app import models
from app.auth.router import router as auth_router
from app.dependencies import get_current_user
from app.doctors.router import router as doctors_router
from app.patients.router import router as patients_router


app = FastAPI(
    title="Doctor Patient Management API",
    version="1.0.0"
)


Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(doctors_router)
app.include_router(patients_router)


@app.get("/")
def root():
    return {
        "message": "Doctor Patient API is running"
    }
@app.get("/protected")
def protected_route(current_user=Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }