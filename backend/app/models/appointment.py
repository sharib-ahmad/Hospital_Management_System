from ..extensions import db
from ..utils.time import utc_now
import uuid
from ..utils.enum import AppointmentStatus



class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    patient_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('doctors.id'), nullable=False)
    
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(AppointmentStatus, name="appointment_status"), default=AppointmentStatus.PENDING)
    reason = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    patient = db.relationship('Patient', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')
    medical_record = db.relationship('MedicalRecord', back_populates='appointment', uselist=False)

    def __repr__(self):
        return f"<Appointment {self.appointment_date} - {self.status.value}>"
