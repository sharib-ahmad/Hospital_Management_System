# app/controllers/department_controller.py
from ..services.department import DepartmentService
from ..schemas.department import DepartmentCreateSchema
from pydantic import ValidationError
from ..utils.response import handle_response
from ..utils.request import validate_json

class DepartmentController:
    @staticmethod
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
        try:
            validated_data = DepartmentCreateSchema(**data)
            department = DepartmentService.create_department(validated_data)
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
