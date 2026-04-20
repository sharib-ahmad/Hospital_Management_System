# app/controllers/doctor_controller.py
from flask import request
from ..services.doctor import DoctorService
from ..schemas.doctor import DepartmentCreateSchema, DoctorCreateSchema ,DoctorUpdateSchema
from pydantic import ValidationError
from ..utils.response import handle_response

class DoctorController:
    @staticmethod
    def get_departments():
        departments = DoctorService.get_all_departments()
        return handle_response(
            success=True,
            message="Departments retrieved successfully",
            data=departments
        )

    @staticmethod
    def create_department():
        try:
            data = request.get_json()
            validated_data = DepartmentCreateSchema(**data)
            department = DoctorService.create_department(validated_data)
            return handle_response(
                success=True,
                message="Department created successfully",
                data=department
            )
        except ValidationError as e:
            return handle_response(
                success=False,
                message="Validation Error",
                errors=e.errors(),
                status_code=400
            )

    @staticmethod
    def create_doctor():
        try:
            data = request.get_json()
            validated_data = DoctorCreateSchema(**data)
            doctor = DoctorService.create_doctor(validated_data)
            return handle_response(
                success=True,
                message="Doctor profile created successfully",
                data=doctor
            )
        except ValidationError as e:
            return handle_response(
                success=False,
                message="Validation Error",
                errors=e.errors(),
                status_code=400
            )

    @staticmethod
    def get_doctors():
        dept_id = request.args.get('department_id', type=int)
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
    def get_doctor(doctor_id):
        doctor = DoctorService.get_doctor_by_id(doctor_id)
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
    def update_doctor(doctor_id):
        try:
            data = request.get_json()
            validated_data = DoctorUpdateSchema(**data)
            doctor = DoctorService.update_doctor(doctor_id, validated_data)
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
