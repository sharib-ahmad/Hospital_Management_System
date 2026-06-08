# app/controllers/medical_records_controller.py
from ..services.medical_records import MedicalRecordsService
from ..utils.request import validate_json


class MedicalRecordsController:

    @staticmethod
    def create_record():
        data, error = validate_json()
        if error:
            return error
        return MedicalRecordsService.create_record(data)

    @staticmethod
    def get_records_for_patient(patient_id):
        return MedicalRecordsService.get_records_for_patient(patient_id)

    @staticmethod
    def get_my_records():
        return MedicalRecordsService.get_my_records()

    @staticmethod
    def get_record_by_id(record_id):
        return MedicalRecordsService.get_record_by_id(record_id)

    @staticmethod
    def parse_prescription(record_id):
        return MedicalRecordsService.parse_prescription(record_id)

    @staticmethod
    def upload_file(file):
        return MedicalRecordsService.upload_file(file)

    @staticmethod
    def get_file(record_id):
        return MedicalRecordsService.get_file(record_id)

