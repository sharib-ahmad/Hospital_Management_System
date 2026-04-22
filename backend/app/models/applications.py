from ..extensions import db
from ..utils.enum import UserRole, ApplicationStatus, Gender, BloodGroup

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    role_applied = db.Column(db.Enum(UserRole, name="application_roles"), nullable=False)
    status = db.Column(db.Enum(ApplicationStatus, name="application_status"), default=ApplicationStatus.PENDING)
    reason = db.Column(db.Text)
    
    #Patients things[optionals]
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum(Gender, name="gender_types"))
    blood_group = db.Column(db.Enum(BloodGroup, name="blood_groups"))
    medical_history = db.Column(db.Text)
    emergency_contact_number = db.Column(db.String(15))
    
    # Role-specific things [optionals, shared across roles]
    specialization = db.Column(db.String(100))
    experience_years = db.Column(db.Integer, default=0)
    consultation_fee = db.Column(db.Numeric(10, 2)) 
    license_number = db.Column(db.String(20), unique=True)
    department_id = db.Column(db.String(12), db.ForeignKey('departments.id'))
    shift = db.Column(db.String(20))  # e.g., "Day", "Night", "Rotating"

    __table_args__ = (
        db.CheckConstraint('experience_years >= 0', name='check_app_experience_years_non_negative'),
    )

    # Relationships
    user = db.relationship('User', back_populates='applications')

    def __repr__(self):
        return f"<Application {self.id} for {self.role_applied.value}>"