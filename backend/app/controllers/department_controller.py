# app/controllers/department_controller.py
from ..services.department import DepartmentService
from ..schemas.department import DepartmentCreateSchema
from ..utils.response import handle_response
from ..utils.request import validate_json
from ..extensions import cache

class DepartmentController:
    @staticmethod
    @cache.cached(timeout=600, key_prefix='all_departments')
    def get_departments():
        departments = DepartmentService.get_all_departments()
        return handle_response(
            success=True,
            message="Departments retrieved successfully",
            data=departments
        )

    @staticmethod
    def create_department():
        data, error = validate_json()
        if error:
            return error
            
        validated_data = DepartmentCreateSchema(**data)
        department = DepartmentService.create_department(validated_data)
        
        # Invalidate departments cache
        cache.delete('all_departments')
        
        return handle_response(
            success=True,
            message="Department created successfully",
            data=department
        )
