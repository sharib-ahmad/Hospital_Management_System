# app/api_models/nurse_models.py
from flask_restx import fields
from ..utils.enum import EnumField, Gender, BloodGroup

class NurseModels:
    def __init__(self, api):
        self.nurse_base = api.model('NurseBase', {
            'experience_years': fields.Integer,
            'license_number': fields.String(required=True),
            'shift': fields.String(required=True),
            'date_of_birth': fields.Date(required=True),
            'gender': EnumField(Gender, required=True),
            'blood_group': EnumField(BloodGroup, required=True),
            'emergency_contact_number': fields.String(required=True),
            'is_available': fields.Boolean,
            'department_id': fields.String(required=True)
        })

        self.nurse_detail = api.inherit('NurseDetail', self.nurse_base, {
            'id': fields.String(readOnly=True, description="User UUID"),
            'nurse_code': fields.String(readOnly=True),
            'username': fields.String(attribute='user.username'),
            'full_name': fields.String(attribute='user.full_name'),
            'email': fields.String(attribute='user.email'),
            'role': fields.String(attribute='user.role_value'),
            'address': fields.String(attribute='user.address'),
            'phone_number': fields.String(attribute='user.phone_number'),
            'pincode': fields.String(attribute='user.pincode'),
            'department_name': fields.String(attribute='department.name'),
            'created_at': fields.DateTime(readOnly=True),
            'updated_at': fields.DateTime(readOnly=True)
        })

        self.nurse_response = api.model('NurseResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.Nested(self.nurse_detail)
        })
        
        self.error_details = api.model('ErrorDetails', {
            'loc': fields.List(fields.Raw, description="Location of the error"),
            'msg': fields.String(description="Error message"),
            'type': fields.String(description="Error type"),
            'url': fields.String(description="Error URL")
        })

        self.nurse_list_response = api.model('NurseListResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.List(fields.Nested(self.nurse_detail), skip_none=True),
            'errors': fields.List(fields.Nested(self.error_details), skip_none=True)
        })
