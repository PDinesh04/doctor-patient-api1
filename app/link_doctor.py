from app.database import SessionLocal
from app.models import User, Doctor


db = SessionLocal()

user = db.query(User).filter(
    User.email == "bobby@example.com"
).first()

doctor = db.query(Doctor).filter(
    Doctor.id == 1
).first()

if not user:
    print("Doctor user not found")
elif not doctor:
    print("Doctor record not found")
else:
    doctor.user_id = user.id

    db.commit()

    print("Doctor linked successfully!")
    print("User ID:", user.id)
    print("Doctor ID:", doctor.id)

db.close()