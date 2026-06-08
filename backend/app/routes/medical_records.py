# app/routes/medical_records.py
from flask import request, send_file
from flask_restx import Namespace, Resource
from werkzeug.datastructures import FileStorage
from ..controllers.medical_records_controller import MedicalRecordsController
from ..api_models.medical_record_models import MedicalRecordModels
from ..utils.role import role_required
from ..utils.enum import UserRole
from ..utils.response import handle_response

medical_records_ns = Namespace('medical-records', description='Medical records operations')
medical_record_models = MedicalRecordModels(medical_records_ns)

# Parser for file upload documentation in Swagger
upload_parser = medical_records_ns.parser()
upload_parser.add_argument('file', type=FileStorage, location='files', required=True, help='The attachment file (PDF/Image)')


@medical_records_ns.route('')
class MedicalRecordList(Resource):
    @medical_records_ns.doc('create_medical_record', security='Bearer Auth')
    @medical_records_ns.expect(medical_record_models.record_create)
    @medical_records_ns.marshal_with(medical_record_models.record_response)
    @role_required(UserRole.DOCTOR)
    def post(self):
        """Create a new medical record for an assigned patient (Doctor only)"""
        return MedicalRecordsController.create_record()


@medical_records_ns.route('/my')
class MyMedicalRecords(Resource):
    @medical_records_ns.doc('get_my_medical_records', security='Bearer Auth')
    @medical_records_ns.marshal_with(medical_record_models.record_list_response)
    @role_required(UserRole.USER)
    def get(self):
        """Get all medical records for the current user's patient profiles"""
        return MedicalRecordsController.get_my_records()


@medical_records_ns.route('/patient/<string:patient_id>')
@medical_records_ns.param('patient_id', 'The patient UUID')
class PatientMedicalRecords(Resource):
    @medical_records_ns.doc('get_patient_medical_records', security='Bearer Auth')
    @medical_records_ns.marshal_with(medical_record_models.record_list_response)
    @role_required(UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE)
    def get(self, patient_id):
        """Get all medical records for a specific patient (Admin/Doctor/Nurse only)"""
        return MedicalRecordsController.get_records_for_patient(patient_id)


@medical_records_ns.route('/<string:record_id>')
@medical_records_ns.param('record_id', 'The medical record UUID')
class MedicalRecordDetail(Resource):
    @medical_records_ns.doc('get_medical_record', security='Bearer Auth')
    @medical_records_ns.marshal_with(medical_record_models.record_response)
    @role_required(UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE, UserRole.USER)
    def get(self, record_id):
        """Get a single medical record by ID"""
        return MedicalRecordsController.get_record_by_id(record_id)


@medical_records_ns.route('/<string:record_id>/parse-prescription')
@medical_records_ns.param('record_id', 'The medical record UUID')
class ParsePrescription(Resource):
    @medical_records_ns.doc('parse_prescription', security='Bearer Auth')
    @role_required(UserRole.USER)
    def get(self, record_id):
        """Parse the medical record's prescription text and match available medicines"""
        return MedicalRecordsController.parse_prescription(record_id)


@medical_records_ns.route('/upload')
class UploadMedicalRecordFile(Resource):
    @medical_records_ns.doc('upload_medical_record_file', security='Bearer Auth')
    @medical_records_ns.expect(upload_parser)
    @role_required(UserRole.DOCTOR)
    def post(self):
        """Upload a new attachment file (PDF/Image) for a medical record (Doctor only)"""
        args = upload_parser.parse_args()
        uploaded_file = args['file']
        
        if not uploaded_file:
            return handle_response(success=False, message="File is required", status_code=400)
            
        return MedicalRecordsController.upload_file(uploaded_file)


@medical_records_ns.route('/<string:record_id>/file')
@medical_records_ns.param('record_id', 'The medical record UUID')
class DownloadMedicalRecordFile(Resource):
    @medical_records_ns.doc('download_medical_record_file', security='Bearer Auth')
    @role_required(UserRole.USER, UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN)
    def get(self, record_id):
        """Download the actual physical file of a medical record's attachment"""
        res = MedicalRecordsController.get_file(record_id)
        if isinstance(res, tuple) and len(res) == 3:
            # Error returned
            return handle_response(success=False, message=res[1], status_code=res[2])
            
        file_path, file_name, status = res
        return send_file(file_path, as_attachment=True, download_name=file_name)

