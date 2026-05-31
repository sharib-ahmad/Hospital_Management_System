# app/api_models/patient_vital_models.py
from flask_restx import fields


class PatientVitalModels:
    def __init__(self, api):
        self.vital_create = api.model('PatientVitalCreate', {
            'patient_id': fields.String(required=True, description='UUID of the patient'),
            'systolic_bp': fields.Integer(description='Systolic blood pressure (mmHg)'),
            'diastolic_bp': fields.Integer(description='Diastolic blood pressure (mmHg)'),
            'blood_sugar': fields.Float(description='Blood sugar level (mg/dL)'),
            'pulse_rate': fields.Integer(description='Pulse rate (bpm)'),
            'temperature': fields.Float(description='Body temperature (°C)'),
            'respiration_rate': fields.Integer(description='Respiration rate (breaths/min)'),
            'notes': fields.String(description='Additional observations'),
        })

        self.vital_response_model = api.model('PatientVital', {
            'patient_id': fields.String(readOnly=True),
            'recorded_by': fields.String(readOnly=True, description='Nurse UUID who recorded the vitals'),
            'systolic_bp': fields.Integer,
            'diastolic_bp': fields.Integer,
            'blood_sugar': fields.Float,
            'pulse_rate': fields.Integer,
            'temperature': fields.Float,
            'respiration_rate': fields.Integer,
            'notes': fields.String,
            'recorded_at': fields.DateTime(readOnly=True),
            'updated_at': fields.DateTime(readOnly=True),
            # Joined data
            'patient_name': fields.String(attribute='patient.full_name'),
            'nurse_name': fields.String(attribute='nurse.user.full_name'),
        })

        self.vital_response = api.model('PatientVitalResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.Nested(self.vital_response_model, skip_none=True),
        })

        self.vital_list_response = api.model('PatientVitalListResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.List(fields.Nested(self.vital_response_model)),
        })
