from ..models.patient import Patient
from ..utils.response import handle_response

class PatientService:
    @staticmethod
    def get_all_patients():
        return Patient.query.all()

    @staticmethod
    def get_patient_by_id(patient_id):
        return Patient.query.get(patient_id)

    @staticmethod
    def get_patients_for_user(user_id):
        return Patient.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_patients_assigned_to_doctor(doctor_id):
        return Patient.query.filter_by(assigned_doctor_id=doctor_id).all()
