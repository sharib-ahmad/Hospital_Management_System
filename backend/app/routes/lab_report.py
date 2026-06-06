from flask import request, send_file
from flask_restx import Namespace, Resource
from werkzeug.datastructures import FileStorage
from ..services.lab_reports import LabReportService
from ..utils.role import role_required
from ..utils.enum import UserRole
from ..utils.response import handle_response

lab_reports_ns = Namespace('lab-reports', description='Patient clinical & lab reports file operations')

# Parser for file upload documentation in Swagger
upload_parser = lab_reports_ns.parser()
upload_parser.add_argument('patient_id', type=str, required=True, location='form', help='The patient UUID')
upload_parser.add_argument('title', type=str, required=True, location='form', help='Report title/name')
upload_parser.add_argument('notes', type=str, required=False, location='form', help='Optional notes')
upload_parser.add_argument('file', type=FileStorage, location='files', required=True, help='The report file (PDF/Image)')

@lab_reports_ns.route('')
class UploadReport(Resource):
    @lab_reports_ns.doc('upload_lab_report', security='Bearer Auth')
    @lab_reports_ns.expect(upload_parser)
    @role_required(UserRole.USER, UserRole.DOCTOR, UserRole.NURSE)
    def post(self):
        """Upload a new lab report (PDF/Image) for a patient"""
        args = upload_parser.parse_args()
        patient_id = args['patient_id']
        title = args['title']
        notes = args.get('notes', '')
        uploaded_file = args['file']
        
        if not uploaded_file:
            return handle_response(success=False, message="File is required", status_code=400)
            
        return LabReportService.upload_report(patient_id, title, notes, uploaded_file)

@lab_reports_ns.route('/patient/<string:patient_id>')
@lab_reports_ns.param('patient_id', 'The patient UUID')
class PatientReports(Resource):
    @lab_reports_ns.doc('get_patient_lab_reports', security='Bearer Auth')
    @role_required(UserRole.USER, UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN)
    def get(self, patient_id):
        """Retrieve the list of lab reports uploaded for a patient"""
        return LabReportService.get_reports_for_patient(patient_id)

@lab_reports_ns.route('/<string:report_id>/file')
@lab_reports_ns.param('report_id', 'The report entry UUID')
class DownloadReport(Resource):
    @lab_reports_ns.doc('download_lab_report_file', security='Bearer Auth')
    @role_required(UserRole.USER, UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN)
    def get(self, report_id):
        """Download the actual physical file of a lab report"""
        res = LabReportService.get_file(report_id)
        if isinstance(res, tuple) and len(res) == 3:
            # Error returned
            return handle_response(success=False, message=res[1], status_code=res[2])
            
        file_path, file_name, status = res
        return send_file(file_path, as_attachment=True, download_name=file_name)
