# app/api_models/doctor_models.py
from flask_restx import fields
from ..utils.enum import EnumField, Gender, BloodGroup

class DoctorModels:
    def __init__(self, api):
        self.doctor_base = api.model('DoctorBase', {
            'specialization': fields.String(required=True),
            'experience_years': fields.Integer,
            'consultation_fee': fields.Fixed(decimals=2, required=True),
            'license_number': fields.String(required=True),
            'shift': fields.String(required=True),
            'date_of_birth': fields.Date(required=True),
            'gender': EnumField(Gender, required=True),
            'blood_group': EnumField(BloodGroup, required=True),
            'emergency_contact_number': fields.String(required=True),
            'is_available': fields.Boolean,
            'department_id': fields.String(required=True)
        })

        self.doctor_detail = api.inherit('DoctorDetail', self.doctor_base, {
            'id': fields.String(readOnly=True, description="User UUID"),
            'full_name': fields.String(attribute='user.full_name'),
            'email': fields.String(attribute='user.email'),
            'department_name': fields.String(attribute='department.name'),
            'created_at': fields.DateTime(readOnly=True),
            'updated_at': fields.DateTime(readOnly=True)
        })

        self.doctor_response = api.model('DoctorResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.Nested(self.doctor_detail)
        })
        
        self.error_details = api.model('ErrorDetails', {
            'loc': fields.List(fields.Raw, description="Location of the error"),
            'msg': fields.String(description="Error message"),
            'type': fields.String(description="Error type"),
            'url': fields.String(description="Error URL")
        })

        self.doctor_list_response = api.model('DoctorListResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.List(fields.Nested(self.doctor_detail), skip_none=True),
            'errors': fields.List(fields.Nested(self.error_details), skip_none=True)
        })
