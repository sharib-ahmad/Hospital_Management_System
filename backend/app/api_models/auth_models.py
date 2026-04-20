# app/api_models/auth_models.py
from flask_restx import fields
from ..utils.enum import UserRole, EnumField

class AuthModels:
    def __init__(self, api):

        self.register = api.model('Register', {
            'username': fields.String(required=True),
            'full_name': fields.String(required=True),
            'email': fields.String(required=True),
            'password': fields.String(required=True),
            'address': fields.String(required=False),
            'phone_number': fields.String(required=False),
            'pincode': fields.String(required=False),
        })

        self.login = api.model('Login', {
            'username': fields.String(required=True),
            'password': fields.String(required=True)
        })

        self.user = api.model('User', {
            'username': fields.String,
            'full_name': fields.String,
            'email': fields.String,
            'address': fields.String,
            'phone_number': fields.String,
            'pincode': fields.String,
            'role': EnumField(UserRole)
        })

        self.error_detail = api.model('ErrorDetail', {
            'loc': fields.List(fields.Raw, description="Location of the error"),
            'msg': fields.String(description="Error message"),
            'type': fields.String(description="Error type"),
            'url': fields.String(description="Error help URL")
        })
        
        self.response_model = api.model('UserResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.Nested(self.user, skip_none=True),
            'errors': fields.List(fields.Nested(self.error_detail), skip_none=True)
        })