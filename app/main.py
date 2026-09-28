from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.database import Base
from app import models
from app.auth.router import router as auth_router
from app.dependencies import get_current_user
from app.doctors.router import router as doctors_router
from app.patients.router import router as patients_router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Doctor Patient Management API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


app.include_router(auth_router, prefix="/api/v1")
app.include_router(doctors_router, prefix="/api/v1")
app.include_router(patients_router, prefix="/api/v1")




@app.get("/")
def root():
    logger.info("Doctor Patient API root endpoint accessed")
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