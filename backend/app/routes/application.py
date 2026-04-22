from flask_restx import Namespace, Resource
from ..api_models.application_model import ApplicationModels
from ..controllers.application_controller import ApplicationController
from ..utils.role import role_required
from ..utils.enum import UserRole

application_ns = Namespace('applications', description='Application related operations')
application_models = ApplicationModels(application_ns)


@application_ns.route('')
class ApplicationList(Resource):
    @role_required(UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN)
    @application_ns.marshal_with(application_models.application_list_response)
    def get(self):
        """List applications based on role permissions"""
        return ApplicationController.get_applications()

@application_ns.route('/patient')
class PatientApplication(Resource):
    @role_required(UserRole.USER)
    @application_ns.expect(application_models.patient_create)
    @application_ns.marshal_with(application_models.patient_response, code=201)
    def post(self):
        """Create a new patient application"""
        return ApplicationController.create_patient_application()

@application_ns.route('/doctor')
class DoctorApplication(Resource):
    @role_required(UserRole.USER)
    @application_ns.expect(application_models.doctor_create)
    @application_ns.marshal_with(application_models.doctor_response, code=201)
    def post(self):
        """Create a new doctor application"""
        return ApplicationController.create_doctor_application()

@application_ns.route('/nurse')
class NurseApplication(Resource):
    @role_required(UserRole.USER)
    @application_ns.expect(application_models.nurse_create)
    @application_ns.marshal_with(application_models.nurse_response, code=201)
    def post(self):
        """Create a new nurse application"""
        return ApplicationController.create_nurse_application()

@application_ns.route('/<int:application_id>/approve')
class ApproveApplication(Resource):
    @role_required(UserRole.ADMIN, UserRole.DOCTOR)
    @application_ns.marshal_with(application_models.generic_response)
    def post(self, application_id):
        """Approve an application (Triggers background job)"""
        return ApplicationController.approve_application(application_id)

@application_ns.route('/<int:application_id>/reject')
class RejectApplication(Resource):
    @role_required(UserRole.ADMIN, UserRole.DOCTOR)
    @application_ns.expect(application_models.rejection_reason)
    @application_ns.marshal_with(application_models.generic_response)
    def post(self, application_id):
        """Reject an application"""
        return ApplicationController.reject_application(application_id)