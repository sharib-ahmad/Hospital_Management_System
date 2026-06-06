from ..extensions import db
from ..utils.time import utc_now
from ..utils.enum import Gender, BloodGroup

class Pharmacist(db.Model):
    __tablename__ = 'pharmacists'

    id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True)
    pharmacist_code = db.Column(db.String(20), unique=True, nullable=False) # e.g., "PHM-2606-A1B"
    department_id = db.Column(db.String(12), db.ForeignKey('departments.id'), nullable=False)
    
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum(Gender, name="gender_types"), nullable=False)
    blood_group = db.Column(db.Enum(BloodGroup, name="blood_groups"), nullable=False)
    emergency_contact_number = db.Column(db.String(15), nullable=False)
    
    shift = db.Column(db.String(20), nullable=False)  # e.g., "Day", "Night", "Rotating"
    experience_years = db.Column(db.Integer, default=0)
    license_number = db.Column(db.String(20), unique=True, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    availability = db.Column(db.JSON, nullable=True)
    
    __table_args__ = (
        db.CheckConstraint('experience_years >= 0', name='check_pharmacist_experience_years_non_negative'),
    )
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = db.relationship('User', back_populates='pharmacist', lazy='joined')
    department = db.relationship('Department', back_populates='pharmacists', lazy='joined')

    def __repr__(self):
        return f"<Pharmacist {self.id} - Department: {self.department_id}>"
