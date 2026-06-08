# app/api_models/medical_record_models.py
from flask_restx import fields


class MedicalRecordModels:
    def __init__(self, api):
        self.record_create = api.model('MedicalRecordCreate', {
            'patient_id': fields.String(required=True, description='UUID of the patient'),
            'appointment_id': fields.String(required=False, description='UUID of the linked appointment (optional)'),
            'diagnosis': fields.String(required=True, description='Diagnosis details'),
            'treatment': fields.String(description='Treatment plan'),
            'prescription': fields.String(description='Prescription details'),
            'notes': fields.String(description='Additional notes'),
        })

        self.record_response_model = api.model('MedicalRecord', {
            'id': fields.String(readOnly=True),
            'patient_id': fields.String,
            'doctor_id': fields.String,
            'appointment_id': fields.String,
            'diagnosis': fields.String,
            'treatment': fields.String,
            'prescription': fields.String,
            'notes': fields.String,
            'file_name': fields.String,
            'file_path': fields.String,
            'created_at': fields.DateTime(readOnly=True),
            'updated_at': fields.DateTime(readOnly=True),
            # Joined data
            'patient_name': fields.String(attribute='patient.full_name'),
            'doctor_name': fields.String(attribute='doctor.user.full_name'),
        })

        self.record_response = api.model('MedicalRecordResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.Nested(self.record_response_model, skip_none=True),
        })

        self.record_list_response = api.model('MedicalRecordListResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.List(fields.Nested(self.record_response_model)),
        })
