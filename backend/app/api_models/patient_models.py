from flask_restx import fields
from ..utils.enum import Gender, BloodGroup, EnumField, Relationship

class PatientModels:
    def __init__(self, api):
        self.patient_base = api.model('PatientBase', {
            'id': fields.String(description='User ID of the patient'),
            'relation': EnumField(Relationship),
            'date_of_birth': fields.Date,
            'gender': EnumField(Gender),
            'blood_group': EnumField(BloodGroup),
            'medical_history': fields.String,
            'emergency_contact_number': fields.String,
            'assigned_doctor_id': fields.String
        })

        self.patient_detail = api.inherit('PatientDetail', self.patient_base, {
            'full_name': fields.String,
            'email': fields.String,
            'address': fields.String,
            'phone_number': fields.String,
            'pincode': fields.String,
            'guardian_name': fields.String(attribute='user.full_name'),
            'guardian_username': fields.String(attribute='user.username'),
            'created_at': fields.DateTime,
            'updated_at': fields.DateTime
        })

        self.patient_list_response = api.model('PatientListResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.List(fields.Nested(self.patient_detail)),
            'errors': fields.Raw
        })
