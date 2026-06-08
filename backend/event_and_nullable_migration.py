from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    # 1. Add tokens_valid_after column to users table if not exists
    try:
        print("Adding tokens_valid_after column to users table...")
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS tokens_valid_after TIMESTAMP WITHOUT TIME ZONE"))
        db.session.commit()
        print("Success adding column.")
    except Exception as e:
        db.session.rollback()
        print(f"Skipped/Failed adding tokens_valid_after column: {e}")

    # 2. Make emergency_contact_number nullable on doctors, nurses, pharmacists
    for table in ["doctors", "nurses", "pharmacists"]:
        try:
            print(f"Dropping NOT NULL constraint on emergency_contact_number for table: {table}...")
            db.session.execute(text(f"ALTER TABLE {table} ALTER COLUMN emergency_contact_number DROP NOT NULL"))
            db.session.commit()
            print("Success dropping constraint.")
        except Exception as e:
            db.session.rollback()
            print(f"Skipped/Failed dropping constraint on {table}: {e}")

    # 3. Create any missing tables (like 'events')
    print("Creating missing database tables (including events table)...")
    db.create_all()
    print("Database migrations applied successfully!")
