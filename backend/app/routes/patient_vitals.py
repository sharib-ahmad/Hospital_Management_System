# app/routes/patient_vitals.py
from flask_restx import Namespace, Resource
from ..controllers.patient_vitals_controller import PatientVitalsController
from ..api_models.patient_vital_models import PatientVitalModels
from ..utils.role import role_required
from ..utils.enum import UserRole

vitals_ns = Namespace('vitals', description='Patient vitals operations')
patient_vital_models = PatientVitalModels(vitals_ns)


@vitals_ns.route('')
class PatientVitalRecord(Resource):
    @vitals_ns.doc('record_vitals', security='Bearer Auth')
    @vitals_ns.expect(patient_vital_models.vital_create)
    @vitals_ns.marshal_with(patient_vital_models.vital_response)
    @role_required(UserRole.NURSE)
    def post(self):
        """Record or update patient vitals (Nurse only). Creates or updates the single vitals record per patient."""
        return PatientVitalsController.record_vitals()


@vitals_ns.route('/<string:patient_id>')
@vitals_ns.param('patient_id', 'The patient UUID')
class PatientVitalDetail(Resource):
    @vitals_ns.doc('get_patient_vitals', security='Bearer Auth')
    @vitals_ns.marshal_with(patient_vital_models.vital_list_response)
    @role_required(UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE, UserRole.USER)
    def get(self, patient_id):
        """Get the vitals history for a patient (Admin/Doctor/Nurse/User)"""
        return PatientVitalsController.get_vitals_for_patient(patient_id)


@vitals_ns.route('/my/export')
class PatientVitalExportDirect(Resource):
    @vitals_ns.doc('export_vitals_direct', security='Bearer Auth')
    @role_required(UserRole.USER)
    def get(self):
        """Download all registered patients' vitals directly as a CSV"""
        return PatientVitalsController.export_vitals_direct()


@vitals_ns.route('/my/export-job')
class PatientVitalExportJob(Resource):
    @vitals_ns.doc('export_vitals_job', security='Bearer Auth')
    @role_required(UserRole.USER)
    def post(self):
        """Trigger a background Celery task to compile and email all patients' vitals as CSV"""
        return PatientVitalsController.export_vitals_via_job()

