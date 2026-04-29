# app/controllers/doctor_controller.py
from flask import request
from ..services.doctor import DoctorService
from ..schemas.doctor import DoctorUpdateSchema
from ..utils.response import handle_response
from ..utils.request import validate_json
from ..errors import NotFoundError
from ..extensions import cache

class DoctorController:
    @staticmethod
    def get_doctors():
        dept_id = request.args.get('department_id')
        return DoctorController._get_doctors_internal(dept_id)

    @staticmethod
    @cache.memoize(timeout=600)
    def _get_doctors_internal(dept_id):
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
    @cache.memoize(timeout=600)
    def get_doctor(doctor_code):
        doctor = DoctorService.get_doctor_by_code(doctor_code)
        if not doctor:
            raise NotFoundError("Doctor not found")
            
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
            
        validated_data = DoctorUpdateSchema(**data)
        doctor = DoctorService.update_doctor(doctor_code, validated_data)
        
        if doctor == "DEPARTMENT_NOT_FOUND":
            raise NotFoundError("Department not found")
        if not doctor:
            raise NotFoundError("Doctor not found")
            
        # Invalidate doctor caches
        cache.delete_memoized(DoctorController.get_doctor, doctor_code)
        # Invalidate all doctor lists
        cache.delete_memoized(DoctorController._get_doctors_internal)
        
        # Invalidate department cache since staff counts might have changed
        from .department_controller import DEPARTMENTS_CACHE_KEY
        cache.delete(DEPARTMENTS_CACHE_KEY)
        
        return handle_response(
            success=True,
            message="Doctor updated successfully",
            data=doctor
        )
