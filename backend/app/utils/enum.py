
import enum
from flask_restx import fields

class UserRole(enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    RECEPTIONIST = "receptionist"
    PATIENT = "patient"
    
    
class AppointmentStatus(enum.Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    
class EnumField(fields.String):
    def __init__(self, enum_cls, **kwargs):
        self.enum_cls = enum_cls
        super().__init__(enum=[e.value for e in enum_cls], **kwargs)

    def format(self, value):
        if isinstance(value, enum.Enum):
            return value.value
        return value