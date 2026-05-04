from flask_restx import Namespace, Resource
from ..api_models.patient_models import PatientModels
from ..controllers.patient_controller import PatientController
from ..utils.role import role_required
from ..utils.enum import UserRole

patient_ns = Namespace('patients', description='Patient operations')
patient_models = PatientModels(patient_ns)

@patient_ns.route('/')
class PatientList(Resource):
    @role_required(UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE)
    @patient_ns.marshal_with(patient_models.patient_list_response)
    def get(self):
        """List all patients"""
        return PatientController.get_patients()

@patient_ns.route('/<string:patient_id>')
class PatientDetail(Resource):
    @role_required(UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE)
    @patient_ns.marshal_with(patient_models.patient_list_response) # Using same response model for simplicity or wrap in data
    def get(self, patient_id):
        """Get patient details"""
        return PatientController.get_patient(patient_id)
