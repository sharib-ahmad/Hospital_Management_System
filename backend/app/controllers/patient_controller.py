from ..services.patient import PatientService
from ..utils.response import handle_response
from flask_jwt_extended import current_user

class PatientController:
    @staticmethod
    def get_patients():
        patients = PatientService.get_all_patients()
        return handle_response(
            success=True,
            message="Patients retrieved successfully",
            data=patients
        )

    @staticmethod
    def get_my_patients():
        patients = PatientService.get_patients_for_user(current_user.id)
        return handle_response(
            success=True,
            message="Your patients retrieved successfully",
            data=patients
        )

    @staticmethod
    def get_patient(patient_id):
        patient = PatientService.get_patient_by_id(patient_id)
        if not patient:
            return handle_response(success=False, message="Patient not found", status_code=404)
        return handle_response(success=True, data=patient)
