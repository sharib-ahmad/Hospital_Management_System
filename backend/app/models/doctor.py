from ..extensions import db

class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    
    specialization = db.Column(db.String(100), nullable=False)
    experience_years = db.Column(db.Integer, default=0)
    consultation_fee = db.Column(db.Numeric(10, 2), nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    # Relationships
    user = db.relationship('User', back_populates='doctor')
    department = db.relationship('Department', back_populates='doctors')
    appointments = db.relationship('Appointment', back_populates='doctor', lazy=True)
    medical_records = db.relationship('MedicalRecord', back_populates='doctor', lazy=True)

    def __repr__(self):
        return f"<Doctor {self.specialization}>"
