# app/controllers/auth_controller.py

from pydantic import ValidationError
from app.schemas.auth import UserRegisterSchema, UserLoginSchema
from app.services.auth import AuthService
from app.utils.response import error_response


def register_controller(request):
    if not request.is_json:
        return error_response(message="Content-Type must be application/json")

    data = request.get_json()

    if not data:
        return error_response(message="Invalid JSON body")

    try:
        validated = UserRegisterSchema(**data)
    except ValidationError as e:
        return error_response(errors=e.errors())

    # pass validated data (not raw)
    return AuthService.register_user(validated)


def login_controller(request):
    if not request.is_json:
        return error_response(message="Content-Type must be application/json")

    data = request.get_json()

    if not data:
        return error_response(message="Invalid JSON body")

    try:
        validated = UserLoginSchema(**data)
    except ValidationError as e:
        return error_response(errors=e.errors())

    return AuthService.login_user(validated)