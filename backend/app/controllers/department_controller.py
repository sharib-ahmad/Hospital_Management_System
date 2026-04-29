# app/controllers/department_controller.py
from ..services.department import DepartmentService
from ..schemas.department import DepartmentCreateSchema
from ..utils.response import handle_response
from ..utils.request import validate_json
from ..extensions import cache

DEPARTMENTS_CACHE_KEY = 'all_departments_v4'

class DepartmentController:
    @staticmethod
    @cache.cached(timeout=600, key_prefix=DEPARTMENTS_CACHE_KEY)
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
        cache.delete(DEPARTMENTS_CACHE_KEY)
        
        return handle_response(
            success=True,
            message="Department created successfully",
            data=department
        )

    @staticmethod
    def update_department(department_id):
        data, error = validate_json()
        if error:
            return error
        
        department = DepartmentService.get_department_by_id(department_id)
        if not department:
            return handle_response(
                success=False,
                message="Department not found",
                status_code=404
            )
        
        updated_dept = DepartmentService.update_department(department, data)
        
        # Invalidate departments cache
        cache.delete(DEPARTMENTS_CACHE_KEY)
        
        return handle_response(
            success=True,
            message="Department updated successfully",
            data=updated_dept
        )

    @staticmethod
    def delete_department(department_id):
        department = DepartmentService.get_department_by_id(department_id)
        if not department:
            return handle_response(
                success=False,
                message="Department not found",
                status_code=404
            )
        
        DepartmentService.delete_department(department)
        
        # Invalidate departments cache
        cache.delete(DEPARTMENTS_CACHE_KEY)
        
        return handle_response(
            success=True,
            message="Department deleted successfully"
        )
