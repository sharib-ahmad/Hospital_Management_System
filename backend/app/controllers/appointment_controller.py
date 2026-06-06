from flask import request
from ..services.appointment import AppointmentService
from ..utils.response import handle_response

class AppointmentController:
    
    @staticmethod
    def get_appointments():
        return AppointmentService.get_appointments()

    @staticmethod
    def create_appointment(data):
        return AppointmentService.create_appointment(data)

    @staticmethod
    def get_appointment(appointment_id):
        return AppointmentService.get_appointment_by_id(appointment_id)

    @staticmethod
    def update_appointment(appointment_id, data):
        return AppointmentService.update_appointment_status(appointment_id, data)

    @staticmethod
    def get_available_slots():
        date_str = request.args.get('date')
        appt_type = request.args.get('appointment_type')
        doctor_id = request.args.get('doctor_id')
        return AppointmentService.get_available_slots(date_str, appt_type, doctor_id)
