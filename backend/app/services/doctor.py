# app/services/doctor.py
from ..extensions import db
from ..models.doctor import Doctor
from ..models.department import Department
from ..models.user import User

class DoctorService:
    @staticmethod
    def get_all_departments():
        return Department.query.all()

    @staticmethod
    def create_department(data):
        department = Department(
            name=data.name,
            description=data.get('description', None)
        )
        db.session.add(department)
        db.session.commit()
        return department

    @staticmethod
    def create_doctor(data):
        doctor = Doctor(
            id=data.user_id,
            specialization=data.specialization,
            experience_years=data.get('experience_years', 0),
            consultation_fee=data.consultation_fee,
            department_id=data.department_id
        )
        db.session.add(doctor)
        db.session.commit()
        return doctor

    @staticmethod
    def get_all_doctors():
        return Doctor.query.all()

    @staticmethod
    def get_doctor_by_id(doctor_id):
        return Doctor.query.get(doctor_id)

    @staticmethod
    def update_doctor(doctor_id, data):
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return None
        
        for key, value in data.items():
            if hasattr(doctor, key) and value is not None:
                setattr(doctor, key, value)
        
        db.session.commit()
        return doctor

    @staticmethod
    def get_doctors_by_department(department_id):
        return Doctor.query.filter_by(department_id=department_id).all()
