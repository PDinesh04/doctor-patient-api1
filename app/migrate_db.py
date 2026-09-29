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
    # Create unique index for doctor email
    try:
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS "
                "ix_doctors_email_unique ON doctors(email)"
            )
        )
        print("Unique doctor email index created successfully!")
    except Exception as e:
        print("Doctor email index error:", e)
    # Add audit fields to doctors table
    audit_columns = [
        ("created_at", "DATETIME"),
        ("updated_at", "DATETIME"),
        ("created_by", "INTEGER"),
        ("updated_by", "INTEGER")
    ]

    for column_name, column_type in audit_columns:
        try:
            connection.execute(
                text(
                    f"ALTER TABLE doctors ADD COLUMN "
                    f"{column_name} {column_type}"
                )
            )
            print(f"Doctor {column_name} added successfully!")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print(f"Doctor {column_name} already exists.")
            else:
                print(f"Doctor {column_name} error:", e)

    # Add audit fields to patients table
    for column_name, column_type in audit_columns:
        try:
            connection.execute(
                text(
                    f"ALTER TABLE patients ADD COLUMN "
                    f"{column_name} {column_type}"
                )
            )
            print(f"Patient {column_name} added successfully!")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print(f"Patient {column_name} already exists.")
            else:
                print(f"Patient {column_name} error:", e)
    connection.commit()

    # Add audit fields to appointments table
    for column_name, column_type in audit_columns:
        try:
            connection.execute(
                text(
                    f"ALTER TABLE appointments ADD COLUMN "
                    f"{column_name} {column_type}"
                )
            )
            print(f"Appointment {column_name} added successfully!")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print(f"Appointment {column_name} already exists.")
            else:
                print(f"Appointment {column_name} error:", e)


print("Database migration completed!")
