from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    # 1. Alter the ENUM types in PostgreSQL
    try:
        print("Altering user_roles enum type in PostgreSQL...")
        db.session.execute(text("ALTER TYPE user_roles ADD VALUE IF NOT EXISTS 'pharmacist'"))
        db.session.commit()
        print("Success.")
    except Exception as e:
        db.session.rollback()
        print(f"Skipped/Failed altering user_roles: {e}")

    try:
        print("Altering application_roles enum type in PostgreSQL...")
        db.session.execute(text("ALTER TYPE application_roles ADD VALUE IF NOT EXISTS 'pharmacist'"))
        db.session.commit()
        print("Success.")
    except Exception as e:
        db.session.rollback()
        print(f"Skipped/Failed altering application_roles: {e}")

    # 2. Run db.create_all() to create the new pharmacists table if not exists
    print("Creating pharmacists table if not exists...")
    db.create_all()
    print("Database tables synchronized successfully!")
