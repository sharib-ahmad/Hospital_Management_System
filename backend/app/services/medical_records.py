# app/services/medical_records.py
from ..extensions import db
from ..models.medical_record import MedicalRecord
from ..models.patient import Patient
from ..utils.enum import UserRole
from ..utils.response import handle_response
from flask_jwt_extended import current_user
import uuid


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
        )

        db.session.add(record)
        db.session.commit()

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

        return handle_response(success=True, data=record, message="Medical record retrieved successfully")
