# app/services/nurse.py
from ..extensions import db
from ..models.nurse import Nurse
from ..models.department import Department

class NurseService:
    @staticmethod
    def get_all_nurses():
        return Nurse.query.all()

    @staticmethod
    def get_nurse_by_id(nurse_id):
        return Nurse.query.get(nurse_id)

    @staticmethod
    def get_nurse_by_code(nurse_code):
        return Nurse.query.filter_by(nurse_code=nurse_code).first()

    @staticmethod
    def update_nurse(nurse_code, data):
        nurse = Nurse.query.filter_by(nurse_code=nurse_code).first()
        if not nurse:
            return None
        
        # Validate department if it's being updated
        if hasattr(data, 'department_id') and data.department_id is not None:
            department = Department.query.get(data.department_id)
            if not department:
                return "DEPARTMENT_NOT_FOUND"

        for key, value in data.dict(exclude_unset=True).items():
            if hasattr(nurse, key) and value is not None:
                setattr(nurse, key, value)
        
        db.session.commit()
        return nurse

    @staticmethod
    def get_nurses_by_department(department_id):
        return Nurse.query.filter_by(department_id=department_id).all()
