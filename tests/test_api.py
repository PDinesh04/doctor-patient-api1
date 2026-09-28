from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


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
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401