# app/controllers/nurse_controller.py
from flask import request
from flask_jwt_extended import current_user
from ..services.nurse import NurseService
from ..schemas.nurse import NurseUpdateSchema
from ..utils.response import handle_response
from ..utils.request import validate_json
from ..errors import NotFoundError
from ..extensions import cache

class NurseController:
    @staticmethod
    def get_nurses():
        dept_id = request.args.get('department_id')
        return NurseController._get_nurses_internal(dept_id)

    @staticmethod
    @cache.memoize(timeout=600)
    def _get_nurses_internal(dept_id):
        if dept_id:
            nurses = NurseService.get_nurses_by_department(dept_id)
        else:
            nurses = NurseService.get_all_nurses()
        
        return handle_response(
            success=True,
            message="Nurses retrieved successfully",
            data=nurses
        )

    @staticmethod
    @cache.memoize(timeout=600)
    def get_nurse(nurse_code):
        nurse = NurseService.get_nurse_by_code(nurse_code)
        if not nurse:
            raise NotFoundError("Nurse not found")

        return handle_response(
            success=True,
            message="Nurse retrieved successfully",
            data=nurse
        )

    @staticmethod
    def update_nurse(nurse_code):
        data, error = validate_json()
        if error:
            return error

        validated_data = NurseUpdateSchema(**data)
        nurse = NurseService.update_nurse(nurse_code, validated_data)
        if nurse == "DEPARTMENT_NOT_FOUND":
            raise NotFoundError("Department not found")
        if not nurse:
            raise NotFoundError("Nurse not found")

        # Invalidate nurse caches
        cache.delete_memoized(NurseController.get_nurse, nurse_code)
        cache.delete_memoized(NurseController._get_nurses_internal)

        # Invalidate department cache since staff counts might have changed
        from .department_controller import DEPARTMENTS_CACHE_KEY
        cache.delete(DEPARTMENTS_CACHE_KEY)

        return handle_response(
            success=True,
            message="Nurse updated successfully",
            data=nurse
        )

    @staticmethod
    def get_me():
        nurse = NurseService.get_nurse_by_id(current_user.id)
        if not nurse:
            raise NotFoundError("Nurse profile not found")
        return handle_response(success=True, message="Profile retrieved successfully", data=nurse)

    @staticmethod
    def update_me():
        data, error = validate_json()
        if error:
            return error

        current_nurse = NurseService.get_nurse_by_id(current_user.id)
        if not current_nurse:
            raise NotFoundError("Nurse profile not found")

        validated_data = NurseUpdateSchema(**data)
        nurse = NurseService.update_nurse(current_nurse.nurse_code, validated_data)

        if nurse == "DEPARTMENT_NOT_FOUND":
            raise NotFoundError("Department not found")
        if not nurse:
            raise NotFoundError("Nurse not found")

        cache.delete_memoized(NurseController.get_nurse, current_nurse.nurse_code)
        cache.delete_memoized(NurseController._get_nurses_internal)

        from .department_controller import DEPARTMENTS_CACHE_KEY
        cache.delete(DEPARTMENTS_CACHE_KEY)

        return handle_response(success=True, message="Profile updated successfully", data=nurse)
