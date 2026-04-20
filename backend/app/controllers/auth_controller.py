# app/controllers/auth_controller.py

from flask import request
from pydantic import ValidationError
from ..schemas.auth import UserRegisterSchema, UserLoginSchema
from ..services.auth import AuthService
from ..utils.response import handle_response

class AuthController:
    @staticmethod
    def register():
        
        
        if not request.is_json:
            return handle_response(success=False, message="Content-Type must be application/json", status_code=400)

        data = request.get_json()
        if not data:
            return handle_response(success=False, message="Invalid JSON body", status_code=400)

        try:
            validated = UserRegisterSchema(**data)
            return AuthService.register_user(validated)
        except ValidationError as e:
            return handle_response(success=False, message="Validation Error", errors=e.errors(), status_code=400)

    @staticmethod
    def login():
        if not request.is_json:
            return handle_response(success=False, message="Content-Type must be application/json", status_code=400)

        data = request.get_json()
        if not data:
            return handle_response(success=False, message="Invalid JSON body", status_code=400)

        try:
            validated = UserLoginSchema(**data)
            return AuthService.login_user(validated)
        except ValidationError as e:
            return handle_response(success=False, message="Validation Error", errors=e.errors(), status_code=400)

    @staticmethod
    def logout():
        return AuthService.logout_user()

    @staticmethod
    def refresh():
        return AuthService.refresh_token()