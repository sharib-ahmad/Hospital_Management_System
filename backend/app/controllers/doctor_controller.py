# app/controllers/doctor_controller.py
from flask import request
from ..services.doctor import DoctorService
from ..schemas.doctor import DoctorUpdateSchema
from pydantic import ValidationError
from ..utils.response import handle_response
from ..utils.request import validate_json

class DoctorController:

    @staticmethod
    def get_doctors():
        dept_id = request.args.get('department_id', type=str)
        if dept_id:
            doctors = DoctorService.get_doctors_by_department(dept_id)
        else:
            doctors = DoctorService.get_all_doctors()
        
        return handle_response(
            success=True,
            message="Doctors retrieved successfully",
            data=doctors
        )

    @staticmethod
    def get_doctor(doctor_code):
        doctor = DoctorService.get_doctor_by_code(doctor_code)
        if not doctor:
            return handle_response(
                success=False,
                message="Doctor not found",
                status_code=404
            )
        return handle_response(
            success=True,
            message="Doctor retrieved successfully",
            data=doctor
        )

    @staticmethod
    def update_doctor(doctor_code):
        data, error = validate_json()
        if error:
            return error
        try:
            validated_data = DoctorUpdateSchema(**data)
            doctor = DoctorService.update_doctor(doctor_code, validated_data)
            if doctor == "DEPARTMENT_NOT_FOUND":
                return handle_response(
                    success=False,
                    message="Department not found",
                    status_code=404
                )
            if not doctor:
                return handle_response(
                    success=False,
                    message="Doctor not found",
                    status_code=404
                )
            return handle_response(
                success=True,
                message="Doctor updated successfully",
                data=doctor
            )
        except ValidationError as e:
            return handle_response(
                success=False,
                message="Validation Error",
                errors=e.errors(),
                status_code=400
            )
