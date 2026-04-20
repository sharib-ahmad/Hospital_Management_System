# app/routes/doctor.py
from flask_restx import Namespace, Resource
from ..api_models.doctor_models import DoctorModels
from ..controllers.doctor_controller import DoctorController
from ..utils.role import role_required
from ..utils.enum import UserRole

doctor_ns = Namespace('doctors', description='Doctor and Department related operations')
doctor_models = DoctorModels(doctor_ns)

@doctor_ns.route('/departments')
class DepartmentList(Resource):
    @doctor_ns.marshal_with(doctor_models.department_response)
    def get(self):
        """List all departments"""
        return DoctorController.get_departments()

    @role_required(UserRole.ADMIN)
    @doctor_ns.expect(doctor_models.department)
    @doctor_ns.marshal_with(doctor_models.department_response)
    def post(self):
        """Create a new department (Admin only)"""
        return DoctorController.create_department()

@doctor_ns.route('/')
class DoctorList(Resource):
    @doctor_ns.doc(params={'department_id': 'Filter by department ID'})
    @doctor_ns.marshal_with(doctor_models.doctor_list_response)
    def get(self):
        """List all doctors"""
        return DoctorController.get_doctors()

    @role_required(UserRole.ADMIN)
    @doctor_ns.expect(doctor_models.doctor_base)
    @doctor_ns.marshal_with(doctor_models.doctor_response)
    def post(self):
        """Create a new doctor profile (Admin only)"""
        return DoctorController.create_doctor()

@doctor_ns.route('/<string:doctor_id>')
@doctor_ns.param('doctor_id', 'The doctor user UUID')
class DoctorDetail(Resource):
    @doctor_ns.marshal_with(doctor_models.doctor_response)
    def get(self, doctor_id):
        """Get doctor details"""
        return DoctorController.get_doctor(doctor_id)

    @role_required(UserRole.ADMIN, UserRole.DOCTOR)
    @doctor_ns.expect(doctor_models.doctor_base)
    @doctor_ns.marshal_with(doctor_models.doctor_response)
    def put(self, doctor_id):
        """Update doctor details (Admin or own Doctor profile)"""
        # Note: In a real scenario, you'd add a check in the controller 
        # to ensure a doctor can only update their own profile.
        return DoctorController.update_doctor(doctor_id)
