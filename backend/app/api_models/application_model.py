from flask_restx import fields
from ..utils.enum import UserRole, EnumField, ApplicationStatus, Gender, BloodGroup, Relationship

class ApplicationModels:
    def __init__(self, api):
        # --- Shared Error Fragment ---
        self.error_detail = api.model('ErrorDetail', {
            'loc': fields.List(fields.Raw, description="Location of the error"),
            'msg': fields.String(description="Error message"),
            'type': fields.String(description="Error type"),
            'url': fields.String(description="Error help URL")
        })

        # --- Basic Profile Fragment (Output) ---
        self.user_profile_fragment = api.model('UserProfileFragment', {
            'username': fields.String(attribute='user.username'),
            'full_name': fields.String(attribute='user.full_name'),
            'email': fields.String(attribute='user.email'),
            'address': fields.String(attribute='user.address'),
            'phone_number': fields.String(attribute='user.phone_number'),
            'pincode': fields.String(attribute='user.pincode')
        })

        # --- Base Application Fields (Shared by Input & Output) ---
        self.base_application_fields = {
            'reason': fields.String(required=True),
            'date_of_birth': fields.Date(required=True),
            'gender': EnumField(Gender, required=True),
            'blood_group': EnumField(BloodGroup, required=True),
            'emergency_contact_number': fields.String(required=False)
        }

        # --- INPUT MODELS ---
        
        self.patient_create = api.model('PatientApplicationCreate', {
            **self.base_application_fields,
            'medical_history': fields.String,
            'full_name': fields.String,
            'relation': EnumField(Relationship),
            'email': fields.String,
            'phone_number': fields.String,
            'address': fields.String,
            'pincode': fields.String
        })

        self.doctor_create = api.model('DoctorApplicationCreate', {
            **self.base_application_fields,
            'specialization': fields.String(required=True),
            'experience_years': fields.Integer(required=True),
            'consultation_fee': fields.Fixed(decimals=2, required=True),
            'license_number': fields.String(required=True),
            'department_id': fields.String(required=True),
            'shift': fields.String(required=True)
        })

        self.nurse_create = api.model('NurseApplicationCreate', {
            **self.base_application_fields,
            'experience_years': fields.Integer(required=True),
            'license_number': fields.String(required=True),
            'department_id': fields.String(required=True),
            'shift': fields.String(required=True)
        })

        self.pharmacist_create = api.model('PharmacistApplicationCreate', {
            **self.base_application_fields,
            'experience_years': fields.Integer(required=True),
            'license_number': fields.String(required=True),
            'shift': fields.String(required=True)
        })

        # --- OUTPUT MODELS ---

        self.application_base_output = api.model('ApplicationBaseOutput', {
            'id': fields.Integer(readOnly=True),
            'role_applied': EnumField(UserRole),
            'status': EnumField(ApplicationStatus),
            'created_at': fields.DateTime(readOnly=True),
            'updated_at': fields.DateTime(readOnly=True),
            'department_name': fields.String(attribute='department.name'),
            'specialization': fields.String,
            'experience_years': fields.Integer,
            'consultation_fee': fields.Fixed(decimals=2),
            'license_number': fields.String,
            'department_id': fields.String,
            'shift': fields.String,
            'medical_history': fields.String,
            'patient_full_name': fields.String,
            'relation': EnumField(Relationship),
            'patient_email': fields.String,
            'patient_phone_number': fields.String,
            'patient_address': fields.String,
            'patient_pincode': fields.String,
            **self.base_application_fields,
            **self.user_profile_fragment
        })

        self.patient_application_detail = api.inherit('PatientApplicationDetail', self.application_base_output, {})

        self.doctor_application_detail = api.inherit('DoctorApplicationDetail', self.application_base_output, {})

        self.nurse_application_detail = api.inherit('NurseApplicationDetail', self.application_base_output, {})

        self.pharmacist_application_detail = api.inherit('PharmacistApplicationDetail', self.application_base_output, {})

        # --- UNIFIED RESPONSE WRAPPER ---

        def create_unified_response(name, data_model):
            return api.model(name, {
                'success': fields.Boolean,
                'message': fields.String,
                'data': fields.Nested(data_model, skip_none=True),
                'errors': fields.List(fields.Nested(self.error_detail), skip_none=True)
            })

        self.patient_response = create_unified_response('PatientApplicationResponse', self.patient_application_detail)
        self.doctor_response = create_unified_response('DoctorApplicationResponse', self.doctor_application_detail)
        self.nurse_response = create_unified_response('NurseResponse', self.nurse_application_detail)
        self.pharmacist_response = create_unified_response('PharmacistResponse', self.pharmacist_application_detail)

        self.rejection_reason = api.model('RejectionReason', {
            'reason': fields.String(description='Reason for rejecting the application', required=True)
        })

        self.generic_response = api.model('GenericResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.Raw,
            'errors': fields.List(fields.Nested(self.error_detail), skip_none=True)
        })

        self.application_list_response = api.model('ApplicationListResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.List(fields.Nested(self.application_base_output, skip_none=True)),
            'errors': fields.List(fields.Nested(self.error_detail), skip_none=True)
        })
