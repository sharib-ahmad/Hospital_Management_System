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
        
        # Link to active appointment if provided
        appt_id_str = data.get('appointment_id')
        referral_created = False
        referral_doc_name = None
        
        if appt_id_str:
            from ..models.appointment import Appointment
            from ..utils.enum import AppointmentStatus
            try:
                appt_id = uuid.UUID(appt_id_str)
                appointment = Appointment.query.get(appt_id)
                if appointment:
                    appointment.vitals_checked = True
                    if appointment.appointment_type == 'vitals_check':
                        appointment.status = AppointmentStatus.COMPLETED
            except ValueError:
                pass

        # Check for automated department referral
        refer_to_dept_id = data.get('refer_to_department_id')
        
        # Referral should only trigger for standalone screening checkups (appointment_type == 'vitals_check')
        # If the patient already had a standard doctor consultation scheduled, referral is not needed.
        is_vitals_check = True
        if appt_id_str:
            from ..models.appointment import Appointment
            try:
                appt_id = uuid.UUID(appt_id_str)
                appointment = Appointment.query.get(appt_id)
                if appointment and appointment.appointment_type != 'vitals_check':
                    is_vitals_check = False
            except ValueError:
                pass

        if refer_to_dept_id and is_vitals_check:
            from ..models.doctor import Doctor
            from ..models.appointment import Appointment
            from ..utils.enum import AppointmentStatus
            from datetime import datetime
            from zoneinfo import ZoneInfo
            
            # Retrieve active doctors in that department
            doctor = Doctor.query.filter_by(department_id=refer_to_dept_id, is_available=True).first()
            if not doctor:
                doctor = Doctor.query.filter_by(department_id=refer_to_dept_id).first()
                
            if doctor:
                kolkata_tz = ZoneInfo("Asia/Kolkata")
                local_now = datetime.now(kolkata_tz).replace(tzinfo=None)
                
                new_appt = Appointment(
                    patient_id=patient_id,
                    doctor_id=doctor.id,
                    appointment_date=local_now,
                    reason="Doctor referral following vitals checkup",
                    status=AppointmentStatus.CONFIRMED,
                    appointment_type='consultation',
                    vitals_checked=True
                )
                db.session.add(new_appt)
                referral_created = True
                if doctor.user:
                    referral_doc_name = doctor.user.full_name

        db.session.commit()

        success_message = "Patient vitals recorded successfully"
        if referral_created and referral_doc_name:
            success_message += f". Referred to Dr. {referral_doc_name}"
        elif refer_to_dept_id and not referral_created:
            success_message += ". Referral requested but no clinician found in department"

        return handle_response(
            success=True,
            data=merged_vital,
            message=success_message,
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
        # Patients/Users can only view their own registered patients
        elif role == UserRole.USER:
            if str(patient.user_id) != str(current_user.id):
                return handle_response(success=False, message="Unauthorized", status_code=403)
        elif role not in (UserRole.ADMIN, UserRole.NURSE):
            return handle_response(success=False, message="Unauthorized", status_code=403)

        vital = PatientVital.query.get(patient_id)
        if not vital:
            return handle_response(success=False, message="No vitals recorded for this patient", status_code=404)

        return handle_response(success=True, data=vital, message="Patient vitals retrieved successfully")
