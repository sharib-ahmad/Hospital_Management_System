# app/services/doctor.py
from ..extensions import db
from ..models.doctor import Doctor
from ..models.department import Department
from ..models.user import User

class DoctorService:
    @staticmethod
    def get_all_doctors():
        return Doctor.query.all()

    @staticmethod
    def get_doctor_by_code(doctor_code):
        return Doctor.query.filter_by(doctor_code=doctor_code).first()

    @staticmethod
    def update_doctor(doctor_code, data):
        doctor = Doctor.query.filter_by(doctor_code=doctor_code).first()
        if not doctor:
            return None
        
        # Validate department if it's being updated
        if hasattr(data, 'department_id') and data.department_id is not None:
            department = Department.query.get(data.department_id)
            if not department:
                return "DEPARTMENT_NOT_FOUND"

        for key, value in data.dict(exclude_unset=True).items():
            if hasattr(doctor, key) and value is not None:
                setattr(doctor, key, value)
        
        db.session.commit()
        return doctor

    @staticmethod
    def get_doctors_by_department(department_id):
        return Doctor.query.filter_by(department_id=department_id).all()
