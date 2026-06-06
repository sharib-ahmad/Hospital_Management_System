from ..extensions import db
from ..utils.time import utc_now

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.String(12), primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    doctor_limit = db.Column(db.Integer, default=3)  # Optional: limit number of doctors in a department
    nurse_limit = db.Column(db.Integer, default=5)  # Optional: limit number of nurses in a department
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    # Relationships
    doctors = db.relationship('Doctor', back_populates='department', lazy='selectin')
    nurses = db.relationship('Nurse', back_populates='department', lazy='selectin')
    pharmacists = db.relationship('Pharmacist', back_populates='department', lazy='selectin')
    applications = db.relationship('Application', back_populates='department', lazy='selectin')
    @property
    def staff(self):
        return {
            "doctors": len(self.doctors),
            "nurses": len(self.nurses),
            "pharmacists": len(self.pharmacists)
        }

    def __repr__(self):
        return f"<Department {self.name}>"
