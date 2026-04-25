# app/controllers/nurse_controller.py
from flask import request
from ..services.nurse import NurseService
from ..schemas.nurse import NurseUpdateSchema
from ..utils.response import handle_response
from ..utils.request import validate_json
from ..errors import NotFoundError

class NurseController:
    @staticmethod
    def get_nurses():
        dept_id = request.args.get('department_id')
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

        return handle_response(
            success=True,
            message="Nurse updated successfully",
            data=nurse
        )
