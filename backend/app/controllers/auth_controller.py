# app/controllers/auth_controller.py

from flask import request, jsonify, make_response
from pydantic import ValidationError
from flask_jwt_extended import set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from ..schemas.auth import UserRegisterSchema, UserLoginSchema, UserResetPasswordSchema
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
            # service returns a tuple (dict, status_code)
            resp_data, status_code = AuthService.login_user(validated)
            
            if status_code != 200:
                return resp_data, status_code
                
            # Create a flask response
            response = make_response(jsonify(resp_data), status_code)
            
            # Set cookies
            access_token = resp_data['data']['access_token']
            refresh_token = resp_data['data']['refresh_token']
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            
            return response
            
        except ValidationError as e:
            return handle_response(success=False, message="Validation Error", errors=e.errors(), status_code=400)

    @staticmethod
    def get_all_users():
        # Invalidate cache to ensure we get fresh credential data
        from .doctor_controller import DoctorController
        from ..extensions import cache
        cache.delete_memoized(DoctorController._get_doctors_internal)
        
        resp_data, status_code = AuthService.get_all_users()
        return resp_data, status_code

    @staticmethod
    def logout():
        resp_data, status_code = AuthService.logout_user()
        response = make_response(jsonify(resp_data), status_code)
        unset_jwt_cookies(response)
        return response

    @staticmethod
    def refresh():
        resp_data, status_code = AuthService.refresh_token()
        if status_code != 200:
            return resp_data, status_code
            
        response = make_response(jsonify(resp_data), status_code)
        access_token = resp_data['data']['access_token']
        set_access_cookies(response, access_token)
        return response

    @staticmethod
    def reset_password():
        data, error = validate_json()
        if error:
            return error

        try:
            validated = UserResetPasswordSchema(**data)
            resp_data, status_code = AuthService.reset_password(validated)
            return resp_data, status_code
        except ValidationError as e:
            return handle_response(success=False, message="Validation Error", errors=e.errors(), status_code=400)