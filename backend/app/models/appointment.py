from ..extensions import db
from ..utils.time import utc_now
import uuid
from ..utils.enum import AppointmentStatus



class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    patient_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('doctors.id'), nullable=True)
    
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(AppointmentStatus, name="appointment_status"), default=AppointmentStatus.PENDING)
    reason = db.Column(db.Text)
    
    vitals_checked = db.Column(db.Boolean, default=False, server_default='false')
    appointment_type = db.Column(db.String(30), default='consultation', server_default='consultation')
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    patient = db.relationship('Patient', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')
    medical_record = db.relationship('MedicalRecord', back_populates='appointment', uselist=False)

    @property
    def doctor_name(self):
        if self.doctor and self.doctor.user:
            return self.doctor.user.full_name
        return "N/A - Standalone Vitals"

    @property
    def doctor_specialization(self):
        if self.doctor:
            return self.doctor.specialization
        return "Vitals Screening"

    @property
    def consultation_fee(self):
        if self.doctor:
            return self.doctor.consultation_fee
        return 0.0

    def __repr__(self):
        return f"<Appointment {self.appointment_date} - {self.status.value}>"
