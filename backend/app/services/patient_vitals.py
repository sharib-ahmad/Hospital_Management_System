# app/services/patient_vitals.py
from ..extensions import db
from ..models.patient_vitals import PatientVital
from ..models.patient import Patient
from ..models.nurse import Nurse
from ..utils.enum import UserRole
from ..utils.response import handle_response
from flask_jwt_extended import current_user
from .audit import AuditService
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

        db.session.add(vital)
        
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

        # Trigger In-App Notification to assigned doctor
        if patient.assigned_doctor_id:
            from .notification import NotificationService
            NotificationService.create_notification(
                user_id=patient.assigned_doctor_id,
                title="Patient Vitals Recorded",
                message=f"Vitals have been updated/recorded for patient {patient.full_name}.",
                category="vitals"
            )
            
        db.session.commit()

        success_message = "Patient vitals recorded successfully"
        if referral_created and referral_doc_name:
            success_message += f". Referred to Dr. {referral_doc_name}"
        elif refer_to_dept_id and not referral_created:
            success_message += ". Referral requested but no clinician found in department"

        AuditService.log_action(
            user_id=current_user.id,
            action="RECORD_VITALS",
            details={"patient_id": patient_id_str}
        )

        return handle_response(
            success=True,
            data=vital,
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

        vitals = PatientVital.query.filter_by(patient_id=patient_id).order_by(PatientVital.recorded_at.desc()).all()
        if not vitals:
            return handle_response(success=False, message="No vitals recorded for this patient", status_code=404)

        AuditService.log_action(
            user_id=current_user.id,
            action="VIEW_PATIENT_VITALS",
            details={"patient_id": str(patient_id)}
        )

        return handle_response(success=True, data=vitals, message="Patient vitals retrieved successfully")

    @staticmethod
    def generate_vitals_csv_string(user_id):
        """
        Generates a CSV string containing vital records for all patients registered under user_id.
        """
        import csv
        import io
        
        patients = Patient.query.filter_by(user_id=user_id).all()
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write CSV Header
        writer.writerow([
            'Patient Name', 'Relationship', 'Systolic BP (mmHg)', 
            'Diastolic BP (mmHg)', 'Blood Sugar (mg/dL)', 'Pulse Rate (bpm)', 
            'Temperature (F)', 'Respiration Rate (breaths/min)', 
            'Notes', 'Recorded At', 'Nurse Code'
        ])
        
        for p in patients:
            # Sort vitals in chronological order for export
            sorted_vitals = sorted(p.patient_vitals, key=lambda v: v.recorded_at)
            for v in sorted_vitals:
                nurse_code = v.nurse.nurse_code if v.nurse else 'N/A'
                rel_val = p.relation.value if (p.relation and hasattr(p.relation, 'value')) else str(p.relation or 'Self')
                writer.writerow([
                    p.full_name,
                    rel_val,
                    v.systolic_bp,
                    v.diastolic_bp,
                    v.blood_sugar,
                    v.pulse_rate,
                    v.temperature,
                    v.respiration_rate,
                    v.notes or '',
                    v.recorded_at.strftime('%Y-%m-%d %H:%M:%S'),
                    nurse_code
                ])
                
        AuditService.log_action(
            user_id=user_id,
            action="DOWNLOAD_VITALS_CSV"
        )
        return output.getvalue()

