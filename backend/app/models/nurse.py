from ..extensions import db
from ..utils.time import utc_now
from ..utils.enum import Gender, BloodGroup

class Nurse(db.Model):
    __tablename__ = 'nurses'

    id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True)
    nurse_code = db.Column(db.String(20), unique=True, nullable=False) # e.g., "N23F26M10"
    department_id = db.Column(db.String(12), db.ForeignKey('departments.id'), nullable=False)
    
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum(Gender, name="gender_types"), nullable=False)
    blood_group = db.Column(db.Enum(BloodGroup, name="blood_groups"), nullable=False)
    emergency_contact_number = db.Column(db.String(15), nullable=True)
    
    shift = db.Column(db.String(20), nullable=False)  # e.g., "Day", "Night", "Rotating"
    experience_years = db.Column(db.Integer, default=0)
    license_number = db.Column(db.String(20), unique=True, nullable=False)
    is_available = db.Column(db.Boolean, default=True)  # Default to available
    availability = db.Column(db.JSON, nullable=True)
    
    __table_args__ = (
        db.CheckConstraint('experience_years >= 0', name='check_nurse_experience_years_non_negative'),
    )
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = db.relationship('User', back_populates='nurse', lazy='joined')
    department = db.relationship('Department', back_populates='nurses', lazy='joined')
    patient_vitals = db.relationship('PatientVital', back_populates='nurse')

    def __repr__(self):
        return f"<Nurse {self.id} - Department: {self.department_id}>"