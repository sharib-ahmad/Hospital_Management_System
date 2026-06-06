import enum
from flask_restx import fields

class UserRole(enum.Enum):
    PATIENT = "patient"
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    USER = "user"
    PHARMACIST = "pharmacist"
    
class AppointmentStatus(enum.Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'

class ApplicationStatus(enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'

class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class BloodGroup(enum.Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"

class Relationship(enum.Enum):
    SELF = "Self"
    FATHER = "Father"
    MOTHER = "Mother"
    SPOUSE = "Spouse"
    SON = "Son"
    DAUGHTER = "Daughter"
    BROTHER = "Brother"
    SISTER = "Sister"
    OTHER = "Other"
    
    
class EnumField(fields.String):
    def __init__(self, enum_cls, **kwargs):
        self.enum_cls = enum_cls
        super().__init__(enum=[e.value for e in enum_cls], **kwargs)

    def format(self, value):
        if isinstance(value, enum.Enum):
            return value.value
        return value