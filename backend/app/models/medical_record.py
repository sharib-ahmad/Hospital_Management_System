from ..extensions import db
from ..utils.time import utc_now
import uuid

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    patient_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('doctors.id'), nullable=False)
    appointment_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('appointments.id'), nullable=True)
    
    diagnosis = db.Column(db.Text, nullable=False)
    treatment = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    patient = db.relationship('Patient', back_populates='medical_records')
    doctor = db.relationship('Doctor', back_populates='medical_records')
    appointment = db.relationship('Appointment', back_populates='medical_records')

    def __repr__(self):
        return f"<MedicalRecord {self.id} - Patient: {self.patient_id}>"
