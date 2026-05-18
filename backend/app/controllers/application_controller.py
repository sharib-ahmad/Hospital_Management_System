from flask import request
from ..services.application import ApplicationService
from ..schemas.application import (
    PatientApplicationCreateSchema, 
    DoctorApplicationCreateSchema, 
    NurseApplicationCreateSchema
)
from pydantic import ValidationError
from ..utils.response import handle_response
from ..utils.request import validate_json
from flask_jwt_extended import current_user

class ApplicationController:
    @staticmethod
    def get_applications():
        return ApplicationService.get_all_applications()

    @staticmethod
    def get_my_applications():
        return ApplicationService.get_user_applications(current_user.id)

    @staticmethod
    def create_patient_application():
        data, error = validate_json()
        if error:
            return error
        try:
            validated_data = PatientApplicationCreateSchema(**data)
            return ApplicationService.create_patient_application(validated_data)
        except ValidationError as e:
            return handle_response(
                success=False,
                message="Validation Error",
                errors=e.errors(),
                status_code=400
            )

    @staticmethod
    def create_doctor_application():
        data, error = validate_json()
        if error:
            return error
        try:
            validated_data = DoctorApplicationCreateSchema(**data)
            return ApplicationService.create_doctor_application(validated_data)
        except ValidationError as e:
            return handle_response(
                success=False,
                message="Validation Error",
                errors=e.errors(),
                status_code=400
            )

    @staticmethod
    def create_nurse_application():
        data, error = validate_json()
        if error:
            return error
        try:
            validated_data = NurseApplicationCreateSchema(**data)
            return ApplicationService.create_nurse_application(validated_data)
        except ValidationError as e:
            return handle_response(
                success=False,
                message="Validation Error",
                errors=e.errors(),
                status_code=400
            )

    @staticmethod
    def approve_application(application_id):
        return ApplicationService.approve_application(application_id)

    @staticmethod
    def reject_application(application_id):
        data, error = validate_json()
        if error:
            return error
        reason = data.get('reason', None)
        return ApplicationService.reject_application(application_id, reason)