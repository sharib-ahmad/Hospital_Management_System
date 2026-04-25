# app/api_models/department_models.py
from flask_restx import fields

class DepartmentModels:
    def __init__(self, api):
        self.department = api.model('Department', {
            'department_id': fields.String(required=True),
            'name': fields.String(required=True),
            'description': fields.String
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
            'data': fields.List(fields.Nested(self.department), skip_none=True),
            'errors': fields.List(fields.Nested(self.error_details), skip_none=True)
        })
