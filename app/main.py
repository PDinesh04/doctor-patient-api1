import time
from starlette.requests import Request
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from collections import defaultdict, deque
from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.database import engine
from app.database import Base
from app import models
from app.auth.router import router as auth_router
from app.dependencies import get_current_user
from app.doctors.router import router as doctors_router
from app.appointments.router import router as appointments_router
from app.patients.router import router as patients_router
from app.billing.router import router as billing_router
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
RATE_LIMIT = 60
RATE_WINDOW = 60

request_history = defaultdict(deque)

@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": 422,
                "message": "Validation error",
                "details": exc.errors()
            }
        }
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(
    request: Request,
    exc: IntegrityError
):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": {
                "code": 400,
                "message": "Database constraint error"
            }
        }
    )

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()

    history = request_history[client_ip]

    while history and current_time - history[0] > RATE_WINDOW:
        history.popleft()

    if len(history) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": {
                    "code": 429,
                    "message": "Too many requests. Please try again later."
                }
            }
        )

    history.append(current_time)

    return await call_next(request)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    response.headers["X-Process-Time"] = f"{process_time:.6f}"

    logger.info(
        "%s %s completed in %.6f seconds",
        request.method,
        request.url.path,
        process_time
    )

    return response
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
app.include_router(appointments_router, prefix="/api/v1")
app.include_router(billing_router, prefix="/api/v1")




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