from app.database import SessionLocal, Base, engine
from app import models
from app.auth.service import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

admin = models.User(
    name="Admin",
    email="admin@example.com",
    password=hash_password("Admin123"),
    role="admin",
    is_active=True
)

db.add(admin)
db.commit()
db.refresh(admin)

print("Admin created successfully!")
print("Email:", admin.email)
print("Role:", admin.role)

db.close()