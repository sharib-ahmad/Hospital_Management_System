from ..extensions import db
from ..utils.security import hash_password, verify_password
from ..utils.time import utc_now
from ..utils.enum import UserRole
import uuid


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=False)

    address = db.Column(db.String(255))
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    pincode = db.Column(db.String(10))

    role = db.Column(db.Enum(UserRole, name="user_roles"),
                     nullable=False, default=UserRole.USER)

    is_active = db.Column(db.Boolean, default=True)

    tokens_valid_after = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime,
                           default=utc_now,
                           nullable=False)

    updated_at = db.Column(db.DateTime,
                           default=utc_now,
                           onupdate=utc_now,
                           nullable=False)

    # Relationships
    doctor = db.relationship('Doctor', back_populates='user', uselist=False)
    patients = db.relationship('Patient', back_populates='user', lazy=True)
    nurse = db.relationship('Nurse', back_populates='user', uselist=False)
    pharmacist = db.relationship('Pharmacist', back_populates='user', uselist=False)
    applications = db.relationship('Application', back_populates='user', lazy=True)
    token_blocklist = db.relationship('TokenBlocklist', back_populates='user', lazy=True)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = hash_password(password)

    def check_password(self, password):
        return verify_password(password, self.password_hash)

    # Flattened Profile Properties for UI
    @property
    def specialization(self):
        return self.doctor.specialization if self.doctor else None

    @property
    def experience_years(self):
        if self.doctor:
            return self.doctor.experience_years
        if self.nurse:
            return self.nurse.experience_years
        if self.pharmacist:
            return self.pharmacist.experience_years
        return None

    @property
    def license_number(self):
        if self.doctor:
            return self.doctor.license_number
        if self.nurse:
            return self.nurse.license_number
        if self.pharmacist:
            return self.pharmacist.license_number
        return None

    @property
    def department_id(self):
        if self.doctor:
            return self.doctor.department_id
        if self.nurse:
            return self.nurse.department_id
        if self.pharmacist:
            return self.pharmacist.department_id
        return None

    @property
    def shift(self):
        if self.doctor:
            return self.doctor.shift
        if self.nurse:
            return self.nurse.shift
        if self.pharmacist:
            return self.pharmacist.shift
        return None

    @property
    def blood_group(self):
        if self.doctor:
            return self.doctor.blood_group.value if self.doctor.blood_group else None
        if self.nurse:
            return self.nurse.blood_group.value if self.nurse.blood_group else None
        if self.pharmacist:
            return self.pharmacist.blood_group.value if self.pharmacist.blood_group else None
        return None

    @property
    def date_of_birth(self):
        if self.doctor:
            return self.doctor.date_of_birth.isoformat() if self.doctor.date_of_birth else None
        if self.nurse:
            return self.nurse.date_of_birth.isoformat() if self.nurse.date_of_birth else None
        if self.pharmacist:
            return self.pharmacist.date_of_birth.isoformat() if self.pharmacist.date_of_birth else None
        return None

    @property
    def medical_history(self):
        return None

    @property
    def gender(self):
        if self.doctor:
            return self.doctor.gender.value if self.doctor.gender else None
        if self.nurse:
            return self.nurse.gender.value if self.nurse.gender else None
        if self.pharmacist:
            return self.pharmacist.gender.value if self.pharmacist.gender else None
        return None

    @property
    def emergency_contact_number(self):
        if self.doctor:
            return self.doctor.emergency_contact_number
        if self.nurse:
            return self.nurse.emergency_contact_number
        if self.pharmacist:
            return self.pharmacist.emergency_contact_number
        return None

    @property
    def role_value(self):
        return self.role.value

    def __repr__(self):
        return f"<User {self.username} ({self.email}) - {self.role.value}>"
