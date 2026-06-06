from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    try:
        print("Altering pharmacists table to drop NOT NULL constraint on department_id...")
        db.session.execute(text("ALTER TABLE pharmacists ALTER COLUMN department_id DROP NOT NULL"))
        db.session.commit()
        print("Successfully dropped NOT NULL constraint on department_id.")
    except Exception as e:
        db.session.rollback()
        print(f"Failed to drop NOT NULL constraint: {e}")
