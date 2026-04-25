# app/routes/doctor.py
from flask_restx import Namespace, Resource
from ..api_models.doctor_models import DoctorModels
from ..controllers.doctor_controller import DoctorController
from ..utils.role import role_required
from ..utils.enum import UserRole

doctor_ns = Namespace('doctors', description='Doctor operations')
doctor_models = DoctorModels(doctor_ns)

@doctor_ns.route('/')
class DoctorList(Resource):
    @doctor_ns.doc(params={'department_id': 'Filter by department ID'})
    @doctor_ns.marshal_with(doctor_models.doctor_list_response)
    def get(self):
        """List all doctors"""
        return DoctorController.get_doctors()

@doctor_ns.route('/<string:doctor_code>')
@doctor_ns.param('doctor_code', 'The doctor code')
class DoctorDetail(Resource):
    @doctor_ns.marshal_with(doctor_models.doctor_response)
    def get(self, doctor_code):
        """Get doctor details"""
        return DoctorController.get_doctor(doctor_code)

    @role_required(UserRole.ADMIN, UserRole.DOCTOR)
    @doctor_ns.expect(doctor_models.doctor_base)
    @doctor_ns.marshal_with(doctor_models.doctor_response)
    def put(self, doctor_code):
        """Update doctor details (Admin or own Doctor profile)"""
        # Note: In a real scenario, you'd add a check in the controller 
        # to ensure a doctor can only update their own profile.
        return DoctorController.update_doctor(doctor_code)
