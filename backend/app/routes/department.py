# app/routes/department.py
from flask_restx import Namespace, Resource
from ..api_models.department_models import DepartmentModels
from ..controllers.department_controller import DepartmentController
from ..utils.role import role_required
from ..utils.enum import UserRole

department_ns = Namespace('departments', description='Department related operations')
department_models = DepartmentModels(department_ns)

@department_ns.route('/')
class DepartmentList(Resource):
    @department_ns.marshal_with(department_models.department_response)
    def get(self):
        """List all departments"""
        return DepartmentController.get_departments()

    @role_required(UserRole.ADMIN)
    @department_ns.expect(department_models.department)
    @department_ns.marshal_with(department_models.department_response)
    def post(self):
        """Create a new department (Admin only)"""
        return DepartmentController.create_department()
