# app/api_models/appointment_models.py
from flask_restx import fields
from ..utils.enum import AppointmentStatus, EnumField

class AppointmentModels:
    def __init__(self, api):
        self.appointment_create = api.model('AppointmentCreate', {
            'patient_id': fields.String(required=False, description="UUID of the patient"),
            'doctor_id': fields.String(required=False, description="UUID of the doctor (optional for vitals checks)"),
            'appointment_date': fields.DateTime(required=True, description="Date and time of the appointment"),
            'reason': fields.String(description="Reason for the appointment"),
            'appointment_type': fields.String(required=False, description="Type: 'consultation' or 'vitals_check'")
        })

        self.appointment_update = api.model('AppointmentUpdate', {
            'status': EnumField(AppointmentStatus, description="New status of the appointment"),
            'reason': fields.String(description="Updated reason for the appointment"),
            'vitals_checked': fields.Boolean(description="Flag indicating if vitals were captured")
        })

        self.appointment = api.model('Appointment', {
            'id': fields.String,
            'patient_id': fields.String,
            'doctor_id': fields.String,
            'appointment_date': fields.DateTime,
            'status': EnumField(AppointmentStatus),
            'reason': fields.String,
            'vitals_checked': fields.Boolean,
            'appointment_type': fields.String,
            'created_at': fields.DateTime,
            'updated_at': fields.DateTime,
            # Joined data
            'patient_name': fields.String(attribute='patient.full_name'),
            'doctor_name': fields.String,
            'specialization': fields.String(attribute='doctor_specialization'),
            'consultation_fee': fields.Float
        })

        self.response_model = api.model('AppointmentResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.Nested(self.appointment, skip_none=True)
        })

        self.response_list_model = api.model('AppointmentListResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.List(fields.Nested(self.appointment))
        })
