from ..extensions import db
from ..models.lab_report import LabReport
from ..models.patient import Patient
from ..utils.enum import UserRole
from ..utils.response import handle_response
from flask_jwt_extended import current_user
import uuid
import os

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads", "lab_reports")

class LabReportService:
    @staticmethod
    def upload_report(patient_id_str, title, notes, file):
        """
        Saves uploaded file and records entries in db.
        """
        try:
            patient_id = uuid.UUID(patient_id_str)
        except ValueError:
            return handle_response(success=False, message="Invalid patient UUID", status_code=400)
            
        patient = Patient.query.get(patient_id)
        if not patient:
            return handle_response(success=False, message="Patient not found", status_code=404)
            
        # Permission check: Patients/Users can upload for their subprofiles.
        # Doctor and Nurse can upload for any patient.
        role = current_user.role
        if role == UserRole.USER:
            if str(patient.user_id) != str(current_user.id):
                return handle_response(success=False, message="Unauthorized to upload files for this patient", status_code=403)
                
        # Ensure uploads folder exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Save file with secure unique name
        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"
        dest_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        file.save(dest_path)
        
        report = LabReport(
            patient_id=patient_id,
            uploaded_by=current_user.id,
            file_name=file.filename,
            file_path=unique_filename,
            title=title,
            notes=notes
        )
        db.session.add(report)
        db.session.commit()
        
        # Trigger In-App Notification for patient if doctor/nurse uploads
        if role in (UserRole.DOCTOR, UserRole.NURSE):
            from .notification import NotificationService
            NotificationService.create_notification(
                user_id=patient.user_id,
                title="New Clinical Report Uploaded",
                message=f"Dr./Nurse has uploaded a new lab/clinical report '{title}' for patient {patient.full_name}.",
                category="vitals"
            )
            
        # Trigger Notification for assigned doctor if patient uploads
        if role == UserRole.USER and patient.assigned_doctor_id:
            from .notification import NotificationService
            NotificationService.create_notification(
                user_id=patient.assigned_doctor_id,
                title="Patient Uploaded Lab Report",
                message=f"Patient {patient.full_name} has uploaded a new report '{title}' for review.",
                category="vitals"
            )
            
        return handle_response(
            success=True,
            data={
                'id': str(report.id),
                'title': report.title,
                'file_name': report.file_name,
                'created_at': report.created_at.strftime('%Y-%m-%d %H:%M:%S')
            },
            message="Report uploaded successfully",
            status_code=201
        )

    @staticmethod
    def get_reports_for_patient(patient_id_str):
        """
        Lists all lab reports uploaded for a patient.
        """
        try:
            patient_id = uuid.UUID(patient_id_str)
        except ValueError:
            return handle_response(success=False, message="Invalid patient UUID", status_code=400)
            
        patient = Patient.query.get(patient_id)
        if not patient:
            return handle_response(success=False, message="Patient not found", status_code=404)
            
        # Permission check
        role = current_user.role
        if role == UserRole.USER:
            if str(patient.user_id) != str(current_user.id):
                return handle_response(success=False, message="Unauthorized", status_code=403)
        elif role == UserRole.DOCTOR:
            if patient.assigned_doctor_id != current_user.id:
                return handle_response(success=False, message="Unauthorized", status_code=403)
        elif role not in (UserRole.ADMIN, UserRole.NURSE):
            return handle_response(success=False, message="Unauthorized", status_code=403)
            
        reports = LabReport.query.filter_by(patient_id=patient_id).order_by(LabReport.created_at.desc()).all()
        
        serialized = []
        for r in reports:
            serialized.append({
                'id': str(r.id),
                'title': r.title,
                'file_name': r.file_name,
                'notes': r.notes or '',
                'uploaded_by': r.uploader.full_name if r.uploader else 'Unknown',
                'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        return handle_response(success=True, data=serialized, message="Lab reports retrieved successfully")

    @staticmethod
    def get_file(report_id_str):
        """
        Fetches absolute path of the uploaded file for download.
        """
        try:
            report_id = uuid.UUID(report_id_str)
        except ValueError:
            return None, "Invalid report UUID", 400
            
        report = LabReport.query.get(report_id)
        if not report:
            return None, "Report not found", 404
            
        # Check permissions
        role = current_user.role
        patient = Patient.query.get(report.patient_id)
        
        if role == UserRole.USER:
            if str(patient.user_id) != str(current_user.id):
                return None, "Unauthorized", 403
        elif role == UserRole.DOCTOR:
            if patient.assigned_doctor_id != current_user.id:
                return None, "Unauthorized", 403
        elif role not in (UserRole.ADMIN, UserRole.NURSE):
            return None, "Unauthorized", 403
            
        absolute_file_path = os.path.join(UPLOAD_DIR, report.file_path)
        if not os.path.exists(absolute_file_path):
            return None, "Physical file not found on disk", 404
            
        return absolute_file_path, report.file_name, 200
