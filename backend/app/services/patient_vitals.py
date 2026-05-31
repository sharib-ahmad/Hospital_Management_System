# app/services/patient_vitals.py
from ..extensions import db
from ..models.patient_vitals import PatientVital
from ..models.patient import Patient
from ..models.nurse import Nurse
from ..utils.enum import UserRole
from ..utils.response import handle_response
from flask_jwt_extended import current_user
import uuid


class PatientVitalsService:

    @staticmethod
    def record_vitals(data):
        """Nurse records or updates vitals for a patient (upsert via merge)."""
        patient_id_str = data.get('patient_id')
        patient_id = uuid.UUID(patient_id_str)

        # Verify patient exists
        patient = Patient.query.get(patient_id)
        if not patient:
            return handle_response(success=False, message="Patient not found", status_code=404)

        # Resolve nurse profile from current_user (who is a Nurse)
        nurse = Nurse.query.get(current_user.id)
        if not nurse:
            return handle_response(success=False, message="Nurse profile not found", status_code=404)

        vital = PatientVital(
            patient_id=patient_id,
            recorded_by=current_user.id,
            systolic_bp=data.get('systolic_bp'),
            diastolic_bp=data.get('diastolic_bp'),
            blood_sugar=data.get('blood_sugar'),
            pulse_rate=data.get('pulse_rate'),
            temperature=data.get('temperature'),
            respiration_rate=data.get('respiration_rate'),
            notes=data.get('notes'),
        )

        # db.session.merge handles INSERT or UPDATE based on the primary key
        merged_vital = db.session.merge(vital)
        db.session.commit()

        return handle_response(
            success=True,
            data=merged_vital,
            message="Patient vitals recorded successfully",
            status_code=200
        )

    @staticmethod
    def get_vitals_for_patient(patient_id):
        """Returns the vitals record for the given patient."""
        # Verify patient exists
        patient = Patient.query.get(patient_id)
        if not patient:
            return handle_response(success=False, message="Patient not found", status_code=404)

        role = current_user.role

        # Doctors can only view vitals for their own patients
        if role == UserRole.DOCTOR:
            if str(patient.assigned_doctor_id) != str(current_user.id):
                return handle_response(success=False, message="Unauthorized", status_code=403)
        elif role not in (UserRole.ADMIN, UserRole.NURSE):
            return handle_response(success=False, message="Unauthorized", status_code=403)

        vital = PatientVital.query.get(patient_id)
        if not vital:
            return handle_response(success=False, message="No vitals recorded for this patient", status_code=404)

        return handle_response(success=True, data=vital, message="Patient vitals retrieved successfully")
