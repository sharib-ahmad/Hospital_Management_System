import enum
from flask_restx import fields

class EnumField(fields.Raw):
    def format(self, value):
        return value.value if isinstance(value, enum.Enum) else value

from .auth_models import AuthModels


