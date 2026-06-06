from ..extensions import db
from ..utils.time import utc_now
from ..utils.enum import Gender, BloodGroup

class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True)
    doctor_code = db.Column(db.String(20), unique=True, nullable=False) # e.g., "DOC-101"
    department_id = db.Column(db.String(12), db.ForeignKey('departments.id'), nullable=False)
      
    shift = db.Column(db.String(20), nullable=False)  # e.g., "Day", "Night", "Rotating"
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum(Gender, name="gender_types"), nullable=False)
    blood_group = db.Column(db.Enum(BloodGroup, name="blood_groups"), nullable=False)
    emergency_contact_number = db.Column(db.String(15), nullable=False)
    
    license_number = db.Column(db.String(20), unique=True, nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    experience_years = db.Column(db.Integer, default=0)
    consultation_fee = db.Column(db.Numeric(10, 2), nullable=False)
    
    __table_args__ = (
        db.CheckConstraint('consultation_fee >= 0', name='check_consultation_fee_non_negative'),
        db.CheckConstraint('experience_years >= 0', name='check_doctor_experience_years_non_negative'),
    )
    
    is_available = db.Column(db.Boolean, default=True)
    availability = db.Column(db.JSON, nullable=True)
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = db.relationship('User', back_populates='doctor', lazy='joined')
    department = db.relationship('Department', back_populates='doctors', lazy='joined')
    appointments = db.relationship('Appointment', back_populates='doctor', lazy=True)
    medical_records = db.relationship('MedicalRecord', back_populates='doctor', lazy=True)
    patients = db.relationship('Patient', back_populates='assigned_doctor', lazy=True)

    def __repr__(self):
        return f"<Doctor {self.specialization}>"
