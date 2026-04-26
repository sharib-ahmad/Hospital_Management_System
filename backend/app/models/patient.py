from ..extensions import db
from ..utils.enum import Gender, BloodGroup
from ..utils.time import utc_now

class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True)
    
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum(Gender, name="gender_types"))
    blood_group = db.Column(db.Enum(BloodGroup, name="blood_groups"))
    medical_history = db.Column(db.Text)
    emergency_contact_number = db.Column(db.String(15))
    assigned_doctor_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('doctors.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = db.relationship('User', back_populates='patient')
    patient_vitals = db.relationship('PatientVital', back_populates='patient')
    appointments = db.relationship('Appointment', back_populates='patient', lazy=True)
    medical_records = db.relationship('MedicalRecord', back_populates='patient', lazy=True)
    assigned_doctor = db.relationship('Doctor', back_populates='patients')

    def __repr__(self):
        return f"<Patient {self.id}>"
