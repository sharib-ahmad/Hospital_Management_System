# app/controllers/patient_vitals_controller.py
from ..services.patient_vitals import PatientVitalsService
from ..utils.request import validate_json


class PatientVitalsController:

    @staticmethod
    def record_vitals():
        data, error = validate_json()
        if error:
            return error
        return PatientVitalsService.record_vitals(data)

    @staticmethod
    def get_vitals_for_patient(patient_id):
        return PatientVitalsService.get_vitals_for_patient(patient_id)
