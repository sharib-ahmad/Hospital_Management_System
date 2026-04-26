from ..extensions import db
from ..utils.time import utc_now

class PatientVital(db.Model):
    __tablename__ = 'patient_vitals'
    
    patient_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('patients.id'), primary_key=True)
    recorded_by = db.Column(db.UUID(as_uuid=True), db.ForeignKey('nurses.id'), nullable=False)

    systolic_bp = db.Column(db.Integer)
    diastolic_bp = db.Column(db.Integer)
    blood_sugar = db.Column(db.Float)
    pulse_rate = db.Column(db.Integer)
    temperature = db.Column(db.Float)
    respiration_rate = db.Column(db.Integer)

    notes = db.Column(db.Text)

    recorded_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    
    patient = db.relationship('Patient', back_populates='patient_vitals')
    nurse = db.relationship('Nurse', back_populates='patient_vitals')