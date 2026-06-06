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

    @staticmethod
    def export_vitals_direct():
        from flask import Response
        csv_data = PatientVitalsService.generate_vitals_csv_string(current_user.id)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=my_patients_vitals.csv"}
        )

    @staticmethod
    def export_vitals_via_job():
        from ..tasks.email_tasks import send_vitals_csv_email
        send_vitals_csv_email.delay(current_user.id, current_user.email)
        return handle_response(
            success=True,
            message="Vitals export job scheduled. You will receive an email shortly.",
            status_code=202
        )

