from ..models.patient import Patient
from ..utils.response import handle_response

class PatientService:
    @staticmethod
    def get_all_patients():
        return Patient.query.all()

    @staticmethod
    def get_patient_by_id(patient_id):
        return Patient.query.get(patient_id)
