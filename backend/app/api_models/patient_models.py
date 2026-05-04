from flask_restx import fields
from ..utils.enum import Gender, BloodGroup, EnumField

class PatientModels:
    def __init__(self, api):
        self.patient_base = api.model('PatientBase', {
            'id': fields.String(description='User ID of the patient'),
            'date_of_birth': fields.Date,
            'gender': EnumField(Gender),
            'blood_group': EnumField(BloodGroup),
            'medical_history': fields.String,
            'emergency_contact_number': fields.String,
            'assigned_doctor_id': fields.String
        })

        self.patient_detail = api.inherit('PatientDetail', self.patient_base, {
            'full_name': fields.String(attribute='user.full_name'),
            'username': fields.String(attribute='user.username'),
            'email': fields.String(attribute='user.email'),
            'role': fields.String(attribute='user.role_value'),
            'address': fields.String(attribute='user.address'),
            'phone_number': fields.String(attribute='user.phone_number'),
            'pincode': fields.String(attribute='user.pincode'),
            'created_at': fields.DateTime,
            'updated_at': fields.DateTime
        })

        self.patient_list_response = api.model('PatientListResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.List(fields.Nested(self.patient_detail)),
            'errors': fields.Raw
        })
