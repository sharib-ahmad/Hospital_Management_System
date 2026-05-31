from ..extensions import db
from ..models.appointment import Appointment
from ..models.doctor import Doctor
from ..models.patient import Patient
from ..utils.enum import UserRole, AppointmentStatus, Relationship
from ..utils.response import handle_response
from flask_jwt_extended import current_user
from datetime import datetime, timezone

class AppointmentService:
    
    @staticmethod
    def get_appointments():
        user_role = current_user.role
        
        if user_role == UserRole.ADMIN:
            appointments = Appointment.query.all()
        elif user_role == UserRole.DOCTOR:
            appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
        elif user_role == UserRole.USER:
            # Query appointments for all patient sub-profiles belonging to this user
            patients = Patient.query.filter_by(user_id=current_user.id).all()
            patient_ids = [p.id for p in patients]
            if patient_ids:
                appointments = Appointment.query.filter(Appointment.patient_id.in_(patient_ids)).all()
            else:
                appointments = []
        elif user_role == UserRole.NURSE:
            appointments = Appointment.query.all()
        else:
            return handle_response(success=False, message="Unauthorized", status_code=403)
            
        return handle_response(success=True, data=appointments, message="Appointments retrieved successfully")

    @staticmethod
    def create_appointment(validated_data):
        user_role = current_user.role
        patient_id = validated_data.get('patient_id')
        
        if user_role == UserRole.USER:
            # If patient_id is not provided, resolve to a matching subprofile or the first patient subprofile
            if not patient_id:
                patient = Patient.query.filter_by(user_id=current_user.id, relation=Relationship.SELF).first()
                if not patient:
                    patient = Patient.query.filter_by(user_id=current_user.id).first()
                if not patient:
                    return handle_response(success=False, message="No patient profile found. Please register a patient first.", status_code=400)
                patient_id = patient.id
            else:
                # Verify that the patient profile belongs to the current user
                patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first()
                if not patient:
                    return handle_response(success=False, message="Unauthorized access to this patient profile", status_code=403)
            
            status = AppointmentStatus.PENDING

        elif user_role == UserRole.DOCTOR:
            if not patient_id:
                return handle_response(success=False, message="Patient ID is required for doctor-scheduled appointments", status_code=400)
                
            # Verify that the patient is assigned to this doctor
            patient = Patient.query.filter_by(id=patient_id, assigned_doctor_id=current_user.id).first()
            if not patient:
                return handle_response(success=False, message="Patient is not assigned to you", status_code=403)
                
            # Set doctor_id automatically to current doctor's user ID
            validated_data['doctor_id'] = current_user.id
            status = AppointmentStatus.CONFIRMED

        else:
            return handle_response(success=False, message="Only patients or doctors can book appointments", status_code=403)
            
        doctor = Doctor.query.get(validated_data['doctor_id'])
        if not doctor:
            return handle_response(success=False, message="Doctor not found", status_code=404)
            
        # Ensure appointment_date is parsed as a timezone-naive datetime in Asia/Kolkata for storage
        date_val = validated_data['appointment_date']
        if isinstance(date_val, str):
            if date_val.endswith('Z'):
                date_val = date_val.replace('Z', '+00:00')
            try:
                parsed_date = datetime.fromisoformat(date_val)
            except ValueError:
                try:
                    parsed_date = datetime.strptime(date_val, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    parsed_date = datetime.strptime(date_val, "%Y-%m-%dT%H:%M:%S")
        else:
            parsed_date = date_val

        if parsed_date.tzinfo is not None:
            from zoneinfo import ZoneInfo
            kolkata_tz = ZoneInfo("Asia/Kolkata")
            parsed_date = parsed_date.astimezone(kolkata_tz).replace(tzinfo=None)


        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=validated_data['doctor_id'],
            appointment_date=parsed_date,
            reason=validated_data.get('reason', 'Scheduled Consultation'),
            status=status
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return handle_response(success=True, data=appointment, message="Appointment booked successfully", status_code=201)

    @staticmethod
    def update_appointment_status(appointment_id, validated_data):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return handle_response(success=False, message="Appointment not found", status_code=404)
            
        # Permission check
        if current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id:
            return handle_response(success=False, message="Unauthorized to update this appointment", status_code=403)
            
        if current_user.role == UserRole.USER:
            # Verify the patient profile belongs to the current user
            patient = Patient.query.filter_by(id=appointment.patient_id, user_id=current_user.id).first()
            if not patient:
                return handle_response(success=False, message="Unauthorized to update this appointment", status_code=403)
            # Users can only cancel appointments
            if validated_data.get('status') != AppointmentStatus.CANCELLED:
                 return handle_response(success=False, message="Patients can only cancel appointments", status_code=403)

        if 'status' in validated_data:
            appointment.status = validated_data['status']
        if 'reason' in validated_data:
            appointment.reason = validated_data['reason']
            
        db.session.commit()
        return handle_response(success=True, data=appointment, message="Appointment updated successfully")

    @staticmethod
    def get_appointment_by_id(appointment_id):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return handle_response(success=False, message="Appointment not found", status_code=404)
            
        # Permission check
        if current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id:
            return handle_response(success=False, message="Unauthorized", status_code=403)
            
        if current_user.role == UserRole.USER:
            patient = Patient.query.filter_by(id=appointment.patient_id, user_id=current_user.id).first()
            if not patient:
                return handle_response(success=False, message="Unauthorized", status_code=403)
            
        return handle_response(success=True, data=appointment, message="Appointment retrieved successfully")
