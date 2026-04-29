# app/api_models/department_models.py
from flask_restx import fields

class DepartmentModels:
    def __init__(self, api):
        self.staff = api.model('Staff', {
            'doctors': fields.Integer(description="Number of doctors in the department"),
            'nurses': fields.Integer(description="Number of nurses in the department")
        })

        # Request Model (Input)
        self.department = api.model('Department', {
            'id': fields.String(required=True),
            'name': fields.String(required=True),
            'description': fields.String,
            'doctor_limit': fields.Integer,
            'nurse_limit': fields.Integer
        })

        # Response Model (Output)
        self.department_detail = api.inherit('DepartmentDetail', self.department, {
            'staff': fields.Nested(self.staff),
            'created_at': fields.DateTime(readOnly=True),
            'updated_at': fields.DateTime(readOnly=True)
        })

        self.error_details = api.model('ErrorDetails', {
            'loc': fields.List(fields.Raw, description="Location of the error"),
            'msg': fields.String(description="Error message"),
            'type': fields.String(description="Error type"),
            'url': fields.String(description="Error URL")
        })
        
        self.department_response = api.model('DepartmentResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.List(fields.Nested(self.department_detail), skip_none=True),
            'errors': fields.List(fields.Nested(self.error_details), skip_none=True)
        })
