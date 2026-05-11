from ..extensions import db
from ..models.appointment import Appointment
from ..models.doctor import Doctor
from ..models.patient import Patient
from ..utils.enum import UserRole, AppointmentStatus
from ..utils.response import handle_response
from flask_jwt_extended import current_user
from datetime import datetime

class AppointmentService:
    
    @staticmethod
    def get_appointments():
        user_role = current_user.role
        
        if user_role == UserRole.ADMIN:
            appointments = Appointment.query.all()
        elif user_role == UserRole.DOCTOR:
            appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
        elif user_role == UserRole.PATIENT:
            appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
        elif user_role == UserRole.NURSE:
            # Nurses might see all appointments for their department or hospital
            appointments = Appointment.query.all()
        else:
            return handle_response(success=False, message="Unauthorized", status_code=403)
            
        return handle_response(success=True, data=appointments, message="Appointments retrieved successfully")

    @staticmethod
    def create_appointment(validated_data):
        if current_user.role != UserRole.PATIENT:
            return handle_response(success=False, message="Only patients can book appointments", status_code=403)
            
        doctor = Doctor.query.get(validated_data['doctor_id'])
        if not doctor:
            return handle_response(success=False, message="Doctor not found", status_code=404)
            
        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=validated_data['doctor_id'],
            appointment_date=validated_data['appointment_date'],
            reason=validated_data.get('reason'),
            status=AppointmentStatus.PENDING
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
        if current_user.role == UserRole.PATIENT and appointment.patient_id != current_user.id:
            # Patients can maybe only cancel
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
        if current_user.role == UserRole.PATIENT and appointment.patient_id != current_user.id:
            return handle_response(success=False, message="Unauthorized", status_code=403)
            
        return handle_response(success=True, data=appointment, message="Appointment retrieved successfully")
