from sqlalchemy import text
from app.database import engine


with engine.connect() as connection:

    # Add user_id column to doctors table
    try:
        connection.execute(
            text("ALTER TABLE doctors ADD COLUMN user_id INTEGER")
        )
        print("user_id column added successfully!")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            print("user_id column already exists.")
        else:
            print("Error:", e)

    # Create unique index
    try:
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS "
                "ix_doctors_user_id_unique ON doctors(user_id)"
            )
        )
        print("Unique index created successfully!")
    except Exception as e:
        print("Index error:", e)

    connection.commit()

print("Database migration completed!")