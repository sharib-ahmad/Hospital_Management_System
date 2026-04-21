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

    created_at = db.Column(db.DateTime,
                           default=utc_now,
                           nullable=False)

    updated_at = db.Column(db.DateTime,
                           default=utc_now,
                           onupdate=utc_now,
                           nullable=False)

    # Relationships
    doctor = db.relationship('Doctor', back_populates='user', uselist=False)
    patient = db.relationship('Patient', back_populates='user', uselist=False)
    nurse = db.relationship('Nurse', back_populates='user', uselist=False)
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

    @property
    def role_value(self):
        return self.role.value

    def __repr__(self):
        return f"<User {self.username} ({self.email}) - {self.role.value}>"
