# app/api_models/doctor_models.py
from flask_restx import fields

class DoctorModels:
    def __init__(self, api):
        self.department = api.model('Department', {
            'id': fields.Integer(readOnly=True),
            'name': fields.String(required=True),
            'description': fields.String
        })

        self.doctor_base = api.model('DoctorBase', {
            'specialization': fields.String(required=True),
            'experience_years': fields.Integer,
            'consultation_fee': fields.Fixed(decimals=2, required=True),
            'is_available': fields.Boolean,
            'department_id': fields.Integer(required=True)
        })

        self.doctor_detail = api.inherit('DoctorDetail', self.doctor_base, {
            'id': fields.String(readOnly=True, description="User UUID"),
            'full_name': fields.String(attribute='user.full_name'),
            'email': fields.String(attribute='user.email'),
            'department_name': fields.String(attribute='department.name')
        })

        self.department_response = api.model('DepartmentResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.List(fields.Nested(self.department))
        })

        self.doctor_response = api.model('DoctorResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.Nested(self.doctor_detail)
        })

        self.doctor_list_response = api.model('DoctorListResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.List(fields.Nested(self.doctor_detail))
        })
