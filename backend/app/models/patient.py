from ..extensions import db
import uuid

class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True)
    
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    blood_group = db.Column(db.String(5))
    medical_history = db.Column(db.Text)
    emergency_contact_number = db.Column(db.String(15))

    # Relationships
    user = db.relationship('User', back_populates='patient')
    appointments = db.relationship('Appointment', back_populates='patient', lazy=True)
    medical_records = db.relationship('MedicalRecord', back_populates='patient', lazy=True)

    def __repr__(self):
        return f"<Patient {self.id}>"
