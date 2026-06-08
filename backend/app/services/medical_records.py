# app/services/medical_records.py
from ..extensions import db
from ..models.medical_record import MedicalRecord
from ..models.patient import Patient
from ..utils.enum import UserRole
from ..utils.response import handle_response
from flask_jwt_extended import current_user
from .audit import AuditService
import uuid
import os

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads", "prescriptions")


class MedicalRecordsService:

    @staticmethod
    def create_record(data):
        """Doctor creates a medical record for an assigned patient."""
        if current_user.role != UserRole.DOCTOR:
            return handle_response(success=False, message="Only doctors can create medical records", status_code=403)

        patient_id = data.get('patient_id')
        appointment_id = data.get('appointment_id')

        # Verify the patient is assigned to this doctor
        patient = Patient.query.filter_by(id=patient_id, assigned_doctor_id=current_user.id).first()
        if not patient:
            return handle_response(
                success=False,
                message="Patient not found or is not assigned to you",
                status_code=403
            )

        record = MedicalRecord(
            patient_id=uuid.UUID(patient_id),
            doctor_id=current_user.id,
            appointment_id=uuid.UUID(appointment_id) if appointment_id else None,
            diagnosis=data.get('diagnosis'),
            treatment=data.get('treatment'),
            prescription=data.get('prescription'),
            notes=data.get('notes'),
            file_name=data.get('file_name'),
            file_path=data.get('file_path'),
        )

        db.session.add(record)
        db.session.commit()

        AuditService.log_action(
            user_id=current_user.id,
            action="CREATE_MEDICAL_RECORD",
            details={"patient_id": patient_id, "appointment_id": appointment_id}
        )

        return handle_response(success=True, data=record, message="Medical record created successfully", status_code=201)

    @staticmethod
    def get_records_for_patient(patient_id):
        """Admin / Doctor / Nurse can view any patient's records."""
        role = current_user.role

        if role == UserRole.USER:
            # Users can only access their own patient sub-profiles
            patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first()
            if not patient:
                return handle_response(success=False, message="Unauthorized", status_code=403)
        elif role == UserRole.DOCTOR:
            # Doctors can only view records for their own patients
            patient = Patient.query.filter_by(id=patient_id, assigned_doctor_id=current_user.id).first()
            if not patient:
                return handle_response(
                    success=False,
                    message="Patient not found or not assigned to you",
                    status_code=403
                )
        elif role not in (UserRole.ADMIN, UserRole.NURSE):
            return handle_response(success=False, message="Unauthorized", status_code=403)

        records = MedicalRecord.query.filter_by(patient_id=patient_id).order_by(MedicalRecord.created_at.desc()).all()
        AuditService.log_action(
            user_id=current_user.id if current_user else None,
            action="VIEW_PATIENT_MEDICAL_RECORDS",
            details={"patient_id": str(patient_id)}
        )
        return handle_response(success=True, data=records, message="Medical records retrieved successfully")

    @staticmethod
    def get_my_records():
        """Returns all medical records for all patient profiles belonging to the current user."""
        patients = Patient.query.filter_by(user_id=current_user.id).all()
        patient_ids = [p.id for p in patients]

        if not patient_ids:
            return handle_response(success=True, data=[], message="No patient profiles found")

        records = (
            MedicalRecord.query
            .filter(MedicalRecord.patient_id.in_(patient_ids))
            .order_by(MedicalRecord.created_at.desc())
            .all()
        )
        AuditService.log_action(
            user_id=current_user.id if current_user else None,
            action="VIEW_OWN_MEDICAL_RECORDS"
        )
        return handle_response(success=True, data=records, message="Your medical records retrieved successfully")

    @staticmethod
    def get_record_by_id(record_id):
        """Get a single medical record with permission checks."""
        record = MedicalRecord.query.get(record_id)
        if not record:
            return handle_response(success=False, message="Medical record not found", status_code=404)

        role = current_user.role

        if role == UserRole.DOCTOR and record.doctor_id != current_user.id:
            return handle_response(success=False, message="Unauthorized", status_code=403)

        if role == UserRole.USER:
            patient = Patient.query.filter_by(id=record.patient_id, user_id=current_user.id).first()
            if not patient:
                return handle_response(success=False, message="Unauthorized", status_code=403)

        if role not in (UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE, UserRole.USER):
            return handle_response(success=False, message="Unauthorized", status_code=403)

        AuditService.log_action(
            user_id=current_user.id if current_user else None,
            action="VIEW_SINGLE_MEDICAL_RECORD",
            details={"record_id": str(record_id)}
        )

        return handle_response(success=True, data=record, message="Medical record retrieved successfully")

    @staticmethod
    def parse_prescription(record_id):
        """
        Parses a medical record's prescription text and matches it against available medicines.
        """
        record = MedicalRecord.query.get(record_id)
        if not record:
            return handle_response(success=False, message="Medical record not found", status_code=404)
            
        # Permission check
        if current_user.role == UserRole.USER:
            patient = Patient.query.filter_by(id=record.patient_id, user_id=current_user.id).first()
            if not patient:
                return handle_response(success=False, message="Unauthorized", status_code=403)
                
        prescription_text = record.prescription or ""
        if not prescription_text:
            return handle_response(success=True, data=[], message="Prescription text is empty")
            
        from ..models.medistore import Medicine
        
        all_medicines = Medicine.query.all()
        matched_medicines = []
        
        # Scan for matching names
        text_lower = prescription_text.lower()
        for med in all_medicines:
            med_name_lower = med.name.lower()
            if med_name_lower in text_lower:
                matched_medicines.append({
                    'id': str(med.id),
                    'name': med.name,
                    'price': float(med.price),
                    'stock': med.stock,
                    'category': med.category,
                    'manufacturer': med.manufacturer
                })
                
        return handle_response(
            success=True,
            data=matched_medicines,
            message=f"Found {len(matched_medicines)} matching medicines from prescription"
        )

    @staticmethod
    def upload_file(file):
        """
        Saves an uploaded file to the secure prescriptions folder.
        """
        # Ensure uploads folder exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Save file with secure unique name
        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"
        dest_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        file.save(dest_path)
        
        return handle_response(
            success=True,
            data={
                'file_name': file.filename,
                'file_path': unique_filename
            },
            message="File uploaded successfully",
            status_code=201
        )

    @staticmethod
    def get_file(record_id_str):
        """
        Retrieves physical file path and name for medical record attachment download.
        """
        try:
            record_id = uuid.UUID(record_id_str)
        except ValueError:
            return None, "Invalid record UUID", 400
            
        record = MedicalRecord.query.get(record_id)
        if not record:
            return None, "Medical record not found", 404
            
        if not record.file_path:
            return None, "No attachment associated with this record", 404
            
        # Check permissions
        role = current_user.role
        if role == UserRole.DOCTOR and record.doctor_id != current_user.id:
            return None, "Unauthorized", 403
            
        if role == UserRole.USER:
            patient = Patient.query.filter_by(id=record.patient_id, user_id=current_user.id).first()
            if not patient:
                return None, "Unauthorized", 403
                
        if role not in (UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE, UserRole.USER):
            return None, "Unauthorized", 403
            
        absolute_file_path = os.path.join(UPLOAD_DIR, record.file_path)
        if not os.path.exists(absolute_file_path):
            return None, "Physical file not found on disk", 404
            
        # Log the access
        AuditService.log_action(
            user_id=current_user.id,
            action="DOWNLOAD_MEDICAL_RECORD_FILE",
            details={"record_id": record_id_str, "file_name": record.file_name}
        )
            
        return absolute_file_path, record.file_name, 200

