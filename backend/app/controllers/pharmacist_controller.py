from flask import request
from flask_jwt_extended import current_user
from ..services.pharmacist import PharmacistService
from ..schemas.pharmacist import PharmacistUpdateSchema
from ..utils.response import handle_response
from ..utils.request import validate_json
from ..errors import NotFoundError
from ..extensions import cache

class PharmacistController:
    @staticmethod
    def get_pharmacists():
        dept_id = request.args.get('department_id')
        return PharmacistController._get_pharmacists_internal(dept_id)

    @staticmethod
    @cache.memoize(timeout=600)
    def _get_pharmacists_internal(dept_id):
        if dept_id:
            pharmacists = PharmacistService.get_pharmacists_by_department(dept_id)
        else:
            pharmacists = PharmacistService.get_all_pharmacists()
        
        return handle_response(
            success=True,
            message="Pharmacists retrieved successfully",
            data=pharmacists
        )

    @staticmethod
    @cache.memoize(timeout=600)
    def get_pharmacist(pharmacist_code):
        pharmacist = PharmacistService.get_pharmacist_by_code(pharmacist_code)
        if not pharmacist:
            raise NotFoundError("Pharmacist not found")

        return handle_response(
            success=True,
            message="Pharmacist retrieved successfully",
            data=pharmacist
        )

    @staticmethod
    def update_pharmacist(pharmacist_code):
        data, error = validate_json()
        if error:
            return error

        validated_data = PharmacistUpdateSchema(**data)
        pharmacist = PharmacistService.update_pharmacist(pharmacist_code, validated_data)
        if pharmacist == "DEPARTMENT_NOT_FOUND":
            raise NotFoundError("Department not found")
        if not pharmacist:
            raise NotFoundError("Pharmacist not found")

        # Invalidate caches
        cache.delete_memoized(PharmacistController.get_pharmacist, pharmacist_code)
        cache.delete_memoized(PharmacistController._get_pharmacists_internal)

        from .department_controller import DEPARTMENTS_CACHE_KEY
        cache.delete(DEPARTMENTS_CACHE_KEY)

        return handle_response(
            success=True,
            message="Pharmacist updated successfully",
            data=pharmacist
        )

    @staticmethod
    def get_me():
        pharmacist = PharmacistService.get_pharmacist_by_id(current_user.id)
        if not pharmacist:
            raise NotFoundError("Pharmacist profile not found")
        return handle_response(success=True, message="Profile retrieved successfully", data=pharmacist)

    @staticmethod
    def update_me():
        data, error = validate_json()
        if error:
            return error

        current_pharmacist = PharmacistService.get_pharmacist_by_id(current_user.id)
        if not current_pharmacist:
            raise NotFoundError("Pharmacist profile not found")

        validated_data = PharmacistUpdateSchema(**data)
        pharmacist = PharmacistService.update_pharmacist(current_pharmacist.pharmacist_code, validated_data)

        if pharmacist == "DEPARTMENT_NOT_FOUND":
            raise NotFoundError("Department not found")
        if not pharmacist:
            raise NotFoundError("Pharmacist not found")

        cache.delete_memoized(PharmacistController.get_pharmacist, current_pharmacist.pharmacist_code)
        cache.delete_memoized(PharmacistController._get_pharmacists_internal)

        from .department_controller import DEPARTMENTS_CACHE_KEY
        cache.delete(DEPARTMENTS_CACHE_KEY)

        return handle_response(success=True, message="Profile updated successfully", data=pharmacist)
