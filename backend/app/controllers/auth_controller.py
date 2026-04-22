# app/controllers/auth_controller.py

from flask import request
from pydantic import ValidationError
from ..schemas.auth import UserRegisterSchema, UserLoginSchema
from ..services.auth import AuthService
from ..utils.response import handle_response
from ..utils.request import validate_json

class AuthController:
    @staticmethod
    def register():
        data, error = validate_json()
        if error:
            return error

        try:
            validated = UserRegisterSchema(**data)
            return AuthService.register_user(validated)
        except ValidationError as e:
            return handle_response(success=False, message="Validation Error", errors=e.errors(), status_code=400)

    @staticmethod
    def login():
        data, error = validate_json()
        if error:
            return error

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